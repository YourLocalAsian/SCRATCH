from BLE_Functions import *
import random
import HUD_Receiver
import Stick_Receiver
import Glove_Receiver
import Settings

def help_info():
    print("\nSCRATCH [Version 1.0]")
    print("Developers:  Luke Ambray")
    print("             Goran Lalich")
    print("             Mena Mishriky")
    print("             Mark Nelson\n")
    print("--d(--debug) Enters debug mode")
    print("--h(--help)  Displays group information and arguments\n")

def debug_menu():
    print("\nSCRATCH - Debug Mode\n")

    print("Subsystem Selection:")
    print("1. HUD")
    print("2. Cue Stick")
    print("3. Glove")
    print("4. Exit")
    val = input("\nSelection: ")

    while (val != 4):
        if (val == '1'):
            debug_HUD()
        elif (val == '2'):
            debug_stick()
        elif (val == '3'):
            debug_glove()
        elif (val == '4'):
            print("Exiting SCRATCH... goodbye")
            return
        else:
            print("ERROR - Invalid selection\n")
            
        print("\nSubsystem Selection:")
        print("1. HUD")
        print("2. Cue Stick")
        print("3. Glove")
        print("4. Exit")
        val = input("\nSelection: ")
    
    return

# HUD Debug Functions
def debug_HUD():
    connect_to_HUD() 

    while (not Settings.HUD_connected):
        time.sleep(1)

    print("\nHUD Selection:")
    print("1. Display")
    print("2. Audio")
    print("3. Camera")
    print("4. Go back to main menu")
    val = input("\nSelection: ")

    while (val != 3):
        if (val == '1'):
            test_display()
        elif (val == '2'):
            test_audio()
        elif (val == '3'):
            test_camera()
        elif (val == '4'):
            return
        else:
            print("ERROR - Invalid selection\n")
        
        print("\nCue Stick Selection:")
        print("1. IMU")
        print("2. Buttons")
        print("3. Go back to main menu")
        val = input("\nSelection: ")

