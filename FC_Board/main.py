"""
Created by Nicole Maggard and Michael Pham 8/19/2022
Updated for Yearling by Nicole Maggard and Rachel Sarmiento 2/4/2023
Updated again for Orpheus by Michael Pham 9/30/2024
This is where the processes get scheduled, and satellite operations are handeled
"""

from pysquared import cubesat as c
import asyncio
import time
import traceback
import gc  # Garbage collection
import microcontroller
import functions
from debugcolor import co


def debug_print(statement):
    if c.debug:
        print(co(str(c.uptime) + "[MAIN]" + str(statement), "blue", "bold"))


f = functions.functions(c)


def initial_boot():
    c.watchdog_pet()
    f.beacon()
    c.watchdog_pet()
    f.listen()
    c.watchdog_pet()
    f.state_of_health()
    f.listen()
    c.watchdog_pet()


try:
    c.c_boot += 1  # Increment boot number
    debug_print("Boot number: " + str(c.c_boot))
    debug_print(str(gc.mem_free()) + " Bytes remaining")

    initial_boot()

except Exception as e:
    debug_print("Error in Boot Sequence: " + "".join(traceback.format_exception(e)))
finally:
    debug_print("Something went wrong!")


def critical_power_operations():

    initial_boot()
    c.watchdog_pet()

    f.Long_Hybernate()


def minimum_power_operations():

    initial_boot()
    c.watchdog_pet()

    f.Short_Hybernate()


def normal_power_operations():

    debug_print("Entering Norm Operations")

    # Defining L1 Tasks
    def check_power():
        gc.collect()

        debug_print("Checking Power State")

        if c.power_mode == "normal" or c.power_mode == "maximum":
            pwr = True
            if c.power_mode == "normal":
                c.RGB = (255, 255, 0)
            else:
                c.RGB = (0, 255, 0)
        else:
            pwr = False

        debug_print(c.power_mode)
        gc.collect()
        return pwr

    async def s_lora_beacon():

        while check_power():
            f.beacon()
            f.listen()
            c.watchdog_pet()
            f.state_of_health()
            f.listen()
            c.watchdog_pet()
            time.sleep(1)  # Guard Time

            await asyncio.sleep(30)

    async def g_face_data():

        while check_power():
            try:
                debug_print("Consider Adding a Logging Function Here!")
                f.all_face_data()

            except Exception as e:
                debug_print("Outta time! " + "".join(traceback.format_exception(e)))

            gc.collect()

            await asyncio.sleep(60)

    async def g_batt_data():

        while check_power():
            try:
                debug_print("Looking to get battery data...")
                batt_data = f.get_battery_data()

                debug_print("Battery Data: " + str(batt_data))

                debug_print(batt_data[0])
                debug_print(batt_data[1])
                debug_print(batt_data[2])

                c.battery_voltage = batt_data[0]
                c.draw_current = batt_data[1]
                c.charge_voltage = batt_data[2]
                c.charge_current = batt_data[3]
                c.is_charging = batt_data[4]
                c.battery_percentage = batt_data[5]

                c.check_reboot()

            except Exception as e:
                debug_print("Outta time! " + "".join(traceback.format_exception(e)))

            gc.collect()

            await asyncio.sleep(30)

    async def s_face_data():

        await asyncio.sleep(20)

        while check_power():
            try:
                debug_print("Looking to send face data...")
                f.send_face()

            except asyncio.TimeoutError as e:
                debug_print("Outta time! " + "".join(traceback.format_exception(e)))

            gc.collect()

            await asyncio.sleep(200)

    async def s_imu_data():

        await asyncio.sleep(45)

        while check_power():

            try:
                debug_print("Looking to get imu data...")
                IMUData = []

                debug_print("IMU has baton")
                IMUData = f.get_imu_data()
                f.send(IMUData)
                f.face_data_baton = False

            except Exception as e:
                debug_print("Outta time! " + "".join(traceback.format_exception(e)))

            gc.collect()

            await asyncio.sleep(100)

    async def detumble():

        await asyncio.sleep(300)

        while check_power():
            try:
                debug_print("Looking to detumble...")
                f.detumble()
                debug_print("Detumble complete")

            except Exception as e:
                debug_print(f"Outta time!" + "".join(traceback.format_exception(e)))

            gc.collect()

            await asyncio.sleep(300)

    async def joke():
        await asyncio.sleep(500)

        while check_power():
            try:
                debug_print("Joke send go!")
                f.joke()
                if f.listen_joke():
                    f.joke()
                debug_print("done!")
            except Exception as e:
                debug_print(f"Outta time!" + "".join(traceback.format_exception(e)))

            gc.collect()
            await asyncio.sleep(500)

    async def check_watchdog():

        c.hardware["WDT"] = True
        while check_power():
            c.watchdog_pet()
            await asyncio.sleep(5)
        c.hardware["WDT"] = False

    async def main_loop():
        # log_face_data_task = asyncio.create_task(l_face_data())

        t1 = asyncio.create_task(s_lora_beacon())
        t2 = asyncio.create_task(s_face_data())
        t3 = asyncio.create_task(s_imu_data())
        t4 = asyncio.create_task(g_face_data())
        t5 = asyncio.create_task(g_batt_data())
        t6 = asyncio.create_task(detumble())
        t7 = asyncio.create_task(joke())
        t8 = asyncio.create_task(check_watchdog())

        await asyncio.gather(t1, t2, t3, t4, t5, t6, t7, t8)

    asyncio.run(main_loop())


######################### MAIN LOOP ##############################
try:

    while True:
        # L0 automatic tasks no matter the battery level
        c.check_reboot()

        if c.power_mode == "critical":
            c.RGB = (0, 0, 0)
            critical_power_operations()

        elif c.power_mode == "minimum":
            c.RGB = (255, 0, 0)
            minimum_power_operations()

        elif c.power_mode == "normal":
            c.RGB = (255, 255, 0)
            normal_power_operations()

        elif c.power_mode == "maximum":
            c.RGB = (0, 255, 0)
            normal_power_operations()

        else:
            f.listen()

except Exception as e:
    debug_print("Critical in Main Loop: " + "".join(traceback.format_exception(e)))
    time.sleep(10)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
finally:
    debug_print("Going Neutral!")

    c.RGB = (0, 0, 0)
    c.hardware["WDT"] = False
