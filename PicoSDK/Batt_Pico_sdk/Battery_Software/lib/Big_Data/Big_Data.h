#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include <device_drivers/MCP9808.h>
#include <device_drivers/TCA9548A.h>
#include <device_drivers/VEML7700.h>
#include <device_drivers/DRV2605.h>

class Big_Data {
public:
    Big_Data(i2c_inst_t* i2c_instance, TCA9548A& tca);

    // Methods for interfacing with MCP9808, VEML7700, and DRV2605 on channels 0 through 4
    float getTemperature(uint8_t channel);
    uint16_t getAmbientLight(uint8_t channel);
    void startEffect(uint8_t channel);
    void stopEffect(uint8_t channel);

private:
    TCA9548A& multiplexer;
    MCP9808 mcp_sensors;
    VEML7700 veml_sensors;
    DRV2605 drv_motors;
};