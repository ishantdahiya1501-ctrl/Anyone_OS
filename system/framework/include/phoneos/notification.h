#ifndef PHONEOS_NOTIFICATION_H
#define PHONEOS_NOTIFICATION_H

#include <stddef.h>

#define PHONEOS_MAX_NOTIFICATIONS 32
#define PHONEOS_NOTIFICATION_TEXT_MAX 96

int phoneos_notification_push(const char *text);
const char *phoneos_notification_latest(void);
size_t phoneos_notification_count(void);
void phoneos_notification_clear(void);

#endif