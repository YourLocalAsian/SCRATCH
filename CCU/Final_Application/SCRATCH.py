# Import Statements
import threading
import time 
import sys
import random
from lib.BLE_Functions import *
import lib.constants as constants
import lib.globals as globals
import subsystems.Stick_Receiver as Stick_Receiver
import subsystems.Glove_Receiver as Glove_Receiver
import subsystems.Debug as Debug

# User Set Up Functions
def set_impaired():
    while (not globals.HUD_connected or not globals.stick_connected):
        time.sleep(1)
        if not globals.HUD_connected:
            print("HUD is not connected")
        if not globals.stick_connected:
            print("Stick is not connected")
    
    print("Asking if user is impaired\n")

    # play audio asking for impairness
    send_data(globals.HUD_audio_char, constants.ASK_IMPAIRED, 1, False)

    print("Checking impairedness:")
    time.sleep(2)
    x = 0
    for x in range(5):
        if globals.new_stick_button_received:
            globals.user_impaired = True
            globals.new_stick_button_received = False
            break
        time.sleep(1)
        print(f"\tSecond {x}")

    # play audio confirming choice
    if globals.user_impaired:
        prompt = constants.BLIND_SELECTED
        send_data(globals.HUD_mode_char, constants.HudStates.BLIND, 1, False)
        print("Selection - User is impaired\n")
    else:
        prompt = constants.NONBLIND_SELECTED
        send_data(globals.HUD_mode_char, constants.HudStates.NB_TARGET, 1, False)
        print("Selection - User is not impaired\n")
    
    time.sleep(2)

    return

def set_operating_mode():
    while (not globals.HUD_connected or not globals.stick_connected):
        continue

    if globals.user_impaired == True: # only option when blind mode is game mode
        globals.operation_mode = constants.OperatingMode.GAME
        time.sleep(2)
        send_data(globals.stick_fsm_char, constants.StickStates.SET_BLD, 1, False)
        send_data(globals.HUD_audio_char, constants.CUE_CALIBRATED, 1, False)
        time.sleep(5)
        return
    
    else:
        # play audio cue for selection
        time.sleep(2)
        print("Checking operating mode:")

        # wait for button notification
        x = 0
        for x in range(5):
            if globals.new_stick_button_received:
                mode = 4
                send_data(globals.HUD_mode_char, mode, 1, False) # ? Also don't know why this one
                globals.operation_mode = constants.OperatingMode.TRAINING
                print("Training Mode selected\n")
                time.sleep(12)
                send_data(globals.stick_fsm_char, constants.StickStates.SET_NON, 1, False)
                time.sleep(2)
                send_data(globals.HUD_audio_char, constants.CUE_CALIBRATED, 1, False)
                time.sleep(5)
                
                return
            time.sleep(1)
            print(f"\tSecond {x}")

    
    globals.operation_mode = constants.OperatingMode.GAME
    globals.new_stick_button_received = False
    mode = 3 
    send_data(globals.HUD_mode_char, mode, 1, False) # ? IDK why this send is here
    print("Game Mode selected\n")
    time.sleep(12)
    send_data(globals.stick_fsm_char, constants.StickStates.SET_NON, 1, False)
    time.sleep(2)
    send_data(globals.HUD_audio_char, constants.CUE_CALIBRATED, 1, False)
    time.sleep(5)

    return

# Game Mode Functions
def game_mode(angle, strength): # Called continously until shot is completed
    debug_print = True
        
    # Check if game completed
    if strength > 100: # strength is set to max value when game is completed 
        if debug_print:
            print("Game completed")
        return
    
    # Check if ongoing game
    elif strength > 0: # strength is positive during on going game
        # User Shot Attempt
        if globals.user_impaired:
            if debug_print:
                print("Calling blind user shot attempt")
            shot_attempt_bld(angle, strength)
        else:
            if debug_print:
                print("Calling standard user shot attempt")
            shot_attempt_std(0, 0, strength)
    
    else: # strength is negative when starting a game
        print("Welcome to Game Mode")
        # Ensure connection to VISION has been established
        while (globals.VISION_connected == False):
            print("Waiting for connection to VISION, sleeping for 1s")
            time.sleep(1)
        if debug_print:
            print("Connection to VISION verified")

    # Request next shot
    if debug_print:
        print("Asking VISION for next shot")

    # Wait for shot data
    if debug_print:
        print("Waiting for shot data")

    # Receive and parse shot data
    if debug_print:
        print("Shot data received")

    if globals.demo_mode:
        p_angle = constants.A_ARRAY[globals.demo_counter]
        p_strength = constants.S_ARRAY[globals.demo_counter]
        globals.demo_counter = (globals.demo_counter + 1) % 3
    else:            
        p_angle = random.randint(-180, 180)
        p_strength = random.randint(0,5)
    
    # Make recursive call
    if debug_print:
        print("Making recursive call to game_mode()")
    
    game_mode(p_angle, p_strength)

    return

