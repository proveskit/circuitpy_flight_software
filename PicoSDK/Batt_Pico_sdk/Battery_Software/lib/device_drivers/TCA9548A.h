#ifndef _TCA9548A_H
#define _TCA9548A_H
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

class TCA9548A{
public:
    TCA9548A(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();
    void enableChannel(uint8_t channel);
    void disableAllChannels();
    void scanChannels();

    i2c_inst_t* getChannelI2C(uint8_t channel);

private:
    i2c_inst_t* tca_i2c;
    uint8_t tca_address;

    i2c_inst_t channel_i2c[8];

    void writeRegister(uint8_t reg, uint8_t value);
};
#endif