#include "phoneos/app.h"

static void gallery_app_render(lv_obj_t *root)
{
    lv_obj_set_layout(root, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(root, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_style_pad_row(root, 8, 0);
    lv_obj_set_style_pad_column(root, 8, 0);

    for (int i = 1; i <= 6; ++i) {
        lv_obj_t *thumb = lv_obj_create(root);
        lv_obj_set_size(thumb, 68, 68);

        lv_obj_t *lbl = lv_label_create(thumb);
        lv_label_set_text_fmt(lbl, "IMG %d", i);
        lv_obj_center(lbl);
    }
}

const phoneos_app_t *gallery_app_descriptor(void)
{
    static const phoneos_app_t app = {
        .id = "gallery",
        .title = "Gallery",
        .render = gallery_app_render,
    };
    return &app;
}