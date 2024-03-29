#include "pico/stdlib.h"
#include "hardware/i2c.h"

class ADS1015 {
public:
    ADS1015(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();

    int16_t readSingleEnded(uint8_t channel);

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint16_t value);
    uint16_t readRegister(uint8_t reg);
};