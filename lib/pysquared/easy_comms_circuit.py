import time
import board
import busio
from lib.pysquared import cubesat as c

class EasyComms:
    
    # Initialize
    baud_rate = 9600
    timeout = 5  # Timeout in seconds
    
#     # Backend setup
    def __init__(self, uart_tx_pin, uart_rx_pin, baud_rate=None):
#         if baud_rate:
#             self.baud_rate = baud_rate
#         # Set up UART interface
          self.uart = c.uart
    
    # Send bytes across
    def send_bytes(self, data: bytes):
        print("Sending bytes...")
        self.uart.write(data)  # write data to port
    
    # Hello!
    def start(self):
        message = "Ahoy!\n"
        print(message)
    
    # CRC Bit Check, returns 2 bytes of integers
    def calculate_crc16(self, data: bytes) -> int:
        crc = 0x1D0F  # CCITT-False is 0xFFFF
        poly = 0x1021  # CRC-CCITT polynomial
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc <<= 1
                crc &= 0xFFFF  # Limit to 16 bits
        return crc
    
    # Read bytes sent across, strip the overhead and CRC
    def read_bytes(self, lowerchunk, upperchunk) -> bytes:
        message = b""
        count = 0
        chunksize = 70
        
        # Collect Chunks
        for i in range(int(lowerchunk), int(upperchunk) + 1):
            time.sleep(1)  # Wait for bytes
            if self.uart.in_waiting > 0:  # Check if there are bytes to read
                data = self.uart.read(chunksize)
                print("Data", data)
                
                # CRC Check
                crctagbb = data[-2:]  # Grab CRC from incoming chunk
                chunknum = data[:2]  # Grab chunk number from incoming chunk
                print("Chunk number: ", chunknum)
                print("Crc tagbb: ", crctagbb)
                
                crctagb = int.from_bytes(crctagbb, 'little')  # Convert CRC bytes to integer
                stripped_data = data[:-2]  # Strip off CRC tag from chunk
                crctaga = self.calculate_crc16(stripped_data)  # Calculate CRC of the stripped chunk
                stripped_data2 = stripped_data[2:]  # Strip overhead, leaving photo bytes
                
                if crctaga == crctagb:  # If CRCs match, no error in the chunk
                    message += stripped_data2
                    request = "A has received chunk with no error!"
                    self.overhead_send(request)  # Confirm reception of chunk
                    count += 1
                else:
                    # If chunk is corrupted
                    while crctaga != crctagb:
                        request = "Chunk has an error."
                        print(request, i)
                        self.overhead_send(request)
                    print("Successfully received chunk!")
            print("Chunk Byte length: ", len(message))
        
        if len(message) > 0:
            return message, count
        else:
            return None
    
    # Send strings across the port
    def overhead_send(self, msg: str):
        print(f'Sending Message: {msg}...')
        msg = msg + '\n'
        self.uart.write(bytes(msg, 'utf-8'))
    
    # Read the strings sent across
    def overhead_read(self) -> str:
        new_line = False
        message = ""
        while not new_line:
            if self.uart.in_waiting > 0:
                message += self.uart.read(1).decode('utf-8')
                if '\n' in message:
                    new_line = True
                    message = message.strip('\n')
                    return message
        return None
