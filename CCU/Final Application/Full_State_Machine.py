# Import Statements
import threading
import time 
import sys
import random
from Settings import *

# Overall CCU Functions
def scan_for_devices(): # TODO
    print("Searching for HUD")
    time.sleep(0.5)
    print("HUD found")
    time.sleep(0.5)
    print("Searching for Stick")
    time.sleep(0.5)
    print("Stick found")
    time.sleep(0.5)
    print("Searching for Glove")
    time.sleep(0.5)
    print("Glove found")
    return

def set_impaired():
    print("Asking if user is impaired")
    time.sleep(1)
    user_impaired = False # TODO: remove with actual setting
    return

def game_mode():
    print("Entered game mode")
    time.sleep(5)
    print("Exiting game mode")
    return

def training_mode():
    print("Entered training mode")
    time.sleep(5)
    print("Exiting game mode")
    return

def on_disconnect(): # TODO
    return

# HUD Interactions
def connect_to_hud(): # TODO
    return

def receive_image(): # TODO
    return

def computer_vision(): # TODO
    return

# Cue Stick
def connect_to_stick(): # TODO
    return

def on_new_acc_stick(): # TODO
    return

def on_new_roll_stick(): # TODO
    return

def on_new_pitch_stick(): # TODO
    return

def on_new_yaw_stick(): # TODO
    return

def on_new_button_stick():
    return

def on_new_fms():
    return

# Glove
def connect_to_glove():
    return

def on_new_dist_glove():
    return

def on_new_yaw_glove():
    return

if __name__ == '__main__':
    # Connect to all peripherals
    print("Connecting to all peripherals")
    scan_for_devices()
    print("Successfully connected")

    # Determine blind vs not blind
    print("Setting (not) blind")
    set_impaired()
    print("Ableness set")

    # Determine Game Mode VS Training Mode

    # Normal Operation
    if operation_mode == OperatingMode.GAME:
        print("Entering game mode")
        game_mode()
    elif operation_mode == OperatingMode.TRAINING:
        print("Entering training mode")
        training_mode()
    else:
        print("IDK how we got here")

    print("Finished")