# Training Mode Functions
def training_mode(shot_x, shot_y, strength):
    debug_print = True
    continue_playing = True 

    # Check if training just started, strength is set to zero on startup
    if strength != 0:
        # Call user shot attempt
        if debug_print:
            print("Calling standard user shot attempt")
        shot_attempt_std(shot_x, shot_y, strength)

        # Ask user if they want to continue
        while (globals.new_stick_button_received == False):
            pass

        if Stick_Receiver.stick_received_button == constants.ButtonInput.A:
            continue_playing = True
        elif Stick_Receiver.stick_received_button == constants.ButtonInput.B:
            continue_playing = False
        
    else:
        if debug_print:
            print("Welcome to Training Mode")

    if continue_playing:
        # Generate PoC and Power
        if debug_print:
            print("Generating random PoC & power")
        
        if globals.demo_mode:
            p_x = constants.X_ARRAY[globals.demo_counter]
            p_y = constants.Y_ARRAY[globals.demo_counter]
            p_strength = constants.S_ARRAY[globals.demo_counter]
            globals.demo_counter = (globals.demo_counter + 1) % 3
        else:
            p_x = random.randint(-15,15)
            p_y = random.randint(-15,15)
            p_strength = random.randint(0,5)

        # Make recursive call
        if debug_print:
            print("Making recursive call to training_mode()")
        training_mode(p_x, p_y, p_strength)
    
    else:
        if debug_print:
            print("Exiting training_mode()")

    return

# Shot Attempt Functions
def shot_attempt_std(desired_x, desired_y, desired_strength):
    while (not globals.HUD_connected or not globals.stick_connected):
        continue

    debug_print = True
    globals.actual_x = 50

    # Send target to HUD
    if debug_print:
        print(f"\tSending target to HUD: {desired_strength}, {desired_x}, {desired_y} | {desired_strength.to_bytes(1, byteorder='big', signed = False)}, {desired_x.to_bytes(1, byteorder='big', signed = True)}, {desired_y.to_bytes(1, byteorder='big', signed = True)}")
    
    send_data(globals.HUD_fsm_char, constants.HudStates.NB_TARGET, 1, False)
    send_data(globals.HUD_power_char, desired_strength, 1, False)
    send_data(globals.HUD_poi_x_char, desired_x, 4,True)
    send_data(globals.HUD_poi_y_char, desired_y, 4, True)

    # Wait for TAKING_SHOT
    while (Stick_Receiver.stick_received_fsm != constants.StickStates.WAITING):
        print(f"\tWaiting for WAITING (2), currentFSM: {Stick_Receiver.stick_received_fsm}, sleeping for 1s")
        time.sleep(1)

    # Trigger HUD to take picture
    if debug_print:
        print("\tTriggering HUD to take picture")
    
    send_data(globals.HUD_fsm_char, constants.HudStates.TAKE_PICTURE, 1, False)

    # Process image & acceleration
    if debug_print:
        print("\tProcessing shot")
    time.sleep(8) # should receive image by then

    # Wait for SHOT_TAKEN
    while (Stick_Receiver.stick_received_fsm != constants.StickStates.SHOT_TAKEN):
        print(f"\tWaiting for shot taken (4), current FSM: {Stick_Receiver.stick_received_fsm}, sleeping for 1s")
        time.sleep(1)
    actual_pow = Stick_Receiver.map_acceleration()

    # Send feedback to HUD
    pow = int(actual_pow)
    poi_x = int(globals.actual_x)
    poi_y = int(globals.actual_y)
    if debug_print:
        print(f'\tSending actual to HUD: {pow}, {poi_x}, {poi_y}')
    
    send_data(globals.HUD_fsm_char, constants.HudStates.ACTUAL, 1, False)
    send_data(globals.HUD_power_char, pow, 1, False)
    send_data(globals.HUD_poi_x_char, poi_x, 4, True)
    send_data(globals.HUD_poi_y_char, poi_y, 4, True)
    
    while Stick_Receiver.stick_received_fsm != constants.StickStates.NOT_READY:
        print("\tWaiting for user to press A for next shot, sleeping for 1s")
        time.sleep(1)
    
    return

