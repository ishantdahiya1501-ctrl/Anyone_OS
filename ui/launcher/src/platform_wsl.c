#include "platform.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <SDL.h>
#include <lvgl.h>

enum {
    PHONEOS_WSL_WIDTH = 800,
    PHONEOS_WSL_HEIGHT = 480,
};

static SDL_Window *g_window;
static SDL_Renderer *g_renderer;
static SDL_Texture *g_texture;
static bool g_running = true;
static bool g_pointer_pressed;
static lv_point_t g_pointer_point;

static void sdl_flush(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    (void)drv;

    SDL_Rect rect;
    rect.x = area->x1;
    rect.y = area->y1;
    rect.w = area->x2 - area->x1 + 1;
    rect.h = area->y2 - area->y1 + 1;

    void *pixels = NULL;
    int pitch = 0;
    if (SDL_LockTexture(g_texture, &rect, &pixels, &pitch) == 0) {
        for (int y = 0; y < rect.h; ++y) {
            uint32_t *dst_row = (uint32_t *)((uint8_t *)pixels + (size_t)y * (size_t)pitch);
            for (int x = 0; x < rect.w; ++x) {
                dst_row[x] = lv_color_to32(color_p[y * rect.w + x]);
            }
        }

        SDL_UnlockTexture(g_texture);
        SDL_RenderClear(g_renderer);
        SDL_RenderCopy(g_renderer, g_texture, NULL, NULL);
        SDL_RenderPresent(g_renderer);
    }

    lv_disp_flush_ready(drv);
}

static void sdl_read(lv_indev_drv_t *drv, lv_indev_data_t *data)
{
    (void)drv;
    data->state = g_pointer_pressed ? LV_INDEV_STATE_PR : LV_INDEV_STATE_REL;
    data->point = g_pointer_point;
}

bool phoneos_platform_init(void)
{
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0) {
        return false;
    }

    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "nearest");
    SDL_SetHint(SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS, "0");

    g_window = SDL_CreateWindow(
        "PhoneOS",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        PHONEOS_WSL_WIDTH,
        PHONEOS_WSL_HEIGHT,
        SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);
    if (!g_window) {
        return false;
    }

    g_renderer = SDL_CreateRenderer(g_window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!g_renderer) {
        g_renderer = SDL_CreateRenderer(g_window, -1, SDL_RENDERER_SOFTWARE);
        if (!g_renderer) {
            return false;
        }
    }

    g_texture = SDL_CreateTexture(
        g_renderer,
        SDL_PIXELFORMAT_ARGB8888,
        SDL_TEXTUREACCESS_STREAMING,
        PHONEOS_WSL_WIDTH,
        PHONEOS_WSL_HEIGHT);
    if (!g_texture) {
        return false;
    }

    static lv_color_t buf1[PHONEOS_WSL_WIDTH * 40];
    static lv_color_t buf2[PHONEOS_WSL_WIDTH * 40];
    static lv_disp_draw_buf_t draw_buf;
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, PHONEOS_WSL_WIDTH * 40);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = PHONEOS_WSL_WIDTH;
    disp_drv.ver_res = PHONEOS_WSL_HEIGHT;
    disp_drv.flush_cb = sdl_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = sdl_read;
    lv_indev_drv_register(&indev_drv);

    g_pointer_pressed = false;
    g_pointer_point.x = 0;
    g_pointer_point.y = 0;
    g_running = true;
    return true;
}

void phoneos_platform_poll(void)
{
    SDL_Event event;
    while (SDL_PollEvent(&event) == 1) {
        switch (event.type) {
        case SDL_QUIT:
            g_running = false;
            break;
        case SDL_KEYDOWN:
            if (event.key.keysym.sym == SDLK_ESCAPE) {
                g_running = false;
            }
            break;
        case SDL_MOUSEMOTION:
            g_pointer_point.x = (lv_coord_t)event.motion.x;
            g_pointer_point.y = (lv_coord_t)event.motion.y;
            break;
        case SDL_MOUSEBUTTONDOWN:
            if (event.button.button == SDL_BUTTON_LEFT) {
                g_pointer_pressed = true;
                g_pointer_point.x = (lv_coord_t)event.button.x;
                g_pointer_point.y = (lv_coord_t)event.button.y;
            }
            break;
        case SDL_MOUSEBUTTONUP:
            if (event.button.button == SDL_BUTTON_LEFT) {
                g_pointer_pressed = false;
                g_pointer_point.x = (lv_coord_t)event.button.x;
                g_pointer_point.y = (lv_coord_t)event.button.y;
            }
            break;
        default:
            break;
        }
    }
}

bool phoneos_platform_running(void)
{
    return g_running;
}

void phoneos_platform_sleep(uint32_t milliseconds)
{
    SDL_Delay(milliseconds);
}

void phoneos_platform_shutdown(void)
{
    if (g_texture) {
        SDL_DestroyTexture(g_texture);
        g_texture = NULL;
    }

    if (g_renderer) {
        SDL_DestroyRenderer(g_renderer);
        g_renderer = NULL;
    }

    if (g_window) {
        SDL_DestroyWindow(g_window);
        g_window = NULL;
    }

    SDL_Quit();
}