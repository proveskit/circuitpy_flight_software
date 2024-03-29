#include "pico/stdlib.h"
#include "hardware/i2c.h"

class VEML7700 {
public:
    VEML7700(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();

    uint16_t readAmbientLight();

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint16_t value);
    uint16_t readRegister(uint8_t reg);
};