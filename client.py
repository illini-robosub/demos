"""
Simple demonstration of Mavlink communication using Pymavlink.
Gives a simple example of a Python thread which sends heartbeats to the server.

NOTE: Launch AFTER `server.py` 

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

def heartbeat(client: mavutil.mavfile):
    """
    Sends 1 [s] spaced heartbeats to the vehicle
    """
    mav: dialect.MAVLink = client.mav
    last_beat = 0

    # 1 [s] loop
    while True:
        loop_time = time.perf_counter()

        # Check to make sure it's actually time to send
        if loop_time - last_beat >= HEARTBEAT_INTERVAL:
            mav.heartbeat_send(dialect.MAV_TYPE_SUBMARINE, dialect.MAV_AUTOPILOT_INVALID, 0, 0, 0)
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
    print("Establishing connection to the server...")

    # Connect to the server on localhost port 14550
    client: mavutil.mavfile = mavutil.mavlink_connection('tcp:127.0.0.1:14550', dialect="ardupilotmega", autoreconnect=True)

    print("Connected!")

    # Set up the heartbeat thread
    heartbeat_thread = Thread(target=heartbeat, daemon=True, args=(client,))
    heartbeat_thread.start()

    # Set up the keyboard handler
    keyboard_handler.initialize_keyboard()

    # Client loop
    print("Press [`] to quit the client!")
    while True:
        # Check any incoming messages
        new_msgs = get_new_messages(client)

        # Print any new messages to the terminal
        for msg in new_msgs:
            msg: dialect.MAVLink_message # Type hinting
            print(f"Received message of type {msg.get_type()}...")
            print(msg)
        
        # Check any keyboard input
        quit = keyboard_handler.get_quit()
        if quit:
            break

    # Shut down the keyboard
    keyboard_handler.destroy_keyboard()

    # No need to join the heartbeat thread as we declared it a daemon thread earlier (i.e. it stops running when the main thread stops)

    print("Shutting down...")

if __name__ == "__main__":
    main()