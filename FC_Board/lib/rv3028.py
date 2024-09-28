"""
This class handles communications

Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
"""

import time
import adafruit_bus_device.i2c_device as i2c_device

class RV3028:
    # Register addresses
    SECONDS = 0x00
    MINUTES = 0x01
    HOURS = 0x02
    WEEKDAY = 0x03
    DATE = 0x04
    MONTH = 0x05
    YEAR = 0x06
    STATUS = 0x0E
    CONTROL1 = 0x0F
    CONTROL2 = 0x10
    EVENT_CONTROL = 0x13
    TIMESTAMP_COUNT = 0x14
    TIMESTAMP_SECONDS = 0x15
    TIMESTAMP_MINUTES = 0x16
    TIMESTAMP_HOURS = 0x17
    TIMESTAMP_DATE = 0x18
    TIMESTAMP_MONTH = 0x19
    TIMESTAMP_YEAR = 0x1A
    EEPROM_BACKUP = 0x37

    def __init__(self, i2c_bus, address=0x52):
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

    def _read_register(self, register, length=1):
        with self.i2c_device as i2c:
            i2c.write(bytes([register]))
            result = bytearray(length)
            i2c.readinto(result)
            return result

    def _write_register(self, register, data):
        with self.i2c_device as i2c:
            i2c.write(bytes([register]) + data)

    def _bcd_to_int(self, bcd):
        return (bcd & 0x0F) + ((bcd >> 4) * 10)

    def _int_to_bcd(self, value):
        return ((value // 10) << 4) | (value % 10)

    def set_time(self, hours, minutes, seconds):
        data = bytes([
            self._int_to_bcd(seconds),
            self._int_to_bcd(minutes),
            self._int_to_bcd(hours)
        ])
        self._write_register(self.SECONDS, data)

    def get_time(self):
        data = self._read_register(self.SECONDS, 3)
        return (
            self._bcd_to_int(data[2]),  # hours
            self._bcd_to_int(data[1]),  # minutes
            self._bcd_to_int(data[0])   # seconds
        )

    def set_date(self, year, month, date, weekday):
        data = bytes([
            self._int_to_bcd(weekday),
            self._int_to_bcd(date),
            self._int_to_bcd(month),
            self._int_to_bcd(year)
        ])
        self._write_register(self.WEEKDAY, data)

    def get_date(self):
        data = self._read_register(self.WEEKDAY, 4)
        return (
            self._bcd_to_int(data[3]),  # year
            self._bcd_to_int(data[2]),  # month
            self._bcd_to_int(data[1]),  # date
            self._bcd_to_int(data[0])   # weekday
        )

    def set_alarm(self, minute, hour, weekday):
        # Set alarm mask to check for minute, hour, and weekday match
        control2 = self._read_register(self.CONTROL2)[0]
        control2 |= 0x08  # Set AIE (Alarm Interrupt Enable) bit
        self._write_register(self.CONTROL2, bytes([control2]))

        data = bytes([
            self._int_to_bcd(minute),
            self._int_to_bcd(hour),
            self._int_to_bcd(weekday)
        ])
        self._write_register(self.MINUTES, data)

    def enable_trickle_charger(self, resistance=3000):
        control1 = self._read_register(self.CONTROL1)[0]
        control1 |= 0x20  # Set TCE (Trickle Charge Enable) bit
        
        # Set TCR (Trickle Charge Resistor) bits
        if resistance == 3000:
            control1 |= 0x00
        elif resistance == 5000:
            control1 |= 0x01
        elif resistance == 9000:
            control1 |= 0x02
        elif resistance == 15000:
            control1 |= 0x03
        else:
            raise ValueError("Invalid trickle charger resistance")

        self._write_register(self.CONTROL1, bytes([control1]))

    def disable_trickle_charger(self):
        control1 = self._read_register(self.CONTROL1)[0]
        control1 &= ~0x20  # Clear TCE (Trickle Charge Enable) bit
        self._write_register(self.CONTROL1, bytes([control1]))

    def configure_evi(self, enable=True):
        """
        Configure EVI for rising edge detection, enable time stamping,
        and enable interrupt.
        
        :param enable: True to enable EVI, False to disable
        """
        if enable:
            # Configure Event Control Register
            event_control = 0x40  # EHL = 1 (rising edge), ET = 00 (no filtering)
            self._write_register(self.EVENT_CONTROL, bytes([event_control]))
            
            # Enable time stamping and EVI interrupt
            control2 = self._read_register(self.CONTROL2)[0]
            control2 |= 0x84  # Set TSE (bit 7) and EIE (bit 2)
            self._write_register(self.CONTROL2, bytes([control2]))
        else:
            # Disable time stamping and EVI interrupt
            control2 = self._read_register(self.CONTROL2)[0]
            control2 &= ~0x84  # Clear TSE (bit 7) and EIE (bit 2)
            self._write_register(self.CONTROL2, bytes([control2]))

    def get_event_timestamp(self):
        """
        Read the timestamp of the last EVI event.
        
        :return: Tuple of (year, month, date, hours, minutes, seconds, count)
        """
        data = self._read_register(self.TIMESTAMP_COUNT, 7)
        return (
            self._bcd_to_int(data[6]),  # year
            self._bcd_to_int(data[5]),  # month
            self._bcd_to_int(data[4]),  # date
            self._bcd_to_int(data[3]),  # hours
            self._bcd_to_int(data[2]),  # minutes
            self._bcd_to_int(data[1]),  # seconds
            data[0]  # count (not BCD)
        )

    def clear_event_flag(self):
        """
        Clear the Event Flag (EVF) in the Status Register.
        """
        status = self._read_register(self.STATUS)[0]
        status &= ~0x02  # Clear EVF (bit 1)
        self._write_register(self.STATUS, bytes([status]))

    def is_event_flag_set(self):
        """
        Check if the Event Flag (EVF) is set in the Status Register.
        
        :return: True if EVF is set, False otherwise
        """
        status = self._read_register(self.STATUS)[0]
        return bool(status & 0x02)  # Check EVF (bit 1)

    def configure_backup_switchover(self, mode='level', interrupt=False):
        """
        Configure the Automatic Backup Switchover function.
        
        :param mode: 'level' for Level Switching Mode (LSM),
                     'direct' for Direct Switching Mode (DSM),
                     or 'disabled' to disable switchover
        :param interrupt: True to enable backup switchover interrupt, False to disable
        """
        backup_reg = self._read_register(self.EEPROM_BACKUP)[0]
        
        # Clear existing BSM bits
        backup_reg &= ~0x0C

        if mode == 'level':
            backup_reg |= 0x0C  # Set BSM to 11 for LSM
        elif mode == 'direct':
            backup_reg |= 0x04  # Set BSM to 01 for DSM
        elif mode == 'disabled':
            pass  # BSM is already cleared to 00
        else:
            raise ValueError("Invalid mode. Use 'level', 'direct', or 'disabled'.")

        # Configure backup switchover interrupt
        if interrupt:
            backup_reg |= 0x40  # Set BSIE bit
        else:
            backup_reg &= ~0x40  # Clear BSIE bit

        # Always enable fast edge detection
        backup_reg |= 0x10  # Set FEDE bit

        # Write the configuration to EEPROM
        self._write_register(self.EEPROM_BACKUP, bytes([backup_reg]))

        # Update EEPROM (command 0x11)
        self._write_register(0x27, bytes([0x00]))  # First command must be 00h
        self._write_register(0x27, bytes([0x11]))  # Update command

    def is_backup_switchover_occurred(self):
        """
        Check if a backup switchover has occurred.
        
        :return: True if switchover occurred, False otherwise
        """
        status = self._read_register(self.STATUS)[0]
        return bool(status & 0x20)  # Check BSF (bit 5)

    def clear_backup_switchover_flag(self):
        """
        Clear the Backup Switchover Flag (BSF) in the Status Register.
        """
        status = self._read_register(self.STATUS)[0]
        status &= ~0x20  # Clear BSF (bit 5)
        self._write_register(self.STATUS, bytes([status]))
