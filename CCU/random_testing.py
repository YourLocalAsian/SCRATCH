import sys
import time

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

def debug_HUD():
    f = open("Final Application/HUD_images/test1.txt")
    print(f.read())
    f.close()
    return

def debug_stick():
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

    return

def test_IMU_acceleration():
    print("Press Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Acceleration: {1}")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return

def test_IMU_orientation():
    print("Press Ctrl+C to exit testing")
    time.sleep(2)
    try:
        while True:
            print(f"Roll: {1}, Pitch: {1}, Yaw: {1}")
            time.sleep(0.25)
    except KeyboardInterrupt:
        return

def test_buttons():
    print("Done with buttons")
    return

def debug_glove():
    print("Debugging Glove")
    return

if __name__ == '__main__':
    argument_passed = True if len(sys.argv) > 1 else False

    if (argument_passed):
        if (sys.argv[1] == "--h" or sys.argv[1] == "--help"):
            help_info()
        elif (sys.argv[1] == "--d" or sys.argv[1] == "--debug"):
            debug_menu()
        else:
            print("ERROR - unknown argument used")
    else:
        print("Main Functionality")




