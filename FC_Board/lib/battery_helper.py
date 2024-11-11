import time

# Written with Claude 3.5
# Author: Michael Pham
# Date: 2024-11-05

class BatteryHelper:
    """Helper class for interfacing with PicoSquared battery management system"""
    
    # Command definitions
    CMD_GET_TEMPERATURES = "1"    # Returns thermocouple_temp, board_temp
    CMD_GET_POWER = "2"          # Returns battery_v, draw_i, charge_v, charge_i, is_charging
    CMD_GET_ERRORS = "3"         # Returns error_count, trust_memory
    CMD_TOGGLE_FACES = "4"       # Toggle face LEDs, returns face status
    CMD_RESET_BUS = "5"          # Reset power bus
    CMD_TOGGLE_CAMERA = "6"      # Toggle camera power, returns camera status
    CMD_USE_AUX_RADIO = "7"      # Switch to auxiliary radio
    CMD_RESET_FC = "8"           # Reset flight controller
    CMD_BURN_COMPLETE = "9"      # Set burn complete flag
    CMD_RESET_MCU = "11"         # Reset microcontroller
    CMD_ERROR = "208"
    
    def __init__(self, pysquared):
        """
        Initialize UART helper with existing Pysquared object
        
        Args:
            pysquared: Pysquared object with initialized UART
        """
        self.uart = pysquared.uart
        self.last_command_time = 0
        self.debug_mode = True
        
    def _flush_input(self):
        """Flush the input buffer"""
        try_count = 0
        while self.uart.in_waiting and try_count < 10:
            try_count += 1
            self.uart.read()
            
    def _wait_for_ack(self):
        """Wait for acknowledgment character"""
        start = time.monotonic()
        
        # Clear any existing data
        if self.uart.in_waiting:
            self.uart.read()
            
        # Wait up to 10ms for ACK
        while (time.monotonic() - start) * 1000 < 10:
            if self.uart.in_waiting:
                byte = self.uart.read(1)
                if self.debug_mode:
                    print(f"ACK byte received: {byte}")
                if byte == b'A':
                    return True
            time.sleep(0.001)
        return False
    
    def _read_message(self, timeout_ms=150):
        """Read until we get a complete message or timeout"""

        response = bytearray()
        
        # Initial wait for data
        start = time.monotonic()
        while not self.uart.in_waiting and (time.monotonic() - start) * 1000 < timeout_ms:
            pass
            
        # Read data as it comes
        last_read = time.monotonic()
        while (time.monotonic() - last_read) * 1000 < 5:  # 5ms timeout between chunks
            if self.uart.in_waiting:
                response.extend(self.uart.read())
                last_read = time.monotonic()
        
        try:
            text = response.decode('utf-8')
            if self.debug_mode:
                print(f"Buffer: {text}")
                
            # Check for complete message
            if 'AA<' in text and '>' in text:
                start_idx = text.find('<')
                end_idx = text.find('>')
                if start_idx < end_idx:
                    return text[start_idx+1:end_idx]
        except UnicodeDecodeError:
            pass
            
        return ""
            
    def _send_command(self, cmd):
        """
        Send command and wait for acknowledgment
        
        Returns:
            str: Response message or empty string on failure
        """
        try:

            # Send command
            self.uart.write(bytes(cmd.encode()))
                
            # Read the response message
            return self._read_message()
            
        except Exception as e:
            print(f"UART error: {e}")
            return ""
        
    def _is_valid_message(self, msg):
        """Verify message format and checksum if implemented"""
        return bool(msg and len(msg) > 0)
    
    def get_temperatures(self):
        """
        Get thermocouple and board temperatures
        Returns: dict with 'thermocouple' and 'board' temperatures in degrees C
        """
        response = self._send_command(self.CMD_GET_TEMPERATURES)
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
        
        Returns:
            Tuple of (battery_voltage, draw_current, charge_voltage, 
                     charge_current, is_charging)
        """
        response = self._send_command(self.CMD_GET_POWER)
        
        if response:
            try:
                parts = response.split(',')
                if len(parts) == 5:
                    return (
                        float(parts[0]),
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                        bool(int(parts[4])),
                        self.get_battery_percentage(float(parts[0]), bool(int(parts[4])))
                    )
            
            except Exception as e:
                if self.debug_mode:
                    print(f"Error parsing metrics: {e}")
        
        if self.debug_mode:
            print("Failed to get valid power metrics")
        return (0.0, 0.0, 0.0, 0.0, False, 0.0)
            
    def get_error_metrics(self):
        """
        Get error count and trust memory
        Returns: dict with error count and trust memory values
        """
        response = self._send_command(self.CMD_GET_ERRORS)
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
        return self._send_command(self.CMD_TOGGLE_FACES)
        
    def reset_power_bus(self):
        """Reset the power bus"""
        return self._send_command(self.CMD_RESET_BUS)
        
    def toggle_camera(self):
        """Toggle camera power"""
        return self._send_command(self.CMD_TOGGLE_CAMERA)
        
    def use_auxiliary_radio(self):
        """Switch to auxiliary radio"""
        return self._send_command(self.CMD_USE_AUX_RADIO)
        
    def reset_flight_controller(self):
        """Reset the flight controller"""
        return self._send_command(self.CMD_RESET_FC)
        
    def set_burn_complete(self):
        """Set the burn complete flag"""
        return self._send_command(self.CMD_BURN_COMPLETE)
        
    def reset_mcu(self):
        """Reset the microcontroller"""
        return self._send_command(self.CMD_RESET_MCU)
    
    def get_battery_percentage(self, pack_voltage, is_charging=False):
        """
        Estimate remaining battery percentage for 2S LG MJ1 pack based on voltage.
        Accounts for voltage rise during charging.
        
        Args:
            pack_voltage (float): Current voltage of 2S battery pack
            is_charging (bool): Whether the pack is currently being charged
        
        Returns:
            float: Estimated remaining capacity percentage (0-100)
        """
        # Convert pack voltage to cell voltage
        cell_voltage = pack_voltage / 2
        
        # Voltage compensation when charging (0.35V per cell = 0.7V per pack)
        if is_charging:
            cell_voltage = cell_voltage - 0.35
        
        # Lookup table from 1A discharge curve [voltage, capacity_remaining_percent]
        DISCHARGE_CURVE = [
            (4.2, 100),    # Full charge
            (4.0, 90),     # Initial drop
            (3.9, 80),
            (3.8, 70),
            (3.7, 60),
            (3.6, 50),
            (3.5, 40),
            (3.4, 30),
            (3.3, 20),
            (3.2, 15),
            (3.1, 10),
            (3.0, 5),
            (2.8, 2),
            (2.7, 0)       # Cutoff at 5.4V pack voltage
        ]
        
        # Handle edge cases
        if cell_voltage >= 4.2:
            return 100
        if cell_voltage <= 2.7:
            return 0
            
        # Find the two voltage points our cell voltage falls between
        for i in range(len(DISCHARGE_CURVE)-1):
            v1, p1 = DISCHARGE_CURVE[i]
            v2, p2 = DISCHARGE_CURVE[i+1]
            
            if v2 <= cell_voltage <= v1:
                # Linear interpolation between points
                percent = p2 + (p1 - p2) * (cell_voltage - v2) / (v1 - v2)
                return round(percent, 1)
        
        return 0  # Fallback
    
    def debug_timing(self):
        """Measure and print timing of each step"""
        
        print("\nTiming analysis:")
        
        # Measure command send time
        start = time.monotonic()
        self.uart.write(bytes(self.CMD_GET_POWER.encode()))
        send_time = (time.monotonic() - start) * 1000
        
        # Measure response read time
        read_start = time.monotonic()
        response = self._read_message()
        read_time = (time.monotonic() - read_start) * 1000
        
        # Measure parse time
        parse_start = time.monotonic()
        if response:
            try:
                parts = response.split(',')
                values = [float(x) for x in parts[:4]]
                values.append(bool(int(parts[4])))
            except Exception as e:
                print(f"Parse error: {e}")
        parse_time = (time.monotonic() - parse_start) * 1000
        
        # Total time
        total_time = (time.monotonic() - start) * 1000
        
        print(f"Send time: {send_time:.2f}ms")
        print(f"Read time: {read_time:.2f}ms")
        print(f"Parse time: {parse_time:.2f}ms")
        print(f"Total time: {total_time:.2f}ms")
        print(f"Response: {response}")