#ifndef _PYSQUARED_H
#define _PYSQUARED_H

#include <stdio.h>
#include <neopixel/neopixel.h>
#include <tools/tools.h>
#include <device_drivers/INA219.h>
#include <device_drivers/PCT2075.h>
#include <device_drivers/PCA9685.h>
#include <device_drivers/TCA9548A.h>
#include <device_drivers/ADS1015.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/pio.h"

class pysquared{
public:
    INA219 battery_power;
    INA219 solar_power;
    PCT2075 internal_temp;
    PCA9685 led_driver;
    TCA9548A i2c_mux;
    ADS1015 adc;

    uint8_t relay_pin;
    uint8_t vbus_reset_pin;
    uint8_t i2c_reset_pin;
    uint8_t rf_enable_pin;
    uint8_t d0_pin;
    uint8_t i2c_sda1_pin;
    uint8_t i2c_scl1_pin;
    uint8_t i2c_sda0_pin;
    uint8_t i2c_scl0_pin;
    uint8_t pwr_mode;
    float error_count;

    pysquared(neopixel neo);

    void check_reboot();
    void all_faces_on();
    void all_faces_off();
    void heater_on();
    void heater_off();
    void exception_handler();
    void can_send(uint16_t id, char * message);
    void can_handler();

    uint8_t get_power_mode();
    float get_thermocouple_temp();
    float get_internal_temp();
    float get_battery_voltage();
    float get_draw_current();
    float get_charge_voltage();
    float get_charge_current();
private:
    tools t;
};
#endif