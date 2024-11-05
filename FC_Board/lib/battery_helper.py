# Written with Claude 3.5
# Author: Michael Pham
# Date: 2024-11-05

class BatteryHelper:
    """Helper class for interfacing with PicoSquared battery management system"""
    
    # Command definitions
    CMD_GET_TEMPERATURES = 1    # Returns thermocouple_temp, board_temp
    CMD_GET_POWER = 2          # Returns battery_v, draw_i, charge_v, charge_i, is_charging
    CMD_GET_ERRORS = 3         # Returns error_count, trust_memory
    CMD_TOGGLE_FACES = 4       # Toggle face LEDs, returns face status
    CMD_RESET_BUS = 5          # Reset power bus
    CMD_TOGGLE_CAMERA = 6      # Toggle camera power, returns camera status
    CMD_USE_AUX_RADIO = 7      # Switch to auxiliary radio
    CMD_RESET_FC = 8           # Reset flight controller
    CMD_BURN_COMPLETE = 9      # Set burn complete flag
    CMD_RESET_MCU = 11         # Reset microcontroller
    
    def __init__(self, pysquared):
        """Initialize with a PicoSquared object that has UART initialized"""
        self.ps2 = pysquared
        
    def send_command(self, cmd):
        """Send a command and return the response"""
        # Convert command to ASCII character
        cmd_char = str(cmd).encode('ascii')
        self.ps2.uart.write(cmd_char)
        
        # Wait for and read response
        response = bytearray()
        while self.ps2.uart.in_waiting:
            byte = self.ps2.uart.read(1)
            if byte is None:
                break
            response.extend(byte)
            
        return response.decode('ascii').strip()
    
    def get_temperatures(self):
        """
        Get thermocouple and board temperatures
        Returns: dict with 'thermocouple' and 'board' temperatures in degrees C
        """
        response = self.send_command(self.CMD_GET_TEMPERATURES)
        try:
            thermo_temp, board_temp = map(float, response.split(','))
            return {
                'thermocouple': thermo_temp,
                'board': board_temp
            }
        except (ValueError, AttributeError):
            return None
            
    def get_power_metrics(self):
        """
        Get power-related measurements
        Returns: dict with battery voltage, currents, and charging status
        """
        response = self.send_command(self.CMD_GET_POWER)
        try:
            batt_v, draw_i, charge_v, charge_i, is_charging = response.split(',')
            return {
                'battery_voltage': float(batt_v),
                'draw_current': float(draw_i),
                'charge_voltage': float(charge_v),
                'charge_current': float(charge_i),
                'is_charging': bool(int(is_charging))
            }
        except (ValueError, AttributeError):
            return None
            
    def get_error_metrics(self):
        """
        Get error count and trust memory
        Returns: dict with error count and trust memory values
        """
        response = self.send_command(self.CMD_GET_ERRORS)
        try:
            error_count, trust_memory = map(int, response.split(','))
            return {
                'error_count': error_count,
                'trust_memory': trust_memory
            }
        except (ValueError, AttributeError):
            return None
            
    def toggle_faces(self):
        """Toggle face LEDs"""
        return self.send_command(self.CMD_TOGGLE_FACES)
        
    def reset_power_bus(self):
        """Reset the power bus"""
        return self.send_command(self.CMD_RESET_BUS)
        
    def toggle_camera(self):
        """Toggle camera power"""
        return self.send_command(self.CMD_TOGGLE_CAMERA)
        
    def use_auxiliary_radio(self):
        """Switch to auxiliary radio"""
        return self.send_command(self.CMD_USE_AUX_RADIO)
        
    def reset_flight_controller(self):
        """Reset the flight controller"""
        return self.send_command(self.CMD_RESET_FC)
        
    def set_burn_complete(self):
        """Set the burn complete flag"""
        return self.send_command(self.CMD_BURN_COMPLETE)
        
    def reset_mcu(self):
        """Reset the microcontroller"""
        return self.send_command(self.CMD_RESET_MCU)