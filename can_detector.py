#!/usr/bin/env python3
"""
CAN Bus Replay Attack Detector - Version 2
Detects repeated message sequences (replay attacks)
"""

import can
import time
from datetime import datetime
from collections import deque

# Connection to CAN bus
bus = can.interface.Bus(channel='vcan0', interface='socketcan')

# Detection settings
WINDOW_SIZE = 10          # Number of messages to analyze for patterns
SEQUENCE_LENGTH = 4       # Length of sequence to check for repetition
REPETITION_THRESHOLD = 2  # How many times the sequence must repeat to trigger alert

# Store recent messages
message_history = deque(maxlen=WINDOW_SIZE * 2)
message_counter = 0

# Track sequences we've seen
seen_sequences = {}
replay_count = 0

print(" CAN Replay Attack Detector v2 Started!")
print(f" Analyzing sequences of {SEQUENCE_LENGTH} messages")
print(f" Alert after {REPETITION_THRESHOLD} repetitions")
print(" Press Ctrl+C to stop\n")

def extract_sequence(history, length):
    """Extract a sequence of messages as a tuple for comparison"""
    if len(history) < length:
        return None
    
    # Create a tuple of (CAN ID, data) for the last 'length' messages
    sequence = tuple(
        (msg.arbitration_id, bytes(msg.data)) 
        for msg in list(history)[-length:]
    )
    return sequence

try:
    while True:
        # Get next CAN message
        msg = bus.recv(timeout=1.0)
        
        if msg is not None:
            message_counter += 1
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Format message for display
            data_hex = ' '.join(f'{b:02X}' for b in msg.data)
            msg_str = f"{hex(msg.arbitration_id)} [{len(msg.data)}] {data_hex}"
            
            # Add to history
            message_history.append(msg)
            
            # Check for replay attack using sequence detection
            sequence = extract_sequence(message_history, SEQUENCE_LENGTH)
            
            if sequence is not None:
                if sequence in seen_sequences:
                    seen_sequences[sequence] += 1
                    count = seen_sequences[sequence]
                    
                    if count >= REPETITION_THRESHOLD:
                        replay_count += 1
                        print(f"🚨 REPLAY ATTACK DETECTED! 🚨")
                        print(f" Message #{message_counter} at {timestamp}")
                        print(f"  Suspicious message: {msg_str}")
                        print(f" Sequence repeated {count} times")
                        print(f" Sequence: {sequence}")
                        print("=" * 60)
                    else:
                        # Repetition detected but below threshold
                        print(f" #{message_counter} {timestamp} {msg_str} (repetition {count})")
                else:
                    # New sequence
                    seen_sequences[sequence] = 1
                    print(f"#{message_counter} {timestamp} {msg_str}")
            
except KeyboardInterrupt:
    print(f"\n\n Detection stopped after {message_counter} messages")
    print(f" Detected {replay_count} replay attacks")
    bus.shutdown()
    print(" SocketcanBus shut down properly")
