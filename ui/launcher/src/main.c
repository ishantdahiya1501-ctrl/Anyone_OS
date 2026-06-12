#include <lvgl.h>

#include <signal.h>
#include <stdlib.h>

#include "launcher.h"
#include "phoneos/app_manager.h"
#include "phoneos/notification.h"
#include "platform.h"

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig)
{
    (void)sig;
    g_running = 0;
}

int main(void)
{
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    lv_init();

    if (!phoneos_platform_init()) {
        return EXIT_FAILURE;
    }

    phoneos_app_manager_init();
    (void)phoneos_notification_push("System online");

    phoneos_launcher_init(lv_scr_act());

    while (g_running && phoneos_platform_running()) {
        phoneos_platform_poll();
        lv_timer_handler();
        phoneos_platform_sleep(5);
    }

    phoneos_platform_shutdown();

    return EXIT_SUCCESS;
}