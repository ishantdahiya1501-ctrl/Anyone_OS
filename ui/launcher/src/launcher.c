#include "launcher.h"
#include "home_screen.h"
#include "status_bar.h"

#include <string.h>

#include "phoneos/app_registry.h"

static lv_obj_t *g_root;
static lv_obj_t *g_content;

static const phoneos_app_t *find_app_by_id(const char *id)
{
    size_t count = phoneos_app_count();
    for (size_t i = 0; i < count; ++i) {
        const phoneos_app_t *app = phoneos_get_app(i);
        if (app && strcmp(app->id, id) == 0) {
            return app;
        }
    }
    return 0;
}

static void on_home_click(lv_event_t *event)
{
    (void)event;
    phoneos_launcher_show_home();
}

static void on_app_selected(const char *app_id)
{
    const phoneos_app_t *app = find_app_by_id(app_id);
    if (app) {
        phoneos_launcher_open_app(app);
    }
}

void phoneos_launcher_init(lv_obj_t *root)
{
    g_root = root;

    lv_obj_set_style_bg_color(g_root, lv_color_hex(0x10131A), 0);
    lv_obj_set_style_bg_opa(g_root, LV_OPA_COVER, 0);

    (void)phoneos_status_bar_create(g_root);

    g_content = lv_obj_create(g_root);
    lv_obj_set_size(g_content, LV_PCT(100), LV_PCT(100));
    lv_obj_set_style_radius(g_content, 0, 0);
    lv_obj_set_style_border_width(g_content, 0, 0);
    lv_obj_set_style_pad_all(g_content, 10, 0);
    lv_obj_set_style_bg_color(g_content, lv_color_hex(0x10131A), 0);
    lv_obj_set_style_bg_opa(g_content, LV_OPA_COVER, 0);
    lv_obj_set_pos(g_content, 0, PHONEOS_STATUS_BAR_HEIGHT);
    lv_obj_set_height(g_content, lv_obj_get_height(g_root) - PHONEOS_STATUS_BAR_HEIGHT);

    phoneos_launcher_show_home();
}

void phoneos_launcher_show_home(void)
{
    lv_obj_clean(g_content);
    phoneos_home_screen_create(g_content, on_app_selected);
}

void phoneos_launcher_open_app(const phoneos_app_t *app)
{
    if (!app) {
        return;
    }

    lv_obj_clean(g_content);

    lv_obj_t *header = lv_obj_create(g_content);
    lv_obj_set_size(header, LV_PCT(100), 36);
    lv_obj_set_style_radius(header, 6, 0);
    lv_obj_set_style_border_width(header, 0, 0);
    lv_obj_set_style_pad_left(header, 8, 0);
    lv_obj_set_style_pad_right(header, 8, 0);
    lv_obj_set_style_bg_color(header, lv_color_hex(0x1A1F2A), 0);
    lv_obj_set_style_bg_opa(header, LV_OPA_COVER, 0);

    lv_obj_t *title = lv_label_create(header);
    lv_label_set_text(title, app->title);
    lv_obj_align(title, LV_ALIGN_LEFT_MID, 0, 0);

    lv_obj_t *home_btn = lv_btn_create(header);
    lv_obj_set_size(home_btn, 58, 24);
    lv_obj_align(home_btn, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_add_event_cb(home_btn, on_home_click, LV_EVENT_CLICKED, 0);

    lv_obj_t *home_lbl = lv_label_create(home_btn);
    lv_label_set_text(home_lbl, "Home");
    lv_obj_center(home_lbl);

    lv_obj_t *app_root = lv_obj_create(g_content);
    lv_obj_set_size(app_root, LV_PCT(100), LV_PCT(100));
    lv_obj_set_y(app_root, 40);
    lv_obj_set_style_radius(app_root, 0, 0);
    lv_obj_set_style_border_width(app_root, 0, 0);
    lv_obj_set_style_bg_color(app_root, lv_color_hex(0x10131A), 0);
    lv_obj_set_style_bg_opa(app_root, LV_OPA_TRANSP, 0);
    lv_obj_set_style_pad_all(app_root, 0, 0);

    app->render(app_root);
}