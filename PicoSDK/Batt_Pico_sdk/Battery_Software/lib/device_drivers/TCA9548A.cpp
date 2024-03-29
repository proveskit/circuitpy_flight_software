#include "TCA9548A.h"

TCA9548A::TCA9548A(i2c_inst_t* i2c_instance, uint8_t i2c_address) {
    tca_i2c = i2c_instance;
    tca_address = i2c_address;

    // Initialize I2C instances for each channel
    for (int channel = 0; channel < 8; ++channel) {
        channel_i2c[channel] = *i2c_instance;  // Copy the I2C configuration
    }
}

void TCA9548A::configure() {
    // Default configuration, all channels disabled
    writeRegister(0x01, 0x00);
}

void TCA9548A::enableChannel(uint8_t channel) {
    if (channel >= 8) {
        // Invalid channel, do nothing
        return;
    }

    // Enable the specified channel
    uint8_t channelMask = 1 << channel;
    writeRegister(0x01, channelMask);
}

void TCA9548A::disableAllChannels() {
    // Disable all channels
    writeRegister(0x01, 0x00);
}

void TCA9548A::scanChannels() {
    for (uint8_t channel = 0; channel < 8; ++channel) {
        enableChannel(channel);
        sleep_ms(1);

        printf("Scanning devices on channel %d:\n", channel);

        for (uint8_t address = 0x08; address < 0x78; ++address) {
            uint8_t data[1] = {0x00};
            if (i2c_write_blocking(&channel_i2c[channel], address, data, 1, true) == PICO_ERROR_GENERIC) {
                // No acknowledge, no device at this address
                continue;
            }

            printf("Device found at address 0x%02X on channel %d\n", address, channel);
        }

        disableAllChannels();
        sleep_ms(1);
    }
}

i2c_inst_t* TCA9548A::getChannelI2C(uint8_t channel) {
    if (channel < 8) {
        return &channel_i2c[channel];
    } else {
        return nullptr;  // Invalid channel
    }
}

void TCA9548A::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t data[2] = {reg, value};
    i2c_write_blocking(tca_i2c, tca_address, data, 2, false);
}