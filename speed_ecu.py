#!/usr/bin/env python3
"""
speed sensor ECU simulator
simulates vehicle speed message on CAN bus
"""
import can
import time
import random
bus=can.interface.Bus(channel="vcan0",bustype="socketcan")
speed_id=0x1A0
max_speed=80
interval=0.5
print("speed sensor ECU started")
print(f"sending on CAN id:{hex(speed_id)}")
print(f"max speed:{max_speed} km/h")
print(f"interval:{interval} seconds")
print("press ctrl+c to stop")
try: 
    while True:
        speed=random.randint(0,max_speed)
        msg=can.Message(
           arbitration_id=speed_id,
           data=[speed],
           is_extended_id=False
        )
        bus.send(msg)
        print(f"sent:{hex(speed_id)} [{speed:3d} km/h]")
        time.sleep(interval)
except KeyboardInterrupt:
    print("\n speed sensor ECU stopped!")
    bus.shutdown()


