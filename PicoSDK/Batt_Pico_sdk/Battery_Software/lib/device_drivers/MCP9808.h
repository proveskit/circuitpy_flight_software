#include "pico/stdlib.h"
#include "hardware/i2c.h"

class MCP9808 {
public:
    MCP9808(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();

    float readTemperature();

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint16_t value);
    uint16_t readRegister(uint8_t reg);
};