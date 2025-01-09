class PacketReceiver:
    def __init__(self, radio, packet_manager, receive_delay=1.0):
        """
        Initialize the packet receiver

        Args:
            radio: The radio object for receiving
            packet_manager: Instance of PacketManager
            receive_delay: Delay between receive attempts (default 1.0 seconds)
        """
        self.radio = radio
        self.pm = packet_manager
        self.receive_delay = receive_delay
        self.reset()

    def reset(self):
        """Reset the receiver state"""
        self.received_packets = {}
        self.total_packets = None
        self.start_time = None

    def process_packet(self, packet):
        """Process a single received packet"""
        print(f"\nProcessing packet of length: {len(packet)}")
        print(f"Header bytes: {[hex(b) for b in packet[:4]]}")

        if self.pm.is_ack_packet(packet):
            print("Packet is an ACK packet, skipping")
            return False, None

        try:
            seq_num = int.from_bytes(packet[:2], "big")
            packet_total = int.from_bytes(packet[2:4], "big")
            print(f"Decoded - Sequence: {seq_num}, Total packets: {packet_total}")

            if self.total_packets is None:
                self.total_packets = packet_total
                print(f"Set total expected packets to: {self.total_packets}")
            elif packet_total != self.total_packets:
                print(
                    f"Warning: Packet indicates different total ({packet_total}) than previously recorded ({self.total_packets})"
                )

            # Store packet and send ACK if it's new
            if seq_num not in self.received_packets:
                self.received_packets[seq_num] = packet
                print(f"Stored new packet {seq_num}")
                self.send_ack(seq_num)
            else:
                print(f"Duplicate packet {seq_num}, resending ACK")
                self.send_ack(seq_num)

            # Check if we have all packets
            if (
                self.total_packets is not None
                and len(self.received_packets) == self.total_packets
                and all(i in self.received_packets for i in range(self.total_packets))
            ):
                print("All packets received!")
                return True, seq_num

            missing = self.get_missing_packets()
            print(f"Missing packets: {missing}")
            return False, seq_num

        except Exception as e:
            print(f"Error processing packet: {e}")
            import traceback

            traceback.print_exc()
            return False, None

    def send_ack(self, seq_num, num_acks=3, ack_delay=0.1):
        """
        Send multiple acknowledgments for a packet with delays

        Args:
            seq_num: Sequence number to acknowledge
            num_acks: Number of ACKs to send
            ack_delay: Delay between ACKs
        """
        import time

        ack = self.pm.create_ack_packet(seq_num)

        for i in range(num_acks):
            print(f"Sending ACK {i+1}/{num_acks} for packet {seq_num}")
            self.radio.send(ack, keep_listening=True)
            if i < num_acks - 1:  # Don't delay after last ACK
                time.sleep(ack_delay)

    def get_missing_packets(self):
        """Return list of missing packet sequence numbers"""
        if self.total_packets is None:
            return []
        return [i for i in range(self.total_packets) if i not in self.received_packets]

    def receive_until_complete(self, timeout=30.0):
        """
        Receive packets until complete message received or timeout

        Args:
            timeout: Total time to wait for complete message

        Returns:
            Tuple of (success, data, stats)
        """
        import time

        print("\nStarting receiver...")
        self.reset()
        self.start_time = time.monotonic()

        stats = {
            "packets_received": 0,
            "duplicate_packets": 0,
            "invalid_packets": 0,
            "time_elapsed": 0,
            "receive_attempts": 0,
        }

        while True:
            current_time = time.monotonic()

            # Check timeout
            if current_time - self.start_time > timeout:
                print("\nTimeout reached")
                print(f"Final state: {len(self.received_packets)} packets received")
                if self.total_packets is not None:
                    print(f"Missing packets: {self.get_missing_packets()}")
                stats["time_elapsed"] = current_time - self.start_time
                return False, None, stats

            # Single receive attempt with delay
            stats["receive_attempts"] += 1
            packet = self.radio.receive()
            print(packet)  # This print helps with radio timing/synchronization

            if packet:
                print(f"\nReceived packet of length: {len(packet)}")
                print(f"Raw packet bytes: {[hex(b) for b in packet[:8]]}")

                current_packet_count = len(self.received_packets)
                is_complete, seq_num = self.process_packet(packet)

                # Update statistics
                if seq_num is not None:
                    if len(self.received_packets) > current_packet_count:
                        stats["packets_received"] += 1
                        print(
                            f"New packet received, total: {stats['packets_received']}"
                        )
                    else:
                        stats["duplicate_packets"] += 1
                        print(
                            f"Duplicate packet received, total: {stats['duplicate_packets']}"
                        )
                else:
                    stats["invalid_packets"] += 1
                    print(f"Invalid packet received, total: {stats['invalid_packets']}")

                if is_complete:
                    print("Reception complete!")
                    stats["time_elapsed"] = time.monotonic() - self.start_time
                    return True, self.get_received_data(), stats

            # Delay between attempts for radio synchronization
            time.sleep(self.receive_delay)

            # Status update every N attempts
            updates_per_minute = 12  # About every 5 seconds with 1-second delay
            if stats["receive_attempts"] % (updates_per_minute) == 0:
                print(
                    f"\nWaiting for packets... Time remaining: {round(timeout - (current_time - self.start_time), 1)} seconds"
                )
                print(f"Receive attempts: {stats['receive_attempts']}")
                if self.total_packets is not None:
                    print(
                        f"Have {len(self.received_packets)}/{self.total_packets} packets"
                    )
                    print(f"Missing packets: {self.get_missing_packets()}")

    def send_retransmit_request(self, missing_packets):
        """Send request for missing packets with adjusted timing"""
        import time

        print(f"\nRequesting retransmission of {len(missing_packets)} packets")

        request = self.pm.create_retransmit_request(missing_packets)
        retransmit_timeout = max(10, len(missing_packets) * 1.0)  # Longer timeout

        # Send request multiple times with longer gaps
        for i in range(2):  # Reduced to 2 attempts to avoid flooding
            print(f"Sending retransmit request attempt {i+1}/2")
            self.radio.send(request, keep_listening=True)
            time.sleep(0.2)

        # Wait for retransmitted packets
        start_time = time.monotonic()
        original_missing = set(missing_packets)
        # last_receive_time = start_time

        print("Waiting for retransmitted packets...")
        while time.monotonic() - start_time < retransmit_timeout:
            packet = self.radio.receive(keep_listening=True)
            print(packet)
            time.sleep(0.5)

            if packet:
                # last_receive_time = time.monotonic()
                try:
                    seq_num = int.from_bytes(packet[:2], "big")
                    if seq_num in original_missing:
                        self.received_packets[seq_num] = packet
                        original_missing.remove(seq_num)
                        print(f"Successfully received retransmitted packet {seq_num}")
                        print(f"Still missing: {list(original_missing)}")

                        if not original_missing:
                            print("All requested packets received!")
                            return True
                except Exception as e:
                    print(f"Error processing retransmitted packet: {e}")

        remaining = list(original_missing)
        if remaining:
            print(f"Retransmission incomplete. Still missing: {remaining}")
        return False

    def fast_receive_until_complete(
        self, timeout=30.0, idle_timeout=5, max_retransmit_attempts=3
    ):
        """
        Fast receive with automatic retransmission after idle period

        Args:
            timeout: Total time to wait for complete message
            idle_timeout: Time to wait with no new packets before requesting retransmit
            max_retransmit_attempts: Maximum number of retransmit attempts
        """
        import time

        print("\nStarting fast receiver...")
        self.reset()
        self.start_time = time.monotonic()
        last_packet_time = time.monotonic()

        stats = {
            "packets_received": 0,
            "duplicate_packets": 0,
            "invalid_packets": 0,
            "time_elapsed": 0,
            "retransmit_rounds": 0,
        }

        # First, wait for and ACK the initial packet
        while True:
            if time.monotonic() - self.start_time > timeout:
                return False, None, stats

            packet = self.radio.receive()
            print(packet)

            if packet:
                try:
                    last_packet_time = time.monotonic()
                    seq_num = int.from_bytes(packet[:2], "big")
                    self.total_packets = int.from_bytes(packet[2:4], "big")

                    if seq_num == 0:  # First packet
                        print(
                            f"Received first packet. Expecting {self.total_packets} total packets"
                        )
                        self.received_packets[0] = packet
                        stats["packets_received"] += 1
                        self.send_ack(0)  # ACK only the first packet
                        break
                except Exception as e:
                    print(f"Error processing first packet: {e}")

            time.sleep(self.receive_delay)

        # Now receive remaining packets without ACKs
        print("Receiving remaining packets...")
        receive_end_time = time.monotonic() + timeout

        while time.monotonic() < receive_end_time:
            current_time = time.monotonic()

            packet = self.radio.receive()
            print(packet)

            if packet:
                try:
                    seq_num = int.from_bytes(packet[:2], "big")
                    # packet_total = int.from_bytes(packet[2:4], "big")

                    if seq_num not in self.received_packets:
                        self.received_packets[seq_num] = packet
                        stats["packets_received"] += 1
                        print(f"Received packet {seq_num}/{self.total_packets}")
                        last_packet_time = current_time  # Update last packet time
                    else:
                        stats["duplicate_packets"] += 1

                    # Check if we have all packets
                    if len(self.received_packets) == self.total_packets:
                        if all(
                            i in self.received_packets
                            for i in range(self.total_packets)
                        ):
                            print("All packets received!")
                            stats["time_elapsed"] = time.monotonic() - self.start_time
                            return True, self.get_received_data(), stats

                except Exception as e:
                    stats["invalid_packets"] += 1
                    print(f"Error processing packet: {e}")

            time.sleep(self.receive_delay)

            # Print status every 10 packets
            if stats["packets_received"] % 10 == 0:
                missing = self.get_missing_packets()
                print(f"Have {len(self.received_packets)}/{self.total_packets} packets")
                print(f"Missing: {missing}")
                # Check if we've been idle too long
            if current_time - last_packet_time > idle_timeout:
                missing = self.get_missing_packets()
                if missing:
                    print(f"\nNo packets received for {idle_timeout} seconds")
                    print(f"Missing {len(missing)} packets: {missing}")

                    if stats["retransmit_rounds"] < max_retransmit_attempts:
                        stats["retransmit_rounds"] += 1
                        print(
                            f"Requesting retransmission (attempt {stats['retransmit_rounds']}/{max_retransmit_attempts})"
                        )

                        if self.send_retransmit_request(missing):
                            print("Retransmission successful!")
                            if not self.get_missing_packets():
                                return True, self.get_received_data(), stats
                        else:
                            print("Retransmission failed")

                        # Reset idle timer after retransmit attempt
                        last_packet_time = current_time
                    else:
                        print(
                            f"Max retransmit attempts ({max_retransmit_attempts}) reached"
                        )
                        break

        # Final retransmit attempt if needed
        missing = self.get_missing_packets()
        if missing:
            print(f"\nTransfer incomplete. Missing {len(missing)} packets")
            print(f"Missing packet numbers: {missing}")
            stats["time_elapsed"] = time.monotonic() - self.start_time
            return False, None, stats
        else:
            print("\nTransfer complete!")
            stats["time_elapsed"] = time.monotonic() - self.start_time
            return True, self.get_received_data(), stats

    def get_received_data(self):
        """
        Attempt to reassemble and return received data

        Returns:
            Reassembled data if complete, None if incomplete
        """
        if not self.received_packets or self.total_packets is None:
            return None

        if len(self.received_packets) != self.total_packets:
            return None

        packets_list = [self.received_packets[i] for i in range(self.total_packets)]
        return self.pm.unpack_data(packets_list)
