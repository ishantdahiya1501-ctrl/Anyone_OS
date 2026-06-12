#include "phoneos/app.h"

static void settings_app_render(lv_obj_t *root)
{
    lv_obj_set_layout(root, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(root, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_style_pad_row(root, 8, 0);

    lv_obj_t *title = lv_label_create(root);
    lv_label_set_text(title, "Settings");

    lv_obj_t *wifi = lv_label_create(root);
    lv_label_set_text(wifi, "Wi-Fi: enabled");

    lv_obj_t *brightness = lv_label_create(root);
    lv_label_set_text(brightness, "Brightness: 70%");

    lv_obj_t *memory = lv_label_create(root);
    lv_label_set_text(memory, "Memory target: < 150 MB idle");
}

const phoneos_app_t *settings_app_descriptor(void)
{
    static const phoneos_app_t app = {
        .id = "settings",
        .title = "Settings",
        .render = settings_app_render,
    };
    return &app;
}