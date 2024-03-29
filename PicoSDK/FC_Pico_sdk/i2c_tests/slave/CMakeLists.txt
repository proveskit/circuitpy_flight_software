if (TARGET tinyusb_device)
        add_executable(i2c_slave_test
                slave.c
                )

        # pull in common dependencies and additional i2c hardware support
        target_link_libraries(i2c_slave_test pico_stdlib pico_i2c_slave hardware_i2c)

        # enable usb output, disable uart output
        pico_enable_stdio_usb(i2c_slave_test 1)
        pico_enable_stdio_uart(i2c_slave_test 0)

        # create map/bin/hex file etc.
        pico_add_extra_outputs(i2c_slave_test)
elseif(PICO_ON_DEVICE)
message(WARNING "not building hello_usb because TinyUSB submodule is not initialized in the SDK")
endif()
