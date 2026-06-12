#include "phoneos/app_registry.h"

static const phoneos_app_t *g_apps[PHONEOS_MAX_APPS];
static size_t g_app_count = 0;

int phoneos_register_app(const phoneos_app_t *app)
{
    if (!app || !app->id || !app->title || !app->render) {
        return -1;
    }

    if (g_app_count >= PHONEOS_MAX_APPS) {
        return -1;
    }

    g_apps[g_app_count++] = app;
    return 0;
}

size_t phoneos_app_count(void)
{
    return g_app_count;
}

const phoneos_app_t *phoneos_get_app(size_t index)
{
    if (index >= g_app_count) {
        return 0;
    }
    return g_apps[index];
}

void phoneos_clear_apps(void)
{
    g_app_count = 0;
}