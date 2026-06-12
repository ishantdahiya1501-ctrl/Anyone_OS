#ifndef PHONEOS_PLATFORM_H
#define PHONEOS_PLATFORM_H

#include <stdbool.h>
#include <stdint.h>

bool phoneos_platform_init(void);
void phoneos_platform_poll(void);
bool phoneos_platform_running(void);
void phoneos_platform_sleep(uint32_t milliseconds);
void phoneos_platform_shutdown(void);

#endif