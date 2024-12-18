"""
Created by Nicole Maggard 12/26/2023
"""

from pysquared_eps import cubesat as c  # pylint: disable=import-error
import asyncio
import time
import traceback
import gc  # Garbage collection
import microcontroller  # pylint: disable=import-error
import battery_functions  # pylint: disable=import-error
from debugcolor import co  # pylint: disable=import-error

f = battery_functions.functions(c)


def debug_print(statement):
    if c.debug:
        print(co("[BATTERY][MAIN]" + str(statement), "blue", "bold"))

    # Defining Operations Within The Power Modes
    """These functions is called when the satellite transitions between various power states.
    It generally thse modes manage the battery, checks the state of health of the system,
    performs a reboot check, and then puts the system into a short hibernation
    mode to conserve power.

    When in low or critical power modes, the satellite will not perform any complex tasks.

    The sub-functions that can be called are:
    - `battery_manager()`: Manages and monitors the battery status.
    - `state_of_health()`: Checks the overall health and status of the satellite.
    - `check_reboot()`: Determines if a system reboot is necessary.
    - `Short_Hybernate()`: Puts the system into a low-power hibernation state.
    """  # pylint: disable=pointless-string-statement


def boot_sequence():
    """
    Perform the boot sequence.

    Returns:
        None
    """

    debug_print("Boot number: " + str(c.c_boot))
    debug_print(str(gc.mem_free()) + " Bytes remaining")  # pylint: disable=no-member

    # power cycle faces to ensure sensors are on:
    c.all_faces_off()
    time.sleep(1)
    c.all_faces_on()
    # test the battery:
    f.battery_manager()

    # Consider Deprecating the Loiter Time
    LOITER_TIME = 1
    for _ in range(LOITER_TIME):
        c.RGB = (255, 0, 255)
        time.sleep(0.5)
        c.RGB = (0, 0, 0)
        time.sleep(0.5)
    c.RGB = (0, 0, 255)

    f.state_of_health()
    f.battery_manager()
    time.sleep(1)
    f.battery_manager()  # Second check to make sure we have enough power to continue
    f.state_of_health()


def critical_power_operations():
    """
    Perform operations necessary during critical power mode.

    Returns:
        None
    """
    f.battery_manager()
    f.state_of_health()
    f.check_reboot()
    f.Short_Hybernate()


def low_power_operations():
    f.battery_manager()
    f.state_of_health()
    f.check_reboot()


def normal_power_operations():

    debug_print("Entering Norm Operations")
    FaceData = []  # Clearing FaceData
    # Defining L1 Tasks

    def check_power():
        gc.collect()
        f.battery_manager()
        f.check_reboot()
        f.battery_manager()  # Second check to make sure we have enough power to continue

        if c.power_mode == "normal" or c.power_mode == "maximum":
            pwr = True
            if c.power_mode == "normal":
                c.RGB = (255, 255, 0)
            else:
                c.RGB = (0, 255, 0)
        else:
            pwr = False

        debug_print("power mode" + str(c.power_mode))
        gc.collect()
        return pwr

    # Consider Deprecating this function or changing it to a logging function. Currently it serves no purpose outside of debug.
    async def g_face_data():

        while check_power():

            FaceData = []

            try:
                debug_print("Getting face data...")
                FaceData = f.all_face_data()
                for _ in range(0, len(FaceData)):
                    debug_print("Face " + str(_) + ": " + str(FaceData[_]))

            except Exception as e_gf:
                debug_print(
                    "Outta time! " + "".join(traceback.format_exception(e_gf))
                )  # pylint: disable=no-value-for-parameter

            gc.collect()

            await asyncio.sleep(60)

    async def s_face_data():

        await asyncio.sleep(20)

        while check_power():
            try:
                debug_print("Looking to send face data...")
                f.send_face()

            except asyncio.TimeoutError as e_sf:
                debug_print(
                    "Outta time! " + "".join(traceback.format_exception(e_sf))
                )  # pylint: disable=no-value-for-parameter

            gc.collect()

            await asyncio.sleep(200)

    async def detumble():

        await asyncio.sleep(300)

        while check_power():
            try:
                debug_print("Looking to detumble...")
                f.detumble()
                debug_print("Detumble complete")

            except Exception as e_de:
                debug_print(
                    f"Outta time!" + "".join(traceback.format_exception(e_de))
                )  # pylint: disable=no-value-for-parameter

            gc.collect()

            await asyncio.sleep(300)

    async def main_loop():
        # log_face_data_task = asyncio.create_task(l_face_data())

        t1 = asyncio.create_task(s_face_data())
        t2 = asyncio.create_task(g_face_data())
        t3 = asyncio.create_task(detumble())

        await asyncio.gather(t1, t2, t3)

    asyncio.run(main_loop())


######################### MAIN LOOP ##############################
try:
    c.all_faces_on()
    try:
        boot_sequence()

    except Exception as e_bo:
        debug_print(
            "Error in Boot Sequence: " + "".join(traceback.format_exception(e_bo))
        )  # pylint: disable=no-value-for-parameter

    finally:
        debug_print("All Faces off!")
        c.all_faces_off()

    while True:
        # L0 automatic tasks no matter the battery level
        f.battery_manager()
        f.check_reboot()

        if c.power_mode == "critical":
            c.RGB = (0, 0, 0)
            critical_power_operations()

        elif c.power_mode == "low":
            c.RGB = (255, 0, 0)
            low_power_operations()

        elif c.power_mode == "normal":
            c.RGB = (255, 255, 0)
            normal_power_operations()

        elif c.power_mode == "maximum":
            c.RGB = (0, 255, 0)
            normal_power_operations()

        else:
            # If the power mode is not recognized, the system will default to critical power mode.
            critical_power_operations()

except Exception as e:
    # This block of code soft resets the system if an error occurs in the main loop. Can lead to boot looping if the error is not fixed.
    debug_print(
        "Fatal Error in Main Loop: " + "".join(traceback.format_exception(e))
    )  # pylint: disable=no-value-for-parameter
    time.sleep(15)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
finally:
    debug_print("All Faces off!")
    c.all_faces_off()
    c.RGB = (0, 0, 0)
