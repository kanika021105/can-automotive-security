import can
import time
from datetime import datetime
bus=can.interface.Bus(channel='vcan0',bustype='socketcan')
timestamp=datetime.now().strftime('%Y%m%d_%H%M%S')
filename=f"can_log_{timestamp}.txt"
log_file=open(filename,'w')
print(f"CAN sniffer started!")
print(f"saving to:{filename}")
print(f"press ctrl+c to stop\n")
message_count=0
try:
    while True:
        msg=bus.recv(timeout=1.0)
        if msg is not None: 
            message_count+=1
            current_time= datetime.now().strftime('%H:%M:%S.%f') [:-3]
            data_hex=' '.join(f'{b:02X}' for b in msg.data)
            log_line=f"{current_time} {hex(msg.arbitration_id)} [{len(msg.data)}] {data_hex}\n"
            print(f"{message_count}:{log_line.strip()}")
            log_file.write(log_line)
            log_file.flush()
except KeyboardInterrupt:
    print(f"\n\n capture complete!")
    print(f"total messages:{message_count}")
    print(f"saved to:{filename}")
    log_file.close()
    bus.shutdown()
