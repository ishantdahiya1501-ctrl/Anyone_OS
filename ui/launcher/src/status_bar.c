#include "status_bar.h"

#include <stdio.h>
#include <time.h>

#include "phoneos/notification.h"

typedef struct {
    lv_obj_t *clock_label;
    lv_obj_t *notif_label;
} status_ctx_t;

static void status_update(status_ctx_t *ctx)
{
    if (!ctx) {
        return;
    }

    time_t now = time(0);
    struct tm *tm_now = localtime(&now);
    if (tm_now) {
        char clock_buf[16];
        (void)snprintf(clock_buf, sizeof(clock_buf), "%02d:%02d", tm_now->tm_hour, tm_now->tm_min);
        lv_label_set_text(ctx->clock_label, clock_buf);
    }

    const char *latest = phoneos_notification_latest();
    if (latest && latest[0] != '\0') {
        lv_label_set_text(ctx->notif_label, latest);
    } else {
        lv_label_set_text(ctx->notif_label, "No notifications");
    }
}

static void status_tick(lv_timer_t *timer)
{
    status_ctx_t *ctx = (status_ctx_t *)timer->user_data;
    status_update(ctx);
}

lv_obj_t *phoneos_status_bar_create(lv_obj_t *parent)
{
    lv_obj_t *bar = lv_obj_create(parent);
    lv_obj_set_size(bar, LV_PCT(100), PHONEOS_STATUS_BAR_HEIGHT);
    lv_obj_align(bar, LV_ALIGN_TOP_MID, 0, 0);
    lv_obj_set_style_radius(bar, 0, 0);
    lv_obj_set_style_border_width(bar, 0, 0);
    lv_obj_set_style_bg_color(bar, lv_color_hex(0x0B0E13), 0);
    lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
    lv_obj_set_style_pad_left(bar, 8, 0);
    lv_obj_set_style_pad_right(bar, 8, 0);

    lv_obj_t *notif = lv_label_create(bar);
    lv_label_set_long_mode(notif, LV_LABEL_LONG_DOT);
    lv_obj_set_width(notif, 190);
    lv_obj_align(notif, LV_ALIGN_LEFT_MID, 0, 0);
    lv_label_set_text(notif, "Boot complete");

    lv_obj_t *clock = lv_label_create(bar);
    lv_obj_align(clock, LV_ALIGN_RIGHT_MID, 0, 0);
    lv_label_set_text(clock, "00:00");

    static status_ctx_t ctx;
    ctx.clock_label = clock;
    ctx.notif_label = notif;

    lv_timer_t *timer = lv_timer_create(status_tick, 1000, &ctx);
    (void)timer;
    status_update(&ctx);

    return bar;
}