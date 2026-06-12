#include "phoneos/app.h"

static void camera_app_render(lv_obj_t *root)
{
    lv_obj_t *title = lv_label_create(root);
    lv_obj_align(title, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_label_set_text(title, "Camera");

    lv_obj_t *preview = lv_obj_create(root);
    lv_obj_set_size(preview, 190, 150);
    lv_obj_align(preview, LV_ALIGN_CENTER, 0, -6);

    lv_obj_t *preview_label = lv_label_create(preview);
    lv_label_set_text(preview_label, "Preview pipeline\nready");
    lv_obj_center(preview_label);
}

const phoneos_app_t *camera_app_descriptor(void)
{
    static const phoneos_app_t app = {
        .id = "camera",
        .title = "Camera",
        .render = camera_app_render,
    };
    return &app;
}