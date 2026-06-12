#include "phoneos/app.h"

static void phone_app_render(lv_obj_t *root)
{
    lv_obj_set_layout(root, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(root, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(root, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);

    lv_obj_t *title = lv_label_create(root);
    lv_label_set_text(title, "Dialer");

    lv_obj_t *hint = lv_label_create(root);
    lv_label_set_text(hint, "Phase 1: call pipeline stub ready.");

    lv_obj_t *last = lv_label_create(root);
    lv_label_set_text(last, "Last call: +1 555 0100");
}

const phoneos_app_t *phone_app_descriptor(void)
{
    static const phoneos_app_t app = {
        .id = "phone",
        .title = "Phone",
        .render = phone_app_render,
    };
    return &app;
}