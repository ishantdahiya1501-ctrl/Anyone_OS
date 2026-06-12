#include "phoneos/app.h"

static void sms_app_render(lv_obj_t *root)
{
    lv_obj_set_layout(root, LV_LAYOUT_FLEX);
    lv_obj_set_flex_flow(root, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(root, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);

    lv_obj_t *title = lv_label_create(root);
    lv_label_set_text(title, "Messages");

    lv_obj_t *msg1 = lv_label_create(root);
    lv_label_set_text(msg1, "Ops: Device online.");

    lv_obj_t *msg2 = lv_label_create(root);
    lv_label_set_text(msg2, "Scheduler: Build queued.");
}

const phoneos_app_t *sms_app_descriptor(void)
{
    static const phoneos_app_t app = {
        .id = "sms",
        .title = "SMS",
        .render = sms_app_render,
    };
    return &app;
}