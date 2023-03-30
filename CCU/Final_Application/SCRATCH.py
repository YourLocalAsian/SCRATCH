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
    globals.HUD_audio_char.write_value(constants.ASK_IMPAIRED.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    # wait for button notification
    print("Checking operating mode")
    x = 0
    for x in range(5):
        if globals.new_stick_button_received:
            globals.user_impaired = True
            globals.new_stick_button_received = False
            break
        time.sleep(1)
        print(f"Second {x}")

    # play audio confirming choice
    if globals.user_impaired:
        prompt = constants.BLIND_SELECTED
        globals.HUD_mode_char.write_value(constants.HudStates.BLIND.to_bytes(1, byteorder='big', signed = False))
        print("User is impaired\n")
    else:
        prompt = constants.NONBLIND_SELECTED
        globals.HUD_mode_char.write_value(constants.HudStates.NB_TARGET.to_bytes(1, byteorder='big', signed = False))
        print("User is not impaired\n")
    
    #globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    return

def set_operating_mode():
    while (not globals.HUD_connected or not globals.stick_connected):
        pass

    if globals.user_impaired == True: # only option when blind mode is game mode
        globals.operation_mode = constants.OperatingMode.GAME
        #globals.HUD_audio_char.write_value(constants.ENTERING_GM.to_bytes(1, byteorder='big', signed = False))
        time.sleep(2)
        globals.stick_fsm_char.write_value(constants.StickStates.SET_BLD.to_bytes(1, byteorder='big', signed = False))
        globals.HUD_audio_char.write_value(constants.CUE_CALIBRATED.to_bytes(1, byteorder='big', signed = False))
        time.sleep(5)
        return
    
    else:
        # play audio cue for selection
        #globals.HUD_audio_char.write_value(constants.SELECT_OP.to_bytes(1, byteorder='big', signed = False))
        time.sleep(2)
        print("Checking operating mode")

        # wait for button notification
        x = 0
        for x in range(5):
            if globals.new_stick_button_received:
                mode = 4
                globals.HUD_mode_char.write_value(mode.to_bytes(1, byteorder='big', signed = False)) # ? Also don't know why this one
                globals.operation_mode = constants.OperatingMode.TRAINING
                print("Training Mode selected\n")
                #globals.HUD_audio_char.write_value(constants.ENTERING_TM.to_bytes(1, byteorder='big', signed = False))
                time.sleep(4)
                #globals.HUD_audio_char.write_value(constants.CALIBRATE_CUE.to_bytes(1, byteorder='big', signed = False))
                time.sleep(8)
                globals.stick_fsm_char.write_value(constants.StickStates.SET_NON.to_bytes(1, byteorder='big', signed = False))
                time.sleep(2)
                globals.HUD_audio_char.write_value(constants.CUE_CALIBRATED.to_bytes(1, byteorder='big', signed = False))
                time.sleep(5)
                
                return
            time.sleep(1)
            print(f"Second {x}")

    
    globals.operation_mode = constants.OperatingMode.GAME
    globals.new_stick_button_received = False
    mode = 3 
    globals.HUD_mode_char.write_value(mode.to_bytes(1, byteorder='big', signed = False)) # ? IDK why this send is here
    print("Game Mode selected\n")
    #globals.HUD_audio_char.write_value(constants.ENTERING_GM.to_bytes(1, byteorder='big', signed = False)) # Send game mode
    time.sleep(4)
    #globals.HUD_audio_char.write_value(constants.CALIBRATE_CUE.to_bytes(1, byteorder='big', signed = False))
    time.sleep(8)
    globals.stick_fsm_char.write_value(constants.StickStates.SET_NON.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)
    globals.HUD_audio_char.write_value(constants.CUE_CALIBRATED.to_bytes(1, byteorder='big', signed = False))
    time.sleep(5)

    return

# Game Mode Functions
def game_mode(angle, strength): # Called continously until shot is completed
    debug_print = True
    
    if debug_print:
        print("Entered standard game mode")
    
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
        # Ensure connection to VISION has been established
        while (globals.VISION_connected == False):
            pass
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
    
    p_angle = random.randint(-180, 180)
    p_strength = random.randint(0, 5)
    
    # Make recursive call
    if debug_print:
        print("Making recursive call to game_mode_std()")
    
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
            time.sleep(1)
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
            time.sleep(1)

    if continue_playing:
        # Generate PoC and Power
        if debug_print:
            print("Generating random PoC & power")
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
        pass

    debug_print = True
    globals.actual_x = 50

    # Send target to HUD
    if debug_print:
        print(f"\tSending target to HUD: {desired_strength}, {desired_x}, {desired_y} | {desired_strength.to_bytes(1, byteorder='big', signed = False)}, {desired_x.to_bytes(1, byteorder='big', signed = True)}, {desired_y.to_bytes(1, byteorder='big', signed = True)}")
    globals.HUD_fsm_char.write_value(constants.HudStates.NB_TARGET.to_bytes(1, byteorder='big', signed = False))
    globals.HUD_power_char.write_value(desired_strength.to_bytes(1, byteorder='big', signed = False))
    globals.HUD_poi_x_char.write_value(desired_x.to_bytes(4, byteorder='big', signed = True))
    globals.HUD_poi_y_char.write_value(desired_y.to_bytes(4, byteorder='big', signed = True))

    # Wait for TAKING_SHOT
    if debug_print:
        print("\tWaiting for TAKING_SHOT")
    
    last_fsm_time = time.time() # * Store last time flag in callback was set
    while (Stick_Receiver.stick_received_fsm != constants.StickStates.TAKING_SHOT):
        #if (time.time() - last_fsm_time > 5): # check if fsm state has been received within the last 5s
        #   print("ERROR - Stick FSM has not been received for 5s")
        if (globals.new_stick_fsm_received):
            print(f"FSM: {Stick_Receiver.stick_received_fsm}")
            last_fsm_time = time.time()
            #time.sleep(1) # ? don't think this sleep is necessary

    # Trigger HUD to take picture
    if debug_print:
        print("\tTriggering HUD to take picture")
    globals.HUD_fsm_char.write_value(constants.HudStates.TAKE_PICTURE.to_bytes(1, byteorder='big', signed = False))

    # Process image & acceleration
    if debug_print:
        print("\tProcessing shot")
    time.sleep(8) # should receive image by then

    # Wait for SHOT_TAKEN
    while (Stick_Receiver.stick_received_fsm != constants.StickStates.SHOT_TAKEN):
        print(f"FSM: {Stick_Receiver.stick_received_fsm}")
        time.sleep(1)
    actual_pow = Stick_Receiver.map_acceleration()

    # Send feedback to HUD
    pow = int(actual_pow)
    poi_x = int(globals.actual_x)
    poi_y = int(globals.actual_y)
    if debug_print:
        print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
    globals.HUD_fsm_char.write_value(constants.HudStates.ACTUAL.to_bytes(1, byteorder='big', signed = False))
    globals.HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
    globals.HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
    globals.HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
    
    while Stick_Receiver.stick_received_fsm != 0:
        continue

    return

def shot_attempt_bld(desired_angle, desired_strength):
    debug_print = True

    while (not globals.HUD_connected or not globals.stick_connected or not globals.glove_connected):
        pass
    
    if debug_print:
        print("\tDoing blind shot stuff")
    
    # Pause cue stick to avoid false SHOT_TAKEN
    globals.stick_fsm_char.write_value(constants.StickStates.PAUSED.to_bytes(1, byteorder='big', signed = False))

    # Check if glove has been zeroed out
    globals.HUD_audio_char.write_value(constants.MOVE_FOR_CALIBRATION.to_bytes(1, byteorder='big', signed = False))
    #Glove_Receiver.check_glove_zeroed()
    #globals.HUD_audio_char.write_value(globals.GLOVE_ZEROED_OUT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    # Check glove angle for correctness
    if debug_print:
        print("\tChecking glove angle")
        time.sleep(1)
    globals.HUD_audio_char.write_value(constants.CHECKING_GLOVE_ANGLE.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)
    
    Glove_Receiver.check_glove_angle(desired_angle) # Call function in Glove_Receiver.py
    
    if debug_print:
        print("\tGlove angle correct")
    globals.HUD_audio_char.write_value(constants.GLOVE_ANGLE_CORRECT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    # Check glove distance
    if debug_print:
        print("\tChecking glove distance")
        time.sleep(1)
    globals.HUD_audio_char.write_value(constants.CHECKING_GLOVE_DISTANCE.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)
    
    Glove_Receiver.check_glove_distance()
    
    if debug_print:
        print("\tGlove distance correct")
        time.sleep(1)
    globals.HUD_audio_char.write_value(constants.GLOVE_DISTANCE_CORRECT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    # Unpause cue stick
    globals.stick_fsm_char.write_value(constants.StickStates.NOT_READY.to_bytes(1, byteorder='big', signed = False))

    # Check cue stick pitch
    if debug_print:
        print("\tChecking cue stick pitch")
        time.sleep(1)
    globals.HUD_audio_char.write_value(constants.CHECKING_STICK_PITCH.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    Stick_Receiver.check_stick_pitch()
    
    if debug_print:
        print("\tCue stick level")
        time.sleep(1)
    globals.HUD_audio_char.write_value(constants.STICK_PITCH_CORRECT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)

    # Send audio cue to HUD "Take shot"
    globals.HUD_audio_char.write_value(constants.TAKE_SHOT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)
    
    # Wait for "Shot Taken" from cue stick
    while (Stick_Receiver.stick_received_fsm != 4):
        pass
    globals.HUD_audio_char.write_value(constants.NICE_SHOT.to_bytes(1, byteorder='big', signed = False))
    time.sleep(2)
    
    return

if __name__ == '__main__':
    argument_passed = True if len(sys.argv) > 1 else False
    
    if (argument_passed):
        if (sys.argv[1] == "--h" or sys.argv[1] == "--help"):
            Debug.help_info()
        elif (sys.argv[1] == "--d" or sys.argv[1] == "--debug"):
            Debug.debug_menu()
        else:
            print("ERROR - unknown argument used")
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
            #print(f"GCB: {globals.callbacks_set}")
            time.sleep(1)

        #globals.HUD_audio_char.write_value(constants.WELCOME.to_bytes(1, byteorder='big', signed = False)) # Welcome to SCRATCH
        #time.sleep(2)

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