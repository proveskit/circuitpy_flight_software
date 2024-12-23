import unittest
from unittest.mock import MagicMock
from Batt_Board.lib.can_bus_helper import CanBusHelper
from Batt_Board.lib.adafruit_mcp2515.canio import Message

class TestCanBusHelper(unittest.TestCase): #In progress! 

    def setUp(self): #runs before each test 
        self.mock_can_bus = MagicMock() #creates mock object for can bus
        self.helper = CanBusHelper(self.mock_can_bus, owner="test_owner", debug=True)
        #creating an instance of bus helper with the mock bus

    #Turns message(s) into list and converts each message into a string and then each string into a byte array.
    #Every 8 bytes is a chunk. If the byte array is greater than 8 bytes, the ID is transformed w/ the sequence # (chunk #).
    #For a byte array no longer than 8 bytes, the original ID is used to create the Message object 
    #(Message object is appended back to the message list which is returned by function).
    def test_construct_messages(self):
        id = 0x01 
        #example valid id (corresponds to BOOT_SEQUENCE according to MESSAGE_IDS dictionary in can_bus_helper.py)
        data = '{"sensor": "temperature", "value": 22.5}' #realistic sensor reading data
        messages = self.helper.construct_messages(id, data)
        self.assertEqual(len(messages), 1) #check number of messages
        expected_data = b'{"sensor": "temperature", "value": 22.5}'
        self.assertEqual(messages[0].data, expected_data) #check content of first message

#python3 test_can_bus_helper.py
if __name__ == '__main__':
    unittest.main()
