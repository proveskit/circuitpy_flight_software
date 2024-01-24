#include "Big_Data.h"

Big_Data::Big_Data(i2c_inst_t* i2c_instance, TCA9548A& tca) : multiplexer(tca),
mcp_sensors(i2c_instance, 0x1B), veml_sensors(i2c_instance, 0x10), drv_motors(i2c_instance, 0x5A)
{
    printf("All Faces Initialized!\n");
}

float Big_Data::getTemperature(uint8_t channel) {
    if (channel < 5) {
        multiplexer.enableChannel(channel);
        float temperature = mcp_sensors.readTemperature();
        multiplexer.disableAllChannels();
        return temperature;
    } else {
        // Invalid channel, return an error value
        return -1.0f;
    }
}

uint16_t Big_Data::getAmbientLight(uint8_t channel) {
    if (channel < 5) {
        multiplexer.enableChannel(channel);
        uint16_t ambientLight = veml_sensors.readAmbientLight();
        multiplexer.disableAllChannels();
        return ambientLight;
    } else {
        // Invalid channel, return an error value
        return 0;
    }
}

void Big_Data::startEffect(uint8_t channel) {
    if (channel < 5) {
        multiplexer.enableChannel(channel);
        drv_motors.start();
        multiplexer.disableAllChannels();
    }
}

void Big_Data::stopEffect(uint8_t channel) {
    if (channel < 5) {
        multiplexer.enableChannel(channel);
        drv_motors.stop();
        multiplexer.disableAllChannels();
    }
}