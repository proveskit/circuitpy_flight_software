from pysquared import cubesat

test_message = "Hello There!"
debug_mode = True
number_of_attempts = 0

# Radio Configuration Setup Here
radio_cfg = {
    "spreading_factor": 8,
    "tx_power": 13,  # Set as a default that works for any radio
    "node": 0x00,
    "destination": 0x00,
    "receive_timeout": 5,
    "enable_crc": False,
}

# Setting the Radio
cubesat.radio1.spreading_factor = radio_cfg["spreading_factor"]
if cubesat.radio1.spreading_factor > 8:
    cubesat.radio1.low_datarate_optimize = True
else:
    cubesat.radio1.low_datarate_optimize = False
cubesat.radio1.tx_power = radio_cfg["tx_power"]
cubesat.radio1.receive_timeout = radio_cfg["receive_timeout"]
cubesat.radio1.enable_crc = False

cubesat.radio1.send(bytes("Hello world KN6YZZ!\r\n", "utf-8"))
print("Sent Hello World message!")

# Wait to receive packets.
print("Waiting for packets...")

while True:
    packet = cubesat.radio1.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print(f"Received (raw bytes): {packet}")
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        try:
            packet_text = str(packet, "ascii")
            print(f"Received (ASCII): {packet_text}")
        except UnicodeError:
            print("Hex data: ", [hex(x) for x in packet])
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = cubesat.radio1.last_rssi
        print(f"Received signal strength: {rssi} dB")
