import traceback
import time

from adafruit_mcp2515.canio import (
    Message,
    RemoteTransmissionRequest,
)  # pylint: disable=import-error
from debugcolor import co  # pylint: disable=import-error

# There may be an AI induced error with the traceback statements


class CanBusHelper:
    def __init__(self, can_bus, owner, debug):
        self.can_bus = can_bus
        self.owner = owner
        self.debug = debug
        self.multi_message_buffer = {}
        self.current_id = 0x00
        self.MESSAGE_IDS = {
            "BOOT_SEQUENCE": 0x01,
            "CRITICAL_POWER_OPERATIONS": 0x02,
            "LOW_POWER_OPERATIONS": 0x03,
            "NORMAL_POWER_OPERATIONS": 0x04,
            "FAULT_ID": 0x1A4,
            "SOT_ID": 0xA5,
            "EOT_ID": 0xA6,
            # Add more message IDs as needed
        }

    def debug_print(self, statement):
        if self.debug:
            print(co("[CAN_BUS][Communications]" + str(statement), "orange", "bold"))

    # BROKEN
    def construct_messages(self, id, messages):
        if not isinstance(messages, list):
            messages = [messages]
        message_objects = []
        sequence_number = 0  # Initialize sequence number

        for message in messages:
            message = str(message)
            byte_message = bytes(message, "UTF-8")

            for i in range(0, len(byte_message), 8):
                chunk = byte_message[i : i + 8]

                if len(byte_message) > 8:
                    # Use the sequence number across all messages in the list
                    extended_id = ((id & 0x7F) << 22) | sequence_number
                    message_objects.append(Message(extended_id, chunk, extended=True))
                    sequence_number += 1  # Increment sequence number for next chunk
                else:
                    # For single message, keep the original ID
                    message_objects.append(Message(id, chunk))

        return message_objects

    def send_can(self, id_str, data, timeout=5):
        if id_str in self.MESSAGE_IDS:
            id_byte = self.MESSAGE_IDS[id_str]
        else:
            # Handle the case where id_str is not in MESSAGE_IDS
            raise ValueError(f"Invalid ID string: {id_str}")

        # Construct the messages
        messages = self.construct_messages(id_byte, data)

        # Use SOT and EOT only for multi-message transmissions
        if len(messages) > 1:
            # Initiate handshake by sending SOT and waiting for ACK
            if not self.send_sot(id_byte, len(messages)):
                self.debug_print("Handshake failed: SOT not acknowledged")
                return False

        # Send the messages and wait for ACK
        if not self.send_messages(messages, timeout):
            return False

        if len(messages) > 1:
            # Send EOT after sending all messages
            self.send_eot()

        return True

    def send_messages(self, messages, timeout=1):
        """
        Sends the given messages and waits for acknowledgments.
        """
        for i, message in enumerate(messages):
            attempts = 0
            ack_received = False
            while attempts < 3 and not ack_received:
                try:
                    self.can_bus.send(message)
                    self.debug_print("Sent CAN message: " + str(message))
                    ack_received = self.wait_for_ack(
                        expected_ack_id=message.id, timeout=1.0
                    )
                    if not ack_received:
                        attempts += 1
                        self.debug_print(
                            f"ACK not received for message {i}. Attempt {attempts}"
                        )
                except Exception as e:
                    self.debug_print(
                        "Error Sending data over CAN bus"
                        + "".join(traceback.format_exception(None, e, e.__traceback__))
                    )
                    break

            if not ack_received:
                self.debug_print(
                    f"Failed to receive ACK after {attempts} attempts for message {i}."
                )
                return False

        return True

    def wait_for_ack(self, expected_ack_id, timeout):
        """
        Waits for an ACK message with the specified ID within the given timeout period.
        """
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            ack_id = self.receive_ack_message()

            if ack_id is not None and ack_id == expected_ack_id:
                return True
        self.debug_print("No ACK received")
        return False

    # =======================================================#
    # ChatGPT Go Crazy                                      #
    # =======================================================#

    def listen_on_can_bus(self, process_message_callback, timeout=1.0):
        """
        General purpose function to listen on the CAN bus and process messages using a callback function.
        Add identical message rejection?
        """
        with self.can_bus.listen(timeout=timeout) as listener:
            message_count = listener.in_waiting()
            for _ in range(message_count):
                try:
                    msg = listener.receive()
                    result = process_message_callback(msg)
                    if result is not None:
                        return result
                except Exception as e:
                    self.debug_print(
                        "Error processing message: "
                        + "".join(traceback.format_exception(None, e, e.__traceback__))
                    )

    def process_general_message(self, msg):
        """
        Callback function for general message processing.
        """
        # Send an ACK for the received message
        self.send_ack(msg.id, is_extended=msg.extended)

        if isinstance(msg, RemoteTransmissionRequest):
            return self.handle_remote_transmission_request(msg)
        elif msg.id == self.MESSAGE_IDS["FAULT_ID"]:
            return {"type": "FAULT", "content": msg.data}
        elif msg.id == self.MESSAGE_IDS["SOT_ID"]:
            self.handle_sot_message(msg)
        elif msg.id == self.MESSAGE_IDS["EOT_ID"]:
            self.handle_eot_message(msg)
        elif msg.extended:
            self.handle_multi_message(msg)
        else:
            self.handle_single_message(msg)
        return None

    def send_ack(self, msg_id, is_extended=False):
        """
        Sends an ACK message with the given message ID.
        Args:
            msg_id (int): The ID of the message to acknowledge.
            is_extended (bool): True if the message ID is an extended ID, False otherwise.
        """
        ack_data = b"ACK"  # ACK message content
        try:
            ack_message = Message(id=msg_id, data=ack_data, extended=is_extended)
            self.can_bus.send(ack_message)
            self.debug_print(f"Sent ACK for message ID: {hex(msg_id)}")
        except Exception as e:
            self.debug_print(
                "Error sending ACK: "
                + "".join(traceback.format_exception(None, e, e.__traceback__))
            )

    # =======================================================#
    # Receive Handler Functions                             #
    # =======================================================#

    def handle_remote_transmission_request(self, rtr):
        """
        Handles a Remote Transmission Request and returns RTR info.
        """
        # Implement handling of RTR
        self.debug_print("RTR length: " + str(rtr.length))
        # Example: Return RTR ID
        return {"type": "RTR", "id": rtr.id}

    def handle_multi_message(self, msg):
        """
        Handles a part of a multi-message sequence.
        """
        # Extract the original ID and the sequence number from the extended ID
        original_id = msg.id >> 22
        sequence_number = msg.id & 0x3FFFFF  # Mask to get the lower 22 bits

        self.debug_print(
            f"Received multi-message chunk for ID: {original_id} with sequence number: {sequence_number}"
        )

        if (
            str(original_id) in self.multi_message_buffer
            and not self.multi_message_buffer[str(original_id)]["is_complete"]
        ):
            # Store this chunk in the buffer
            self.multi_message_buffer[str(original_id)]["received_chunks"][
                sequence_number
            ] = msg.data

            # Check if all parts of the message have been received
            # This can be done based on your protocol's specifics
            if self.check_if_complete(original_id):
                complete_message = self.reassemble_message(original_id)
                # Process the complete message
                self.process_complete_message(original_id, complete_message)

        else:
            self.debug_print(
                f"Unexpected multi-message chunk received for ID: {original_id}"
            )

    def check_if_complete(self, original_id):
        """
        Checks if all parts of a multi-message sequence have been received.
        """
        # Implement logic to determine if all parts are received
        # This might involve checking sequence numbers, expected length, etc.
        buffer = self.multi_message_buffer[str(original_id)]
        return len(buffer["received_chunks"]) == buffer["expected_length"]

    def check_ack_message(self, msg):
        return msg.id if msg.data == b"ACK" else None

    def reassemble_message(self, original_id):
        """
        Reassembles all parts of a multi-message sequence into the complete message.
        """
        buffer = self.multi_message_buffer[str(original_id)]
        complete_message = b"".join(
            buffer["received_chunks"][seq] for seq in sorted(buffer["received_chunks"])
        )
        buffer["is_complete"] = True
        return complete_message

    def handle_single_message(self, msg):
        """
        Handles a single message. Pretty much only used for debug.
        """
        # Process a single, non-extended message
        self.debug_print(f"Received single message with ID: {msg.id}")
        self.debug_print(f"Message data: {msg.data}")

    def process_complete_message(self, original_id, message):
        """
        Processes the complete reassembled message.
        """
        # Implement your logic to handle the complete message
        self.debug_print(f"Received complete message for ID: {original_id}")
        self.debug_print(f"Message data: {message}")

    # =======================================================#
    # Wrapper Functions                                     #
    # =======================================================#

    def receive_ack_message(self):
        """
        Wrapper function to receive an ACK message.
        """
        return self.listen_on_can_bus(self.check_ack_message, timeout=1.0)

    def listen_messages(self, timeout=1.0):
        """
        Wrapper function to listen to general messages.
        """
        return self.listen_on_can_bus(self.process_general_message, timeout)

    # =======================================================#
    # Handshaking Functions                                 #
    # =======================================================#

    def send_sot(self, original_id, data_length):
        """
        Sends a Start-of-Transmission message with the expected data length.
        """
        sot_id = self.MESSAGE_IDS["SOT_ID"]

        # Combine the original_id and data_length into a single string, separated by a special character
        data = f"{original_id}:{data_length}"
        sot_message = Message(sot_id, data=bytes(data, "utf-8"), extended=False)

        try:
            self.can_bus.send(sot_message)
            self.debug_print(
                f"Sent SOT for ID: {sot_id} with data length: {data_length}"
            )
        except Exception as e:
            self.debug_print(
                "Error sending SOT: "
                + "".join(traceback.format_exception(None, e, e.__traceback__))
            )

        # Wait for ACK
        return self.wait_for_ack(sot_id, 1.0)

    def handle_sot_message(self, msg):
        """
        Processes the Start-of-Transmission (SOT) message.
        """
        # Extract the data length from the message
        try:
            original_id, data_length = msg.data.decode("utf-8").split(
                ":"
            )  # Assuming data is sent as a string
            data_length = int(data_length)
            self.debug_print(
                f"Received SOT for ID: {msg.id} with expected data length: {data_length}"
            )
        except ValueError:
            self.debug_print(f"Invalid data length format in SOT message: {msg.data}")
            return

        # Send ACK for SOT message
        self.send_ack(msg.id)

        # Initialize the buffer for the upcoming data stream

        if original_id not in self.multi_message_buffer:
            self.multi_message_buffer[original_id] = {
                "expected_length": data_length,
                "received_chunks": {},
                "is_complete": False,
            }
        else:
            # Reset the buffer if it already exists for this ID
            self.multi_message_buffer[original_id]["expected_length"] = data_length
            self.multi_message_buffer[original_id]["received_chunks"].clear()
            self.multi_message_buffer[original_id]["is_complete"] = False

        self.debug_print(f"Initialized buffer for multi-message ID: {original_id}")

    def send_eot(self):
        """
        Sends an End-of-Transmission message.
        """
        eot_id = self.MESSAGE_IDS["EOT_ID"]

        eot_message = Message(eot_id, data=b"EOT", extended=False)
        try:
            self.can_bus.send(eot_message)
            self.debug_print(f"Sent EOT for ID: {eot_id}")
        except Exception as e:
            self.debug_print(
                "Error sending EOT: "
                + "".join(traceback.format_exception(None, e, e.__traceback__))
            )

    def handle_eot_message(self, msg):
        """
        Processes the End-of-Transmission message.
        """
        original_id = msg.id  # Assuming the original ID is used in the EOT message

        # Validate the EOT message

        # Perform any cleanup or final processing

        # Send ACK for the EOT message
        self.send_ack(msg.id)

        self.debug_print(f"Processed EOT for ID: {original_id}")

    # =======================================================#
    # File Transfer Functions                               #
    # =======================================================#

    def send_rtr_and_receive(self, rtr_id, timeout=5.0):
        """
        Sends an RTR and waits for a response, which could be either single or multi-message.
        """
        # Send RTR
        rtr_message = RemoteTransmissionRequest(id=rtr_id)
        try:
            self.can_bus.send(rtr_message)
            self.debug_print(f"Sent RTR with ID: {hex(rtr_id)}")
        except Exception as e:
            self.debug_print(
                "Error sending RTR: "
                + "".join(traceback.format_exception(None, e, e.__traceback__))
            )
            return None

        # Listen for responses
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            response = self.receive_response()
            if response:
                # Process response
                if response["type"] == "SINGLE":
                    return response["data"]  # Return single message data
                elif response["type"] == "MULTI":
                    # Handle multi-message sequence
                    # You can either wait for the full sequence here or return and handle it elsewhere
                    pass

        return None

    def receive_response(self):
        """
        Listens for a single message or the start of a multi-message sequence.
        """
        msg = self.can_bus.receive()
        if msg:
            if msg.extended:
                # Start of a multi-message sequence
                self.handle_multi_message(msg)
                return {"type": "MULTI"}
            else:
                # Single message response
                return {"type": "SINGLE", "data": msg.data}
        return None

    def request_file(self, file_id, timeout=5.0):
        # Code from request_file goes here
        rtr = RemoteTransmissionRequest(id=file_id)
        self.can_bus.send(rtr)

        file_data = bytearray()
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError("No response received for file request")
            msg = self.can_bus.receive()
            if msg is None:
                continue
            if isinstance(msg, Message) and msg.id == file_id:
                if msg.data == b"start":
                    continue
                elif msg.data == b"stop":
                    break
                else:
                    file_data.extend(msg.data)
        return file_data
