#include "platform.h"

#include <unistd.h>

#include <lvgl.h>
#include <lv_drivers/display/fbdev.h>
#include <lv_drivers/indev/evdev.h>

static bool g_running = true;

bool phoneos_platform_init(void)
{
    fbdev_init();
    evdev_init();

    static lv_color_t buf1[800 * 40];
    static lv_color_t buf2[800 * 40];
    static lv_disp_draw_buf_t draw_buf;
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, 800 * 40);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.flush_cb = fbdev_flush;
    disp_drv.draw_buf = &draw_buf;
    disp_drv.hor_res = 800;
    disp_drv.ver_res = 480;
    lv_disp_drv_register(&disp_drv);

    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = evdev_read;
    lv_indev_drv_register(&indev_drv);

    g_running = true;
    return true;
}

void phoneos_platform_poll(void)
{
}

bool phoneos_platform_running(void)
{
    return g_running;
}

void phoneos_platform_sleep(uint32_t milliseconds)
{
    usleep(milliseconds * 1000U);
}

void phoneos_platform_shutdown(void)
{
}