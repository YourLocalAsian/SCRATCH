# Import Statements
import threading
import time 
import sys
import random
from Settings import *
from Glove_Receiver import *
from HUD_Receiver import *
from Stick_Receiver import *

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
    user_impaired = True # TODO: remove with actual setting
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
def game_mode(angle, strength): # Called continously until shot is completed
    global user_impaired

    debug_print = True
    
    if debug_print:
        print("Entered standard game mode")
    
    # Check if game completed
    if strength > 100: # strength is set to max value when game is completed 
        if debug_print:
            print("Game completed")
            time.sleep(1)
        return
    
    # Check if ongoing game
    elif strength > 0: # strength is positive during on going game
        # User Shot Attempt
        if user_impaired:
            if debug_print:
                print("Calling blind user shot attempt")
                time.sleep(1)
            shot_attempt_bld(angle, strength)
        else:
            if debug_print:
                print("Calling standard user shot attempt")
                time.sleep(1)
            shot_attempt_std(0, 0, strength)
    
    else: # strength is negative when starting a game
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
    p_strength = 1
    
    # Make recursive call
    if debug_print:
        print("Making recursive call to game_mode_std()")
    
    game_mode(p_angle, p_strength)

    return

# Training Mode Functions
def training_mode(shot_x, shot_y, strength): # TODO
    debug_print = True
    continue_playing = True

    # Check if training just started, strength is set to zero on startup
    if strength != 0:
        # Call user shot attempt
        if debug_print:
            print("Calling standard user shot attempt")
            time.sleep(1)
        shot_attempt_std(shot_x, shot_y, strength)

        # Ask user if they want to continue
        continue_playing = False # ! IDK how we want to do this in practice
        
    else:
        if debug_print:
            print("Welcome to Training Mode")
            time.sleep(1)

    if continue_playing:
        # Generate PoC and Power
        if debug_print:
            print("Generating random PoC & power")
        p_x = 0
        p_y = 0
        p_strength = 1

        # Make recursive call
        if debug_print:
            print("Making recursive call to training_mode()")
            time.sleep(1)
        training_mode(p_x, p_y, p_strength)
    
    else:
        if debug_print:
            print("Exiting training_mode()")
            time.sleep(1)

    return

# Shot Attempt Functions
def shot_attempt_std(desired_x, desired_y, desired_strength):
    print("\tDoing standard shot stuff")
    time.sleep(5)
    
    return

def shot_attempt_bld(desired_angle, desired_strength):
    global HUD_audio_char
    debug_print = True
    
    if debug_print:
        print("\tDoing blind shot stuff")

    # Check if glove has been zeroed out
    prompt = MOVE_FOR_CALIBRATION
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    
    check_glove_zeroed()
    
    prompt = GLOVE_ZEROED_OUT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

    # Check glove angle for correctness
    if debug_print:
        print("\tChecking glove angle")
        time.sleep(1)
    prompt = CHECKING_GLOVE_ANGLE
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    
    check_glove_angle(desired_angle) # Call function in Glove_Receiver.py
    
    if debug_print:
        print("\tGlove angle correct")
    prompt = GLOVE_ANGLE_CORRECT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

    # Check glove distance
    if debug_print:
        print("\tChecking glove distance")
        time.sleep(1)
    prompt = CHECKING_GLOVE_DISTANCE
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    
    check_glove_distance()
    
    if debug_print:
        print("\tGlove distance correct")
        time.sleep(1)
    prompt = GLOVE_DISTANCE_CORRECT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

    # Check cue stick pitch
    if debug_print:
        print("\tChecking cue stick pitch")
        time.sleep(1)
    prompt = CHECKING_STICK_PITCH
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

    check_stick_pitch()
    
    if debug_print:
        print("\tCue stick level")
        time.sleep(1)
    prompt = STICK_PITCH_CORRECT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

    # Send audio cue to HUD "Take shot"
    prompt = TAKE_SHOT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    
    # Wait for "Shot Taken" from cue stick
    while (stick_received_fsm != 4):
        pass

    prompt = NICE_SHOT
    HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    
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
        print("Calling game_mode")
        game_mode(0, -1)
    elif operation_mode == OperatingMode.TRAINING:
        if user_impaired == False:
            print("Calling training_mode")
            training_mode(0, 0, 0)
        elif user_impaired == True:
            print("Error - blind user cannot enter training mode")
    else:
        print("Error - IDK how we got here")

    print("Finished")