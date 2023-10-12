"""
Simple demonstration of Mavlink communication using Pymavlink.

NOTE: Launch BEFORE `client.py`

October 12th 2023
Eric Roth
"""

import os
import time
from threading import Thread

from pymavlink import mavutil
import pymavlink.dialects.v20.ardupilotmega as dialect

import keyboard_handler

# Set Mavlink2 as our default
os.environ['MAVLINK20'] = '1'

# File constants
HEARTBEAT_INTERVAL = 1

def heartbeat(server: mavutil.mavfile):
    """
    Sends 1 [s] spaced heartbeats to the vehicle
    """
    mav: dialect.MAVLink = server.mav
    last_beat = 0

    # 1 [s] loop
    while True:
        loop_time = time.perf_counter()

        # Check to make sure it's actually time to send
        if loop_time - last_beat >= HEARTBEAT_INTERVAL:
            mav.heartbeat_send(dialect.MAV_TYPE_GCS, dialect.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            last_beat = time.perf_counter()

        # Sleep until next heartbeat      
        time.sleep(HEARTBEAT_INTERVAL - (last_beat - loop_time))

def get_new_messages(client: mavutil.mavfile):
    """
    Clears out the message buffer and returns a list of messages
    """
    msgs = []
    while True:
        msg: dialect.MAVLink_message = client.recv_msg()

        if msg is None:
            break

        msgs.append(msg)

    return msgs  

def main():
    print("Opening up server connection...")

    # Listen for incoming UDP connection on localhost port 14550
    server: mavutil.mavfile = mavutil.mavlink_connection('tcpin:127.0.0.1:14550', dialect="ardupilotmega", autoreconnect=True)

    # Confirm the connection is valid
    server.wait_heartbeat()

    # Print out vehicle information
    print("Heartbeat from system (system %u component %u)" % (server.target_system, server.target_component))

    # Set up the heartbeat thread
    heartbeat_thread = Thread(target=heartbeat, daemon=True, args=(server,))
    heartbeat_thread.start()

    # Initialize the keyboard handler
    keyboard_handler.initialize_keyboard()

    # Server loop
    print("Press [`] to quit the client!")
    while True:
        # Check any incoming messages
        new_msgs = get_new_messages(server)

        # Print any new messages to the terminal
        for msg in new_msgs:
            msg: dialect.MAVLink_message # Type hinting
            print(f"Received message of type {msg.get_type()}...")
            print(msg)

        # Check 
        quit = keyboard_handler.get_quit()
        if quit:
            break

    # Destroy the keyboard
    keyboard_handler.destroy_keyboard()

    # No need to join the heartbeat thread as we declared it a daemon thread earlier (i.e. it stops running when the main thread stops)

    print("Shutting down...")

if __name__ == "__main__":
    main()