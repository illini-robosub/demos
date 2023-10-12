"""
Handles I/O for quitting the server/client programs.

Uses basic synchronization techniques to demonstrate how they work in Python. Not required because of the Global Interpretor Lock (GIL).
On the use of `blocking=True`, we are using the spinlock paradigm. Look into the linux kernel if you're interested.
Also uses `global` variables which is BAD practice! Use a class to encapsulate all the state.

October 12th 2023
Eric Roth
"""

import threading
from threading import Thread

from sshkeyboard import listen_keyboard, stop_listening


# Global state
quit_thread: Thread = None
quit_lock = threading.Lock()
quit = 0

def get_quit():
    """
    Allows other files to access the quit variable (w/ necessary synchronization)
    """
    global quit

    quit_lock.acquire(blocking=True)
    ret = quit
    quit_lock.release()
    return ret

def on_key_press(key):
    """
    Handler for pressing a key on the keyboard
    """
    global quit

    # Check if `enter` character is pressed
    if key == '`':
        quit_lock.acquire(blocking=True)
        quit = 1
        quit_lock.release()

def on_key_release(key):
    """
    Handler for releasing a key on the keyboard
    """
    return

def initialize_keyboard():
    """
    Initializes the keyboard thread
    """
    global quit_thread

    quit_thread = Thread(target=listen_keyboard, daemon=True, kwargs={"on_press": on_key_press, "on_release": on_key_release, "sleep": 0.01})
    quit_thread.start()

def destroy_keyboard():
    """
    Cleans up the keyboard
    """
    global quit_thread

    stop_listening()
    quit_thread.join()

if __name__ == "__main__":
    """
    Sample program which demonstartes use of the keyboard handler.
    """
    initialize_keyboard()

    while True:
        q = get_quit()
        if q:
            break

    destroy_keyboard()
    print("Quit the program!")