#ifndef _PYSQUARED_H
#define _PYSQUARED_H

#include <stdio.h>
#include <neopixel/neopixel.h>
#include <tools/tools.h>
#include <device_drivers/LSM303AGR.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"

class pysquared{
public:
    LSM303AGR_ACCEL accel;
    LSM303AGR_MAG mag;
    uint relay_pin;
    uint vbus_reset_pin;
    uint i2c_reset_pin;
    uint rf_enable_pin;
    uint rf_reset_pin;
    uint rf_dio0_pin;
    uint rf_dio4_pin;
    uint d0_pin;
    uint i2c_sda1_pin;
    uint i2c_scl1_pin;
    uint8_t pwr_mode;
    pysquared(neopixel neo);
    void check_reboot();
    uint8_t get_power_mode() const {return pwr_mode;}
private:
    tools t;
};
#endif