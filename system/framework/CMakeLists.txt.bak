add_library(phoneos_framework STATIC
    src/app_registry.c
)

target_include_directories(phoneos_framework
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(phoneos_framework
    PUBLIC
        ${PHONEOS_LVGL_TARGET}
)