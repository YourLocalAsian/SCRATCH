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

def set_impaired(): # TODO
    global user_impaired

    print("Asking if user is impaired")
    time.sleep(1)
    user_impaired = False # TODO: remove with actual setting
    return

def set_operating_mode(): # TODO
    global operation_mode

    if user_impaired == True: # only option when blind mode is game mode
        operation_mode = OperatingMode.GAME
        print("User impaired - defaulting to Game Mode")
    else:
        # play audio cue for selection
        # get user response
        if BUTTON_CHAR_STICK_UUID == ButtonInput.A: # Press A = Game Mode # TODO: change this to value of characteristic
            operation_mode = OperatingMode.GAME
        elif BUTTON_CHAR_STICK_UUID == ButtonInput.B: # Press B = Training Mode
            operation_mode = OperatingMode.TRAINING

    operation_mode = OperatingMode.TRAINING # TODO: Force mode selection
    print("Forced mode:", operation_mode)

def game_mode_std(): # TODO
    print("Entered standard game mode")
    time.sleep(5)
    print("Exiting standard game mode")
    return

def game_mode_bld(): # TODO
    print("Entered blind game mode")
    time.sleep(5)
    print("Exiting blind game mode")
    return

def training_mode(): # TODO
    print("Entered training mode")
    time.sleep(5)
    print("Generating random PoC & power")
    time.sleep(5)
    print("Exiting training mode")
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
    print(f"Successfully connected\n")

    # Determine blind vs not blind
    print("Calling set_impaired()")
    set_impaired()
    print(f"Impairedness set:", user_impaired, "\n")

    # Determine Game Mode VS Training Mode
    print("Calling set_operating_mode()")
    set_operating_mode()
    print(f"Operating mode set:", operation_mode, "\n")

    # Normal Operation
    if operation_mode == OperatingMode.GAME:
        if user_impaired == False:
            print("Calling game_mode_std")
            game_mode_std()
        elif user_impaired == True:
            print("Calling game_mode_bld")
            game_mode_bld()
    elif operation_mode == OperatingMode.TRAINING:
        if user_impaired == False:
            print("Calling training mode")
            training_mode()
        elif user_impaired == True:
            print("Error - blind user cannot enter training mode")
    else:
        print("Error - IDK how we got here")

    print("Finished")