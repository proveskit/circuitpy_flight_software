# FCB_class.py
import time
import storage
import os

class FCBCommunicator:
    def __init__(self, com_instance):
        self.com = com_instance
        self.image_counter = 0
        self.last_num = self.get_last_num()

        #Uncomment for practical testing (Not using an IDE)
        #storage.remount("/", readonly=False)

    def send_command(self, command):
        self.com.overhead_send(command)

    def get_last_num(self):
        if(os.stat('last_num.txt')[6] == 0):
            with open('last_num.txt', 'w') as file:
                print("File was empty. Bummer...")
                file.write(str(1))
        try:
            with open('last_num.txt', 'r') as f:
                return int(f.read())
        except OSError:
            return 1
        
    def wait_for_acknowledgment(self):
        while True:
            acknowledgment = self.com.overhead_read()
            if acknowledgment == 'acknowledge':
                print('Acknowledgment received, proceeding with data transfer...')
                return True
            time.sleep(1)

    def send_chunk_request(self, lowerchunk='0', upperchunk='10'):
        if lowerchunk.isdigit() and upperchunk.isdigit() and int(lowerchunk) <= int(upperchunk):
            message = f"{lowerchunk} {upperchunk}"
            self.send_command(message)
            print(message)
            
            jpg_bytes, count = self.com.read_bytes(lowerchunk, upperchunk)
            print('Number of chunks received = ', count)
            print('Number of bytes received = ', len(jpg_bytes))
            return jpg_bytes
        else:
            print('Incorrect input, only accepted whole numbers.')
            self.send_command("Wrong")
            return None

    def save_image(self, jpg_bytes):
        filename = f"inspireFly_Capture_{self.image_counter}.jpg"
        try:
            with open(filename, "wb") as file:
                file.write(jpg_bytes)
                print(f"{filename} successfully created!")
            self.image_counter += 1
        except OSError as e:
            print(f"Failed to write file: {e}")

    def end_communication(self):
        self.send_command("end")
        print("Ended communications.")
