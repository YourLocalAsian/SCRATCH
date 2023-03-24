from BLE_Functions import *
import Settings
import time

MAX_ACCELERATION = 1000
mapArray = [-1, -3, -5, -7, -9]
ballSpeed = ["SOFT_TOUCH", "SLOW", "MEDIUM", "FAST", "POWER"]

# Variables for holding received values
stick_received_acc = 0
stick_received_roll = 0
stick_received_pitch = 0
stick_received_yaw = 0
stick_received_button = 0
stick_received_fsm = 0

# Callback functions
def stick_on_new_acc(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    
    value = changed_props.get('Value', None)
    #print(f'Value is {value}')
    if not value:
        print("\'Value\' not found!")
        return
    #TODO 
    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    
    # Store the acceleration values
    Settings.stick_received_acceleration.append(number)
    #print(f"Received the acc value {number}.")

    return

def stick_on_new_roll(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    number = int(value[3])
    #print(number)
    binn = bin(number)
    #print(f"Binary value is {binn}")
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1]) 
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    #print(f"Received the roll value {int(number)}.")

def stick_on_new_pitch(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global stick_received_pitch

    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    
    # Store pitch value
    stick_received_pitch = number
    #print(f"Received the pitch value {stick_received_pitch}.")

    # Set flag that pitch received 
    Settings.new_stick_pitch_received = True

    return

def stick_on_new_yaw(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    #print(f"Received the yaw value {number}.")

def stick_on_new_button(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global stick_received_button
    
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    
    # Store distance value
    stick_received_button = number
    #print(f"Received the button value {stick_received_button}.")

    # Set flag that button received
    Settings.new_stick_button_received = True

def stick_on_new_fsm(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global stick_received_fsm, new_stick_fsm_received

    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    
    # Store FSM Value
    stick_received_fsm = number
    print(f"Received the fsm value {stick_received_fsm}.")

    # Set flag
    new_stick_fsm_received = True

    return

# Checking functions
def check_stick_pitch():
    global stick_received_pitch
    pitch = 180
    debug_print = True

    Settings.new_stick_pitch_received = False # initialize flag

    while abs(pitch) > Settings.ANGLE_THRESHOLD:
        while (Settings.new_stick_pitch_received == False): # block until new stick pitch received
            pass
        
        pitch = stick_received_pitch
        
        if pitch > 0:
            if debug_print:
                print("\t\Tilt stick down")
                time.sleep(1)
            # Send audio cue
            prompt = Settings.AIM_LOWER
            Settings.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
            time.sleep(2)
        else:
            if debug_print:
                print("\t\tTilt stick up")
                time.sleep(1)
            # Send audio cue
            prompt = Settings.AIM_HIGHER
            Settings.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
            time.sleep(2)

        time.sleep(1)
        Settings.new_stick_pitch_received = False # clear flag before proceeding

    return

def map_acceleration():
    # Find global minima
    minimum = MAX_ACCELERATION
    for s in Settings.stick_received_acceleration:
        if s < minimum:
            minimum = s
        else:
            minimum = minimum
    
    # Map acceleration to strength
    mapped = 0
    for i in range(len(mapArray) - 1):
        if minimum <= mapArray[i]:
            mapped = i 
    
    Settings.stick_received_acceleration = [] # clear received_acceleration b.c shot is done
    
    return mapped