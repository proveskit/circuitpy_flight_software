#include "pico/stdlib.h"
#include "hardware/i2c.h"

class PCT2075 {
public:
    PCT2075(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();

    float readTemperature();

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint8_t value);
    uint16_t readRegister(uint8_t reg);
};