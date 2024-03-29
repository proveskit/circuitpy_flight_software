#ifndef MCP25625_DRIVER_H
#define MCP25625_DRIVER_H

#include "pico/stdlib.h"
#include "hardware/spi.h"

class MCP25625Driver {
public:
    MCP25625Driver(spi_inst_t *spi, uint cs_pin);

    void configure();

    void sendMessage(uint32_t id, uint8_t data_len, const uint8_t *data);

    bool receiveMessage(uint32_t &id, uint8_t &data_len, uint8_t *data);

    bool isTXBufferFull();

    void sendDataPackets(uint32_t id, const uint8_t *data, size_t data_len);

private:
    spi_inst_t *spi;
    uint cs_pin;

    void select();

    void deselect();

    void writeRegister(uint8_t reg, uint8_t value);

    uint8_t readRegister(uint8_t reg);

    void modifyRegister(uint8_t reg, uint8_t mask, uint8_t data);

    bool readTXStatus(uint8_t buffer_num);

    void handleError(const char *message);
};

#endif // MCP25625_DRIVER_H