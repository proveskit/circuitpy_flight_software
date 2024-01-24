if (NOT PICO_NO_HARDWARE)
    add_subdirectory(scan)
    add_subdirectory(slave)
endif ()