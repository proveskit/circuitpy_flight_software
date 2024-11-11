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
        
    def _flush_input(self):
        """Flush the input buffer"""
        try_count = 0
        while self.uart.in_waiting and try_count < 10:
            try_count += 1
            self.uart.read()
            
    def _read_response(self, timeout_ms=1000, retries=3):
        """
        Read response with retries and intelligent waiting
        
        Args:
            timeout_ms: Maximum time to wait for response in milliseconds
            retries: Number of retry attempts if response is invalid
            
        Returns:
            Response string or empty string on failure
        """
        
        for attempt in range(retries):
            start = time.monotonic()
            response = bytearray()
            
            # Initial delay to allow response to arrive
            time.sleep(0.05)  # 50ms initial wait
            
            # Read until timeout or valid response
            while (time.monotonic() - start) * 1000 < timeout_ms:
                if self.uart.in_waiting:
                    chunk = self.uart.read()
                    if chunk:
                        response.extend(chunk)
                        # If we got data, reset timeout to allow for more
                        start = time.monotonic()
                        timeout_ms = 500  # Reset timeout to 500ms
                else:
                    # Small delay only if no data available
                    time.sleep(0.01)
                    
                # Check if we have a complete response
                if response and response[-1] in [ord('\n'), ord('\r')]:
                    break
            
            if response:
                try:
                    return response.decode('utf-8').strip()
                except UnicodeDecodeError:
                    continue  # Try again if decode failed
                    
            # If we get here with no response, wait longer before next retry
            time.sleep(0.1 * (attempt + 1))  # Increasing delay between retries
            
        return ""
            
    def _send_command(self, cmd: int, min_interval_ms=100) -> str:
        """
        Send a command and return the response with rate limiting
        
        Args:
            cmd: Command number to send
            min_interval_ms: Minimum time between commands in milliseconds
            
        Returns:
            Response string from the device
        """
        
        try:
            current_time = time.monotonic()
            
            # Rate limiting
            time_since_last = (current_time - self.last_command_time) * 1000
            if time_since_last < min_interval_ms:
                time.sleep((min_interval_ms - time_since_last) / 1000)
            
            # Clear any pending data
            self._flush_input()
            
            # Send command with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                # Send command
                self.uart.write(bytes(cmd.encode()))
                response = self._read_response(timeout_ms=1000)
                
                if response:
                    self.last_command_time = time.monotonic()
                    return response
                    
                # If no response, wait before retry
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
            
            print("Failed to get response after all retries")
            return ""
            
        except Exception as e:
            print(f"UART error: {e}")
            return ""
    
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
        max_retries = 3
        for attempt in range(max_retries):
            response = self._send_command(self.CMD_GET_POWER)
            if response:
                try:
                    metrics = response.split(',')
                    if len(metrics) == 5:
                        # Create tuple manually instead of using unpacking
                        values = []
                        for i in range(4):
                            values.append(float(metrics[i]))
                        values.append(bool(int(metrics[4])))
                        
                        # Basic sanity checks
                        if all(0 <= v <= 100 for v in values[:4]):  # Adjust ranges as needed
                            return tuple(values)
                except Exception as e:
                    print(f"Error parsing power metrics (attempt {attempt + 1}): {e}")
            
            import time
            time.sleep(0.1 * (attempt + 1))
            
        print("Failed to get valid power metrics after all retries")
        return (0.0, 0.0, 0.0, 0.0, False)
            
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