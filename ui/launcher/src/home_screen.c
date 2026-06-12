#include "home_screen.h"

#include <string.h>

#include "phoneos/app_registry.h"

typedef struct {
    void (*on_app_selected)(const char *app_id);
    char app_id[32];
} app_btn_ctx_t;

static app_btn_ctx_t g_button_contexts[PHONEOS_MAX_APPS];
static size_t g_button_context_count;

static void on_app_click(lv_event_t *event)
{
    app_btn_ctx_t *ctx = (app_btn_ctx_t *)lv_event_get_user_data(event);
    if (ctx && ctx->on_app_selected) {
        ctx->on_app_selected(ctx->app_id);
    }
}

void phoneos_home_screen_create(lv_obj_t *parent, void (*on_app_selected)(const char *app_id))
{
    g_button_context_count = 0;

    lv_obj_t *grid = lv_obj_create(parent);
    lv_obj_set_size(grid, LV_PCT(100), LV_PCT(100));
    lv_obj_set_style_border_width(grid, 0, 0);
    lv_obj_set_style_radius(grid, 0, 0);
    lv_obj_set_style_bg_opa(grid, LV_OPA_TRANSP, 0);
    lv_obj_set_style_pad_all(grid, 8, 0);
    lv_obj_set_layout(grid, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(grid, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_flex_align(grid, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);
    lv_obj_set_style_pad_row(grid, 10, 0);
    lv_obj_set_style_pad_column(grid, 10, 0);

    size_t count = phoneos_app_count();
    for (size_t i = 0; i < count; ++i) {
        const phoneos_app_t *app = phoneos_get_app(i);
        if (!app) {
            continue;
        }

        lv_obj_t *btn = lv_btn_create(grid);
        lv_obj_set_size(btn, 102, 72);

        if (g_button_context_count >= PHONEOS_MAX_APPS) {
            continue;
        }

        app_btn_ctx_t *ctx = &g_button_contexts[g_button_context_count++];

        ctx->on_app_selected = on_app_selected;
        strncpy(ctx->app_id, app->id, sizeof(ctx->app_id) - 1);
        ctx->app_id[sizeof(ctx->app_id) - 1] = '\0';

        lv_obj_add_event_cb(btn, on_app_click, LV_EVENT_CLICKED, ctx);

        lv_obj_t *lbl = lv_label_create(btn);
        lv_label_set_text(lbl, app->title);
        lv_obj_center(lbl);
    }
}