#ifndef PHONEOS_APP_H
#define PHONEOS_APP_H

#include <lvgl.h>

typedef struct {
    const char *id;
    const char *title;
    void (*render)(lv_obj_t *root);
} phoneos_app_t;

#endif