def test_display():
    print("Press Ctrl+C to exit testing")
    time.sleep(2)
    
    try:
        while True:
            # Send random target
            strength = random.randint(0,5)
            poi_x = random.randint(-15, 15)
            poi_y = random.randint(-15, 15)

            Settings.HUD_fsm_char.write_value(Settings.HudStates.NB_TARGET.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_power_char.write_value(strength.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
            Settings.HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
            print(f"Sending target power, x and y to be: {strength}, {poi_x}, {poi_y}")
            time.sleep(2)

            strength = random.randint(0,5)
            poi_x = random.randint(-15, 15)
            poi_y = random.randint(-15, 15)

            Settings.HUD_fsm_char.write_value(Settings.HudStates.ACTUAL.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_power_char.write_value(strength.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
            Settings.HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
            print(f"Sending actual power, x and y to be: {strength}, {poi_x}, {poi_y}")
            time.sleep(2)
    except KeyboardInterrupt:
        return

def test_audio():
    print("Press Ctrl+C to exit testing")
    time.sleep(2)
    
    try:
        Settings.HUD_mode_char.write_value(Settings.HudStates.BLIND.to_bytes(1, byteorder='big', signed = False))
        while True:
            val = "\nEnter prompt number: "
            Settings.HUD_audio_char.write_value(val.to_bytes(1, byteorder='big', signed = False))
            time.sleep(3)
    except KeyboardInterrupt:
        return

def test_camera():
    print("Press Ctrl+C to exit testing")
    time.sleep(2)

    try:
        while True:
            Settings.actual_x = 50
            print('Setting state to INITIAL')
            Settings.HUD_fsm_char.write_value(Settings.HudStates.INITIAL.to_bytes(1, byteorder='big', signed = False))

            #send random power and poi numbers
            #target
            pow = random.randint(0,5)
            poi_x = random.randint(-15, 15)
            poi_y = random.randint(-15,15)
            print(f'Sending target power, x and y to be {pow}, {poi_x}, {poi_y}')
            Settings.HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
            Settings.HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
            time.sleep(3)
            
            #cycle through states
            print("Triggering picture capture")
            Settings.HUD_fsm_char.write_value(Settings.HudStates.TAKE_PICTURE.to_bytes(1, byteorder='big', signed = False))
            time.sleep(8) #should receive image
            
            #post shot feedback
            pow = random.randint(0,5)
            poi_x = int(Settings.actual_x)
            poi_y = int(Settings.actual_y)
            print(f'Sending actual power, x and y to be {pow}, {poi_x}, {poi_y}')
            Settings.HUD_fsm_char.write_value(Settings.HudStates.ACTUAL.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
            Settings.HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
            Settings.HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
            
            #here user inspects his performance
            time.sleep(8)
    except KeyboardInterrupt:
        return        

# Stick Debug Functions
def debug_stick():
    connect_to_stick()
    
    print("\nCue Stick Selection:")
    print("1. IMU")
    print("2. Buttons")
    print("3. Go back to main menu")
    val = input("\nSelection: ")

    while (val != 3):
        if (val == '1'):
            test_IMU()
        elif (val == '2'):
            test_buttons()
        elif (val == '3'):
            return
        else:
            print("ERROR - Invalid selection\n")
        
        print("\nCue Stick Selection:")
        print("1. IMU")
        print("2. Buttons")
        print("3. Go back to main menu")
        val = input("\nSelection: ")

def test_IMU():
    while (not Settings.stick_connected):
        time.sleep(1)

    # enable cue stick
    Settings.stick_fsm_char.write_value(Settings.StickStates.SET_NON.to_bytes(1, byteorder='big', signed = False))

    print("\nIMU Test Selection")
    print("1. Orientation")
    print("2. Acceleration")
    print("3. Go back to stick selection")
    val = input("\nSelection: ")

    while (val != 3):
        if (val == '1'):
            test_IMU_orientation()
        elif (val == '2'):
            test_IMU_acceleration()
        elif (val == '3'):
            return
        else:
            print("ERROR - Invalid selection\n")
        
        print("\nCue Stick Selection:")
        print("1. Orientation")
        print("2. Acceleration")
        print("3. Go back to stick selection")
        val = input("\nSelection: ")

def test_IMU_acceleration():
    print("Type Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Acceleration: {Stick_Receiver.stick_received_acc}")
            if (Stick_Receiver.stick_received_fsm == Settings.StickStates.SHOT_TAKEN): # unblock stick FSM
                print("STICK STUCK - Press A to continue")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return

def test_IMU_orientation():
    print("Type Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Roll: {Stick_Receiver.stick_received_roll}, Pitch: {Stick_Receiver.stick_received_pitch}, Yaw: {Stick_Receiver.stick_received_yaw}")
            if (Stick_Receiver.stick_received_fsm == Settings.StickStates.SHOT_TAKEN): # unblock stick FSM
                print("STICK STUCK - Press A to continue")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return

def test_buttons():
    print("Type Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            if (Settings.new_stick_button_received):
                print(f"Button: {Stick_Receiver.stick_received_button}")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return

# Glove Debug Functions
def debug_glove():
    connect_to_glove()

    while (not Settings.glove_connected):
        time.sleep(1)
    
    print("\nGlove Selection:")
    print("1. Distance")
    print("2. Angle")
    print("3. Go back to main menu")
    val = input("\nSelection: ")

    while (val != 3):
        if (val == '1'):
            test_glove_distance()
        elif (val == '2'):
            test_glove_angle()
        elif (val == '3'):
            return
        else:
            print("ERROR - Invalid selection\n")
        
        print("\nGlove Selection:")
        print("1. Distance")
        print("2. Angle")
        print("3. Go back to main menu")
        val = input("\nSelection: ")

def test_glove_distance():
    print("Type Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Distance: {Glove_Receiver.glove_received_dist}")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return
    
def test_glove_angle():
    print("Type Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Angle: {Glove_Receiver.glove_received_yaw}")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return