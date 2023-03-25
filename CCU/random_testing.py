import sys

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
    val = input("\nSelection: ")

    if (val == '1'):
        debug_HUD()
    elif (val == '2'):
        debug_stick()   
    elif (val == '3'):
        debug_glove()
    else:
        print("ERROR - Invalid option, exiting program\n") 
    
    return

def debug_HUD():
    print("Debugging HUD")
    return

def debug_stick():
    print("\nCue Stick Selection:")
    print("1. IMU")
    print("2. Buttons")
    val = input("\nSelection: ")

    while (val != 3):
        if (val == '1'):
            print("Testing IMU")
            print("\nCue Stick Selection:")
            print("1. IMU")
            print("2. Buttons")
            val = input("\nSelection: ")
        elif (val == '2'):
            print("Testing Buttons")
            print("\nCue Stick Selection:")
            print("1. IMU")
            print("2. Buttons")
            val = input("\nSelection: ")
        else:
            val = 3

    return


def test_IMU():
    return
def test_buttons():
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




