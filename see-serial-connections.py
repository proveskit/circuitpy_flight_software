import platform

import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

golden_port = None

for p in ports:
    string_p = str(p)
    print(string_p)
    serial_port = string_p.split(" - ")[0]
    name = string_p.split(" - ")[1]

    if name == "FLIGHT_CONTROLLER" and platform.system() == "Darwin":
        golden_port = serial_port

    elif name[:17] == "USB Serial Device":
        golden_port = serial_port


def convert_cu_to_tty(port):
    return "/dev/tty." + port.split("cu.")[1]