def shot_attempt_bld(desired_angle, desired_strength):
    debug_print = True

    while (not globals.HUD_connected or not globals.stick_connected or not globals.glove_connected):
        pass

    print("\tEntering blind shot attempt")

    # Check if glove has been zeroed out
    print("\tChecking if glove has been zeroed out")
    send_data(globals.HUD_audio_char, constants.MOVE_FOR_CALIBRATION, 1, False)
    time.sleep(4)
    
    Glove_Receiver.check_glove_zeroed()
    
    print("\tGlove has been zeroed out")
    time.sleep(4)

    # Check glove angle for correctness
    if debug_print:
        print("\tChecking glove angle")
    send_data(globals.HUD_audio_char, constants.CHECKING_GLOVE_ANGLE, 1, False)
    time.sleep(4)
    
    Glove_Receiver.check_glove_angle(desired_angle) # Call function in Glove_Receiver.py
    
    if debug_print:
        print("\tGlove angle correct")
    send_data(globals.HUD_audio_char, constants.GLOVE_ANGLE_CORRECT, 1, False)
    time.sleep(4)

    # Check glove distance
    if debug_print:
        print("\tChecking glove distance")
    send_data(globals.HUD_audio_char, constants.CHECKING_GLOVE_DISTANCE, 1, False)
    time.sleep(4)
    
    Glove_Receiver.check_glove_distance()
    
    if debug_print:
        print("\tGlove distance correct")
    send_data(globals.HUD_audio_char, constants.GLOVE_DISTANCE_CORRECT, 1, False)
    time.sleep(4)

    # Check cue stick pitch
    if debug_print:
        print("\tChecking cue stick pitch")
    send_data(globals.HUD_audio_char, constants.CHECKING_STICK_PITCH, 1, False)
    time.sleep(4)

    Stick_Receiver.check_stick_pitch()
    
    if debug_print:
        print("\tCue stick level")
    send_data(globals.HUD_audio_char, constants.STICK_PITCH_CORRECT, 1, False)
    time.sleep(4)

    # Send audio cue to HUD "Take shot"
    mode = 16
    send_data(globals.stick_fsm_char, mode, 1, False)
    
    if debug_print:
        print("\tTelling user to TAKE SHOT")
    send_data(globals.HUD_audio_char, constants.TAKE_SHOT, 1, False)
    time.sleep(2)
    
    # Wait for "Shot Taken" from cue stick
    while (Stick_Receiver.stick_received_fsm != 4):
        continue

    print("\tSHOT TAKEN")
    send_data(globals.HUD_audio_char, constants.NICE_SHOT, 1, False)
    print("\tSent NICE SHOT")
    time.sleep(2)
    
    return

if __name__ == '__main__':
    argument_passed = True if len(sys.argv) > 1 else False
    
    if (argument_passed and not sys.argv[1] == "--demo"):
        if (sys.argv[1] == "--h" or sys.argv[1] == "--help"):
            Debug.help_info()
        elif (sys.argv[1] == "--d" or sys.argv[1] == "--debug"):
            Debug.debug_menu()
        else:
            print("ERROR - unknown argument used")
    else:
        if (argument_passed and sys.argv[1] == "--demo"):
            globals.demo_mode = True
            print("Welcome to SCRATCH - Demo Mode")
        else: 
            print("Welcome to SCRATCH\n")
        
        connect_to_everything() # Connect to all peripherals
        
        while (not globals.HUD_connected or not globals.stick_connected or not globals.glove_connected):
            if not globals.HUD_connected:
                print('HUD not connected')
            if not globals.stick_connected:
                print('stick not connected')
            if not globals.glove_connected:
                print('glove not connected')
            time.sleep(1)
        print(f"Successfully connected\n")

        while (globals.callbacks_set < 9):
            time.sleep(1)
        
        send_data(globals.stick_fsm_char, constants.StickStates.SET_SB, 1, False)

        # Determine blind vs not blind
        set_impaired()
        print(f"Impairedness set:", globals.user_impaired, "\n")
        time.sleep(5)

        # Determine Game Mode VS Training Mode
        set_operating_mode()
        print(f"Operating mode set:", globals.operation_mode, "\n")

        # Normal Operation
        if globals.operation_mode == constants.OperatingMode.GAME:
            print("Calling game_mode")
            game_mode(0, -1)
        elif globals.operation_mode == constants.OperatingMode.TRAINING:
            if globals.user_impaired == False:
                print("Calling training_mode")
                training_mode(0, 0, 0)
            elif globals.user_impaired == True:
                print("ERROR - blind user cannot enter training mode")
        else:
            print("ERROR - IDK how we got here")

        print("Finished")