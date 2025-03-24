import os
import platform
import subprocess
import time

import serial
import serial.tools.list_ports


def convert_cu_to_tty(port):
    return "/dev/tty." + port.split("cu.")[1]


def find_FCBoard_port() -> str:
    ports = list(serial.tools.list_ports.comports())

    golden_port = None

    for port in ports:
        string_p = str(port)
        serial_port = string_p.split(" - ")[0]
        name = string_p.split(" - ")[1]

        print(string_p)
        if (
            name == "FLIGHT_CONTROLLER"
            or name.startswith("ProvesKit")
            and platform.system() != "Windows"
        ):
            golden_port = serial_port
            print("dfjdfajdjfdjasdjkadfjsk")

        elif name[:17] == "USB Serial Device":
            golden_port = serial_port

    if os.name == "posix" and platform.system() == "Linux":
        return golden_port

    # If on a Mac, the port will initially show as a cu device instead of tty
    if platform.system() == "Darwin":
        return convert_cu_to_tty(golden_port)

    return golden_port


def sync_time():
    port = find_FCBoard_port()

    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            print(
                "\nSync Time in Progress... DO NOT create a screen session or another serial connection to the board!!!"
            )
            repl_line_met = False
            while not repl_line_met:
                ser.write(b"\x03")
                # s = ser.read(10)
                lines = ser.readlines()

                for line in lines:
                    # print(line)
                    if b"Press any key to enter the REPL" in line:
                        repl_line_met = True
                        ser.write(b"\r\n")

            adafruit_line_met = False
            while not adafruit_line_met:
                # s = ser.read(10)
                lines = ser.readlines()

                for line in lines:
                    # print(line)
                    if b"Adafruit CircuitPython" in line:
                        adafruit_line_met = True

            ser.write(b"import lib.pysquared.rtc.rp2040 as rp")
            ser.write(b"\r\n")
            current_time_stuct = time.localtime()
            update_time_string = (
                "rp.RP2040RTC.set_time({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(
                    current_time_stuct.tm_year,
                    current_time_stuct.tm_mon,
                    current_time_stuct.tm_mday,
                    current_time_stuct.tm_hour,
                    current_time_stuct.tm_min,
                    current_time_stuct.tm_sec,
                    current_time_stuct.tm_wday,
                )
            )
            result = update_time_string.encode()
            ser.write(result)
            ser.write(b"\r\n")
            ser.write(b"import supervisor")
            ser.write(b"\r\n")
            ser.write(b"supervisor.reload()")
            ser.write(b"\r\n")
        print(
            "\nFINISHED! The time has been updated on the board! You may now create a screen session or another other serial connection to the board!\n"
        )

    except serial.serialutil.SerialException:
        if platform.system() == "Windows":
            print(
                "The time was unable to be updated because a separate serial connection is present.\nPlease close that connection, and try the make-sync command again."
            )
            return

        print(
            "\nThere is currently a screen session used with the board. This prevents this command from being able to run."
        )
        print(
            "If the serial connection happens to be a screen session, the screen session will first be terminated, and the time will be updated."
        )

        processID_output = subprocess.check_output(["fuser", port])

        processID = processID_output.decode().split("\n")[0]

        try:
            # checking if screen is present
            isScreen = subprocess.check_output(["screen", "-ls", processID])
        except Exception:
            print(
                "An exception occured during the command. Please try the command again."
            )
            return

        # screen session not detected
        if isScreen[:11] == "No Sockets":
            print(
                "The time was unable to be updated because a separate serial connection is present.\nPlease close that connection, and try the make-sync command again."
            )
            return

        print(
            "A screen session associated with the serial port has been found. That screen process will be deleted and the time will be updated\n"
        )

    except Exception:
        # try:
        #   # print(processID)
        #   subprocess.call(["kill", processID])

        # except Exception:
        print("JAODSJKSAJKFJKDSFKJDSJKDS")

        # time.sleep(2)
        # sync_time()


sync_time()
