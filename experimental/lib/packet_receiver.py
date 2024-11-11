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
            seq_num = int.from_bytes(packet[:2], 'big')
            packet_total = int.from_bytes(packet[2:4], 'big')
            print(f"Decoded - Sequence: {seq_num}, Total packets: {packet_total}")
            
            if self.total_packets is None:
                self.total_packets = packet_total
                print(f"Set total expected packets to: {self.total_packets}")
            elif packet_total != self.total_packets:
                print(f"Warning: Packet indicates different total ({packet_total}) than previously recorded ({self.total_packets})")
                
            # Store packet and send ACK if it's new
            if seq_num not in self.received_packets:
                self.received_packets[seq_num] = packet
                print(f"Stored new packet {seq_num}")
                self.send_ack(seq_num)
            else:
                print(f"Duplicate packet {seq_num}, resending ACK")
                self.send_ack(seq_num)
                
            # Check if we have all packets
            if (self.total_packets is not None and 
                len(self.received_packets) == self.total_packets and 
                all(i in self.received_packets for i in range(self.total_packets))):
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
            self.radio.send(ack)
            if i < num_acks - 1:  # Don't delay after last ACK
                time.sleep(ack_delay)
        
    def get_missing_packets(self):
        """Return list of missing packet sequence numbers"""
        if self.total_packets is None:
            return []
        return [i for i in range(self.total_packets) 
                if i not in self.received_packets]
        
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
            'packets_received': 0,
            'duplicate_packets': 0,
            'invalid_packets': 0,
            'time_elapsed': 0,
            'receive_attempts': 0
        }
        
        while True:
            current_time = time.monotonic()
            
            # Check timeout
            if current_time - self.start_time > timeout:
                print("\nTimeout reached")
                print(f"Final state: {len(self.received_packets)} packets received")
                if self.total_packets is not None:
                    print(f"Missing packets: {self.get_missing_packets()}")
                stats['time_elapsed'] = current_time - self.start_time
                return False, None, stats
            
            # Single receive attempt with delay
            stats['receive_attempts'] += 1
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
                        stats['packets_received'] += 1
                        print(f"New packet received, total: {stats['packets_received']}")
                    else:
                        stats['duplicate_packets'] += 1
                        print(f"Duplicate packet received, total: {stats['duplicate_packets']}")
                else:
                    stats['invalid_packets'] += 1
                    print(f"Invalid packet received, total: {stats['invalid_packets']}")
                    
                if is_complete:
                    print("Reception complete!")
                    stats['time_elapsed'] = time.monotonic() - self.start_time
                    return True, self.get_received_data(), stats
            
            # Delay between attempts for radio synchronization
            time.sleep(self.receive_delay)
            
            # Status update every N attempts
            updates_per_minute = 12  # About every 5 seconds with 1-second delay
            if stats['receive_attempts'] % (updates_per_minute) == 0:
                print(f"\nWaiting for packets... Time remaining: {round(timeout - (current_time - self.start_time), 1)} seconds")
                print(f"Receive attempts: {stats['receive_attempts']}")
                if self.total_packets is not None:
                    print(f"Have {len(self.received_packets)}/{self.total_packets} packets")
                    print(f"Missing packets: {self.get_missing_packets()}")

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
            
        packets_list = [self.received_packets[i] 
                       for i in range(self.total_packets)]
        return self.pm.unpack_data(packets_list)