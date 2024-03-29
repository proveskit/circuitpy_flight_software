#include "pico/stdlib.h"
#include "hardware/i2c.h"

class PCA9685 {
public:
    PCA9685(i2c_inst_t* i2c_instance, uint8_t address);

    void configure();
    void toggleOutputs(bool state); // true for ON, false for OFF
    void setDutyCycle(uint8_t port, uint16_t duty_cycle); // port: 0-15, duty_cycle: 0-4095
    void setPortState(uint8_t port, bool state); // true for ON, false for OFF

private:
    i2c_inst_t* i2c;
    uint8_t address;

    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);
};