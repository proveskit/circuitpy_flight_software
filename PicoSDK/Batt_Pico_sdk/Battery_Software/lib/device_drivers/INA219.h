#include "pico/stdlib.h"
#include "hardware/i2c.h"

class INA219 {
public:
    INA219(i2c_inst_t* i2c_instance, uint8_t i2c_address);

    void configure();
    float readShuntVoltage();
    float readBusVoltage();
    float readCurrent();

private:
    i2c_inst_t* i2c;
    uint8_t address;

    
    void calibrate(float max_current_amps, float max_voltage);
    void writeRegister(uint8_t reg, uint16_t value);
    uint16_t readRegister(uint8_t reg);
};