from lib.pysquared.logger import Logger


class PacketSender:
    def __init__(
        self, radio, packet_manager, ack_timeout=2.0, max_retries=3, send_delay=0.2
    ):
        """
        Initialize the packet sender with optimized timing
        """
        self.radio = radio
        self.pm = packet_manager
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

            if packet and self.pm.is_ack_packet(packet):
                ack_seq = self.pm.get_ack_seq_num(packet)
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

    def send_data(self, data, logger: Logger, progress_interval=10):
        """Send data with minimal progress updates"""
        packets = self.pm.pack_data(data)
        total_packets = len(packets)
        logger.info(f"Sending {total_packets} packets...")

        for i, packet in enumerate(packets):
            if i % progress_interval == 0:
                logger.info(f"Progress: {i}/{total_packets}")

            if not self.send_packet_with_retry(packet, i):
                logger.warning(f"Failed at packet {i}/{total_packets}")
                return False

        logger.info(f"Successfully sent {total_packets} packets!")
        return True

    def handle_retransmit_request(self, packets, request_packet, logger: Logger):
        """Handle retransmit request by sending requested packets"""
        import time

        try:
            missing_packets = self.pm.parse_retransmit_request(request_packet)
            logger.info(
                f"\nRetransmit request received for {len(missing_packets)} packets",
            )
            time.sleep(0.2)  # Small delay before retransmission

            for seq in missing_packets:
                if seq < len(packets):
                    logger.info(f"Retransmitting packet {seq}")
                    self.radio.send(packets[seq])
                    time.sleep(0.2)  # Small delay between retransmitted packets
                    self.radio.send(packets[seq])
                    time.sleep(0.2)  # Small delay between retransmitted packets

            return True

        except Exception as e:
            logger.error(f"Error handling retransmit request: {e}")
            return False

    def fast_send_data(
        self, data, logger: Logger, send_delay=0.5, retransmit_wait=15.0
    ):
        """Send data with improved retransmission handling"""
        import time

        packets = self.pm.pack_data(data)
        total_packets = len(packets)
        logger.info(f"Sending {total_packets} packets...")

        # Send first packet with retry until ACKed
        for attempt in range(self.max_retries):
            logger.info(
                f"Sending first packet (attempt {attempt + 1}/{self.max_retries})",
            )
            self.radio.send(packets[0])

            if self.wait_for_ack(0):
                break
            else:
                if attempt < self.max_retries - 1:
                    time.sleep(1.0)
                else:
                    logger.warning("Failed to get ACK for first packet")
                    return False

        # Send remaining packets without waiting for ACKs
        logger.info("Sending remaining packets...")
        for i in range(1, total_packets):
            if i % 10 == 0:
                logger.info(f"Sending packet {i}/{total_packets}")
            self.radio.send(packets[i])
            time.sleep(send_delay)

        logger.info("Waiting for retransmit requests...")
        retransmit_end_time = time.monotonic() + retransmit_wait

        while time.monotonic() < retransmit_end_time:
            packet = self.radio.receive()
            if packet:
                logger.info(
                    f"Received potential retransmit request: {[hex(b) for b in packet]}",
                )

                if self.pm.is_retransmit_request(packet):
                    logger.info("Valid retransmit request received!")
                    missing_packets = self.pm.parse_retransmit_request(packet)
                    logger.info(
                        f"Retransmitting packets: {missing_packets}",
                    )

                    # Add delay before retransmission to let receiver get ready
                    time.sleep(1)

                    for seq in missing_packets:
                        if seq < len(packets):
                            logger.info(
                                f"Retransmitting packet {seq}",
                            )
                            self.radio.send(packets[seq])
                            time.sleep(
                                0.5
                            )  # Longer delay between retransmitted packets
                            logger.info(
                                f"Retransmitting packet {seq}",
                            )
                            self.radio.send(packets[seq])
                            time.sleep(
                                0.2
                            )  # Longer delay between retransmitted packets

                    # Reset timeout and add extra delay after retransmission
                    time.sleep(1.0)
                    retransmit_end_time = time.monotonic() + retransmit_wait

            time.sleep(0.1)

        logger.info("Finished sending all packets")
        return True
