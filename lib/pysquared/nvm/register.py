from micropython import const


class NVM:
    BOOTCNT = const(0)
    ERRORCNT = const(7)
    FLAG = const(16)


class FLAG_01:
    SOFTBOOT = const(0)
    BROWNOUT = const(3)
    SHUTDOWN = const(5)
    BURNED = const(6)
    USE_FSK = const(7)
