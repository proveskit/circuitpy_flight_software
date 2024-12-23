import time
from pysquared import cubesat as c

print("=" * 70)
print("Initializing Simple Repeater Commanding Script")
print("=" * 70)

c.radio1.node = 0xFA
c.radio1.destination = 0xFB
c.radio1.tx_power = 20
c.radio1.spreading_factor = 8
c.radio1.coding_rate = 5
passcode = "MATT"
cube_callsign = "KO6AZM"

while True:
    print(
        """
    =============== /\\ ===============
    = Please select command  :)      =
    ==================================
    1 - noop                         |
    2 - hreset                       |
    3 - shutdown                     |
    4 - query                        |
    5 - exec_cmd                     |
    6 - joke_reply                   |
    7 - FSK                          |
    8 - Repeat Code                  |
    9 - State of Health              |
    0 - FaceData
    ==================================
    """
    )

    chosen_command = input("Select cmd pls: ")

    packet = b""

    if chosen_command == "1":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\x8eb"
    elif chosen_command == "2":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\xd4\x9f"
    elif chosen_command == "3":
        packet = (
            b"\x00\x00\x00\x00" + passcode.encode() + b"\x12\x06" + b"\x0b\xfdI\xec"
        )
    elif chosen_command == "4":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"8\x93" + input()
    elif chosen_command == "5":
        packet = (
            b"\x00\x00\x00\x00" + passcode.encode() + b"\x96\xa2" + input("Command: ")
        )
    elif chosen_command == "6":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\xa5\xb4"
    elif chosen_command == "7":
        packet = b"\x00\x00\x00\x00" + passcode.encode() + b"\x56\xc4"
    elif chosen_command == "8":
        packet = (
            b"\x00\x00\x00\x00"
            + passcode.encode()
            + b"RP"
            + input("Message to Repeat: ")
        )
    elif chosen_command == "9":
        packet = (
            b"\x00\x00\x00\x00"
            + passcode.encode()
            + b"\x96\xa2"
            + b"f.state_of_health();f.listen()"
        )
    elif chosen_command == "0":
        packet = (
            b"\x00\x00\x00\x00"
            + passcode.encode()
            + b"\x96\xa2"
            + b"f.send_face()"
        )
    else:
        print(
            "Command is not valid or not implemented open radio_test.py and add them yourself!"
        )

    c.radio1.send(packet)
