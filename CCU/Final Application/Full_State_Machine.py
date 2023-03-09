# Import Statements
import threading
import time 
import sys
import random
from Settings import *

# Setup Functions
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
    # play audio asking for impairness
    # wait for button notification
    user_impaired = False # TODO: remove with actual setting
    # play audio confirming choice
    time.sleep(1)
    
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

    operation_mode = OperatingMode.GAME # TODO: Force mode selection
    print("Forced mode:", operation_mode)

def on_disconnect(): # TODO
    return

# Game Mode Functions
def game_mode(angle, force): # Called continously until shot is completed
    debug_print = True
    
    if debug_print:
        print("Entered standard game mode")
    
    # Check if game completed
    if force > 100: # force is set to max value when game is completed 
        if debug_print:
            print("Game completed")
            time.sleep(1)
        return
    
    # Check if ongoing game
    elif force > 0: # force is positive during on going game
        # User Shot Attempt
        if debug_print:
            print("Calling standard user shot attempt")
            time.sleep(1)
    
    else: # force is negative when starting a game
        # Ensure connection to VISION has been established
        if debug_print:
            print("Connection to VISION verified")
            time.sleep(1)

    # Request next shot
    if debug_print:
        print("Asking VISION for next shot")
        time.sleep(1)

    # Wait for shot data
    if debug_print:
        print("Waiting for shot data")
        time.sleep(1)

    # Receive and parse shot data
    if debug_print:
        print("Shot data received")
    p_angle = 0
    p_force = 1
    
    # Make recursive call
    if debug_print:
        print("Making recursive call to game_mode_std()")
    
    game_mode(p_angle, p_force)

    return

# Training Mode Functions
def training_mode(): # TODO
    print("Entered training mode")
    time.sleep(5)
    print("Generating random PoC & power")
    time.sleep(5)
    print("Exiting training mode")
    return

# Shot Attempt Functions


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
            game_mode(0, -1)
        elif user_impaired == True:
            print("Calling game_mode_bld")
            game_mode()
    elif operation_mode == OperatingMode.TRAINING:
        if user_impaired == False:
            print("Calling training mode")
            training_mode()
        elif user_impaired == True:
            print("Error - blind user cannot enter training mode")
    else:
        print("Error - IDK how we got here")

    print("Finished")