import can
import time
import random
bus= can.interface.Bus(channel='vcan0',bustype='socketcan')
print("turn signal ECU started! sending messages....")
print("Press ctrl+c to stop\n")

TURN_SIGNAL_ID = 0x210
LEFT=0x01
RIGHT=0x02
BOTH=0x03
OFF=0x00

try:
    while True:
        state = random.choice([LEFT,RIGHT,BOTH,OFF])
        msg = can.Message(
            arbitration_id=TURN_SIGNAL_ID,
            data=[state],
            is_extended_id=False
        )
        
        bus.send(msg)
        state_names={
            LEFT:"LEFT",
            RIGHT:"RIGHT",
            BOTH:"BOTH(HAZARD)",
            OFF:"OFF",
        }
        print(f"Sent:CAN ID {hex(TURN_SIGNAL_ID)}->{state_names.get(state,'UNKNOWN')}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n Turn signal ECU stopped")
    bus.shutdown()
