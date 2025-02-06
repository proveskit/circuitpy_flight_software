from lib.pysquared.logger import Logger


class PacketSender:
    def __init__(
        self,
        logger: Logger,
        radio,
        packet_manager,
        ack_timeout=2.0,
        max_retries=3,
        send_delay=0.2,
    ):
        """
        Initialize the packet sender with optimized timing
        """
        self.logger = logger
        self.radio = radio
        self.packet_manager = packet_manager
        self.ack_timeout = ack_timeout
        self.max_retries = max_retries
        self.send_delay = send_delay

    def wait_for_ack(self, expected_seq):
        """
        Optimized ACK wait with early return
        """
        import time

        start_time = time.monotonic()

        # Minimal delay after sending
        time.sleep(self.send_delay)

        while (time.monotonic() - start_time) < self.ack_timeout:
            packet = self.radio.receive()

            if packet and self.packet_manager.is_ack_packet(packet):
                ack_seq = self.packet_manager.get_ack_seq_num(packet)
                if ack_seq == expected_seq:
                    # Got our ACK - only wait briefly for a duplicate then continue
                    time.sleep(0.2)
                    return True

            time.sleep(0.1)  # Small delay between checks

        return False

    def send_packet_with_retry(self, packet, seq_num):
        """Optimized packet sending with minimal delays"""
        import time

        for attempt in range(self.max_retries):
            self.radio.send(packet)

            if self.wait_for_ack(seq_num):
                # Success - minimal delay before next packet
                time.sleep(0.2)
                return True

            if attempt < self.max_retries - 1:
                # Only short delay before retry
                time.sleep(1.0)

        return False

    def send_data(self, data, progress_interval=10):
        """Send data with minimal progress updates"""
        packets = self.packet_manager.pack_data(data)
        total_packets = len(packets)
        self.logger.info("Sending packets...", num_packets=total_packets)

        for i, packet in enumerate(packets):
            if i % progress_interval == 0:
                self.logger.info(
                    "Making progress sending packets",
                    current_packet=i,
                    num_packets=total_packets,
                )

            if not self.send_packet_with_retry(packet, i):
                self.logger.warning(
                    "Failed to send packet", current_packet=i, num_packets=total_packets
                )
                return False

        self.logger.info(
            "Successfully sent all the packets!", num_packets=total_packets
        )
        return True

    def handle_retransmit_request(self, packets, request_packet):
        """Handle retransmit request by sending requested packets"""
        import time

        try:
            missing_packets = self.packet_manager.parse_retransmit_request(
                request_packet
            )
            self.logger.info(
                "Retransmit request received for missing packets",
                num_missing_packets=len(missing_packets),
            )
            time.sleep(0.2)  # Small delay before retransmission

            for seq in missing_packets:
                if seq < len(packets):
                    self.logger.info("Retransmitting packet ", packet=seq)
                    self.radio.send(packets[seq])
                    time.sleep(0.2)  # Small delay between retransmitted packets
                    self.radio.send(packets[seq])
                    time.sleep(0.2)  # Small delay between retransmitted packets

            return True

        except Exception as e:
            self.logger.error("Error handling retransmit request", err=e)
            return False

    def fast_send_data(self, data, send_delay=0.5, retransmit_wait=15.0):
        """Send data with improved retransmission handling"""
        import time

        packets = self.packet_manager.pack_data(data)
        total_packets = len(packets)
        self.logger.info("Sending packets..", num_packets=total_packets)

        # Send first packet with retry until ACKed
        for attempt in range(self.max_retries):
            self.logger.info(
                "Sending first packet",
                attempt_num=attempt + 1,
                max_retries=self.max_retries,
            )
            self.radio.send(packets[0])

            if self.wait_for_ack(0):
                break
            else:
                if attempt < self.max_retries - 1:
                    time.sleep(1.0)
                else:
                    self.logger.warning("Failed to get ACK for first packet")
                    return False

        # Send remaining packets without waiting for ACKs
        self.logger.info("Sending remaining packets...")
        for i in range(1, total_packets):
            if i % 10 == 0:
                self.logger.info(
                    "Sending packet", current_packet=i, num_packets=total_packets
                )
            self.radio.send(packets[i])
            time.sleep(send_delay)

        self.logger.info("Waiting for retransmit requests...")
        retransmit_end_time = time.monotonic() + retransmit_wait

        while time.monotonic() < retransmit_end_time:
            packet = self.radio.receive()
            if not packet:
                break

            self.logger.info(
                "Received potential retransmit request:",
                packet=[hex(b) for b in packet],
            )

            if not self.packet_manager.is_retransmit_request(packet):
                break

            self.logger.info("Valid retransmit request received!")
            missing_packets = self.packet_manager.parse_retransmit_request(packet)
            self.logger.info("Retransmitting packets", missing_packets=missing_packets)

            # Add delay before retransmission to let receiver get ready
            time.sleep(1)

            for seq in missing_packets:
                if seq >= len(packets):
                    break

                self.logger.info("Retransmitting packet", packet=seq)
                self.radio.send(packets[seq])
                time.sleep(0.5)  # Longer delay between retransmitted packets
                self.logger.info("Retransmitting packet", packet=seq)
                self.radio.send(packets[seq])
                time.sleep(0.2)  # Longer delay between retransmitted packets

            # Reset timeout and add extra delay after retransmission
            time.sleep(1.0)
            retransmit_end_time = time.monotonic() + retransmit_wait

            time.sleep(0.1)

        self.logger.info("Finished sending all packets")
        return True
