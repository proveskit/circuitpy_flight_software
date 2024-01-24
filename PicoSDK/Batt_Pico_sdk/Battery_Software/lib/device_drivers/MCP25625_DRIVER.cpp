#include "MCP25625_DRIVER.h"
#include "MCP25625.h"

MCP25625Driver::MCP25625Driver(spi_inst_t *spi, uint cs_pin) : spi(spi), cs_pin(cs_pin) {}

void MCP25625Driver::configure() {
    // Perform MCP25625 configuration here

    // For example, set the mode to normal and set the baud rate
    // This should be adjusted based on your specific requirements
    writeRegister(MCP25625_CANCTRL, 0x00);  // Set to normal mode
    writeRegister(MCP25625_CNF1, 0x01);     // Configure the baud rate
    writeRegister(MCP25625_CNF2, 0x90);
    writeRegister(MCP25625_CNF3, 0x82);
}

void MCP25625Driver::sendMessage(uint32_t id, uint8_t data_len, const uint8_t *data) {
    // Check if any TX buffer is available
    if (!isTXBufferFull()) {
        // Construct and send a CAN message
        uint8_t buffer[MCP25625_MAX_MESSAGE_LENGTH + 5];  // Buffer for the message

        buffer[0] = MCP25625_TXB0SIDH;  // Start at the SIDH register

        // Set the ID
        buffer[1] = (uint8_t)(id >> 3);
        buffer[2] = (uint8_t)(id << 5);

        // Set the data length and data
        buffer[3] = data_len & 0x0F;
        for (uint8_t i = 0; i < data_len; i++) {
            buffer[4 + i] = data[i];
        }

        // Set the control byte to initiate the transmission
        buffer[4 + data_len] = MCP25625_TXB_TXREQ;

        // Transmit the message via SPI
        select();
        if (spi_write_blocking(spi, buffer, 5 + data_len) != 5 + data_len) {
            // Handle SPI write error
            handleError("Error writing to SPI");
        }
        deselect();
    } else {
        // Handle the case where all TX buffers are filled (you may want to add specific error handling)
        handleError("All TX buffers are filled");
    }
}

bool MCP25625Driver::receiveMessage(uint32_t &id, uint8_t &data_len, uint8_t *data) {
    // Check if there's a message in the receive buffer
    uint8_t status = readRegister(MCP25625_CANINTF);
    if ((status & MCP25625_RX0IF) == 0) {
        // No message available
        return false;
    }

    // Read the received message
    uint8_t buffer[MCP25625_MAX_MESSAGE_LENGTH + 5];  // Buffer for the message

    buffer[0] = MCP25625_RXB0SIDH;  // Start at the SIDH register

    // Read the ID
    buffer[1] = 0;
    buffer[2] = 0;
    id = ((uint32_t)buffer[1] << 3) | (buffer[2] >> 5);

    // Read the data length and data
    data_len = buffer[4] & 0x0F;
    for (uint8_t i = 0; i < data_len; i++) {
        data[i] = buffer[5 + i];
    }

    // Clear the receive buffer full flag
    modifyRegister(MCP25625_CANINTF, MCP25625_RX0IF, 0);

    return true;
}

bool MCP25625Driver::isTXBufferFull() {
    // Check if any of the TX buffers are full
    return readTXStatus(0) & MCP25625_TXB_TXREQ ||
           readTXStatus(1) & MCP25625_TXB_TXREQ ||
           readTXStatus(2) & MCP25625_TXB_TXREQ;
}

void MCP25625Driver::sendDataPackets(uint32_t id, const uint8_t *data, size_t data_len) {
    const size_t packet_size = 8;  // Maximum data length per CAN frame
    size_t remaining_bytes = data_len;

    // Loop through data and send packets
    for (size_t i = 0; i < data_len; i += packet_size) {
        size_t current_packet_size = remaining_bytes < packet_size ? remaining_bytes : packet_size;

        // Send a packet
        sendMessage(id, current_packet_size, &data[i]);

        // Update remaining bytes
        remaining_bytes -= current_packet_size;

        // If there are no more remaining bytes, break out of the loop
        if (remaining_bytes == 0) {
            break;
        }
    }
}

void MCP25625Driver::select() {
    gpio_put(cs_pin, 0);
}

void MCP25625Driver::deselect() {
    gpio_put(cs_pin, 1);
}

void MCP25625Driver::writeRegister(uint8_t reg, uint8_t value) {
    select();
    if (spi_write_blocking(spi, &reg, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    if (spi_write_blocking(spi, &value, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    deselect();
}

uint8_t MCP25625Driver::readRegister(uint8_t reg) {
    select();
    if (spi_write_blocking(spi, &reg, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    uint8_t value;
    if (spi_read_blocking(spi, 0, &value, 1) != 1) {
        // Handle SPI read error
        handleError("Error reading from SPI");
    }
    deselect();
    return value;
}

void MCP25625Driver::modifyRegister(uint8_t reg, uint8_t mask, uint8_t data) {
    select();
    if (spi_write_blocking(spi, &reg, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    if (spi_write_blocking(spi, &mask, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    if (spi_write_blocking(spi, &data, 1) != 1) {
        // Handle SPI write error
        handleError("Error writing to SPI");
    }
    deselect();
}

bool MCP25625Driver::readTXStatus(uint8_t buffer_num) {
    // Read the status of the specified TX buffer
    return readRegister(MCP25625_TXB0CTRL + buffer_num * 0x10);
}

void MCP25625Driver::handleError(const char *message) {
    // Add your custom error handling logic here
    // For example, you can log the error, reset the device, or take appropriate action
    // You may also want to add error codes or return values to indicate specific error conditions
    // Print error message to the console for now
    printf("Error: %s\n", message);
    // You may want to add more robust error handling based on your application requirements
}