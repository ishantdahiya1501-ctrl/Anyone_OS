#include "phoneos/notification.h"

#include <string.h>

static char g_notifications[PHONEOS_MAX_NOTIFICATIONS][PHONEOS_NOTIFICATION_TEXT_MAX];
static size_t g_head = 0;
static size_t g_count = 0;

int phoneos_notification_push(const char *text)
{
    if (!text) {
        return -1;
    }

    strncpy(g_notifications[g_head], text, PHONEOS_NOTIFICATION_TEXT_MAX - 1);
    g_notifications[g_head][PHONEOS_NOTIFICATION_TEXT_MAX - 1] = '\0';

    g_head = (g_head + 1) % PHONEOS_MAX_NOTIFICATIONS;
    if (g_count < PHONEOS_MAX_NOTIFICATIONS) {
        g_count++;
    }

    return 0;
}

const char *phoneos_notification_latest(void)
{
    if (g_count == 0) {
        return "";
    }

    size_t latest = (g_head + PHONEOS_MAX_NOTIFICATIONS - 1) % PHONEOS_MAX_NOTIFICATIONS;
    return g_notifications[latest];
}

size_t phoneos_notification_count(void)
{
    return g_count;
}

void phoneos_notification_clear(void)
{
    g_head = 0;
    g_count = 0;
    memset(g_notifications, 0, sizeof(g_notifications));
}