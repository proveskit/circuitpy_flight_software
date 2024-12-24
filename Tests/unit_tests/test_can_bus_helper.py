import unittest
from unittest.mock import MagicMock
from Batt_Board.lib.can_bus_helper import CanBusHelper
from Batt_Board.lib.adafruit_mcp2515.canio import Message

class TestCanBusHelper(unittest.TestCase): #In progress! 

    def setUp(self): #runs before each test 
        self.mock_can_bus = MagicMock() #creates mock object for can bus
        self.helper = CanBusHelper(self.mock_can_bus, owner="test_owner", debug=True)
        #creating an instance of bus helper with the mock bus

    #id: identify type of message (should be in MESSAGE_ID dictionary in can_bus_helper.py)
    #data: contents of message
    #Turns message(s) into list and converts each message into a string and then each string into a byte array.
    #Every 8 bytes is a chunk. If the byte array is greater than 8 bytes, the id is transformed w/ the sequence # (chunk #).
    #For a byte array no longer than 8 bytes, the original id is used to create the Message object 
    #(Message object is appended back to the message list which is returned by function).
    def test_construct_messages_single(self): #single message -> less than 8 bytes
        id = 0x01 
        #example valid id (according to MESSAGE_IDS dictionary in can_bus_helper.py)
        data = 'T:22.5' #realistic sensor reading data?
        messages = self.helper.construct_messages(id, data)
        self.assertEqual(len(messages), 1) #check number of messages
        expected_data = b'T:22.5' #byte string
        self.assertEqual(messages[0].data, expected_data) #check content of first message
        self.assertEqual(messages[0].id, id) #original id is kept if single message
        self.assertFalse(messages[0].extended) #extended attribute should be false in case of single message

    def test_construct_messages_mult(self): #multiple messages -> longer than 8 bytes
        id = 0x01 #example valid id 
        data = '{"sensor": "temperature", "value": 22.5}' #realistic sensor reading data?
        messages = self.helper.construct_messages(id, data)

        self.assertEqual(len(messages), 5) #5 chunks of 8 bytes
        expected_chunks = [b'{"sensor', b'": "temp', b'erature"', b', value', b': 22.5}']
        
        for i, messages in enumerate(messages):
            self.assertEqual(message.data, expected_chunks[i]) #check content of each chunk
            expected_id = ((id & 0x7F) << 22) | i #transform id of message with sequence # (chunk #)
            self.assertEqual(messages.id, expected_id) #check id
            self.assertTrue(message.extended) #extended attribute should be true in case of multiple messages

    #id: identify type of message (should be in MESSAGE_ID dictionary in can_bus_helper.py)
    #data: contents of message
    #Checks id_str argument against message id dictionary and converts id to byte value. 
    #Calls construct_messages(id_byte, data). 
    #If the length of the list of messages returned is > 1, a Start of Transmission (SOT) handshake is initiated.
    #Sends constructed message list and waits for acknowledgment. 
    #If multiple messages, sends an End of Transmission (EOT) message.
    #Returns true if all steps successful, false otherwise.
    def test_send_can_invalid_id(self):
        id_str = 'BATTERY_TEMPERATURE' #not a valid id
        data = 'T:22.5'
        with self.assertRaises(ValueError) as context:
            self.helper.send_can(id_str, data)
        self.assertEqual(str(context.exception), f"Invalid ID string: {id_str}") 
        #check if ValueError exception is correctly raised at invalid id
    
    def test_send_can(self):
        id_str = 'BOOT_SEQUENCE' #valid id
        data = 'T:22.5'
        

        self.helper.construct_messages = MagicMock(return_value=[Message()])





#python3 test_can_bus_helper.py
if __name__ == '__main__':
    unittest.main()
