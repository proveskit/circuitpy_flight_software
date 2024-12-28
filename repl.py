print("Welcome to the Proves REPL!")
print("Run watchdog_init() to initialize the watchdog timer.")


def watchdog_init():
    import board
    import time
    import digitalio

    watchdog_pin = digitalio.DigitalInOut(board.WDT_WDI)
    watchdog_pin.direction = digitalio.Direction.OUTPUT
    watchdog_pin.value = False
