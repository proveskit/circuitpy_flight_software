if (TARGET tinyusb_device)
    add_executable(boot boot.cpp)

    pico_generate_pio_header(boot ${CMAKE_CURRENT_LIST_DIR}/blink.pio)
    pico_generate_pio_header(boot ${CMAKE_CURRENT_LIST_DIR}/neopixel.pio)

    target_sources(boot PRIVATE boot.cpp)

    # pull in common dependencies and additional pwm hardware support
    target_link_libraries(boot PRIVATE pico_stdlib hardware_pio hardware_gpio hardware_i2c main neopixel)

    # enable usb output, disable uart output
    pico_enable_stdio_usb(boot 1)
    pico_enable_stdio_uart(boot 0)

    # create map/bin/hex file etc.
    pico_add_extra_outputs(boot)

    # add url via pico_set_program_url
    example_auto_set_url(boot)
elseif(PICO_ON_DEVICE)
    message(WARNING "not building hello_usb because TinyUSB submodule is not initialized in the SDK")
endif()
