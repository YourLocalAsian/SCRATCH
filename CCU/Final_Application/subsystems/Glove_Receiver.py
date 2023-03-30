import sys
import time
sys.path.append("../Final_Application")
import lib.constants as constants
import lib.globals as globals
from lib.BLE_Functions import *

# Variables for holding received values
glove_received_yaw = 0
glove_received_dist = 0

# Callback functions
def glove_on_new_yaw(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global glove_received_yaw
    
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found! - glove_on_new_yaw")
        globals.callbacks_set += 1
        return

    # Convert byte stream into int
    number = int(value[3])
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1])
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 180): #ASK LUKE
        number -= 4294967296
    
    # Store yaw value
    glove_received_yaw = number
    #print(f"Received the yaw value {glove_received_yaw}.")

    # Set flag that yaw received
    globals.new_glove_angle_received = True
    
    return

def glove_on_new_distance(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global glove_received_dist
    
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found! - glove_on_new_distance")
        globals.callbacks_set += 1
        return

    # Convert byte stream into int
    number = int(value[1])
    number = (number << 8) + int(value[0])

    # Store distance value
    glove_received_dist = number
    #print(f"Received the distance value {glove_received_dist}.")

    # Set flag that dist received
    globals.new_glove_dist_received = True

    return

# Checking functions
def check_glove_zeroed():
    global glove_received_yaw
    angle = 180
    debug_print = True

    globals.new_glove_angle_received = False # initialize flag

    while abs(angle) > constants.ANGLE_THRESHOLD:
        while (globals.new_glove_angle_received == False): # block until new glove angle received
            pass
        
        angle = glove_received_yaw
        
        # Send audio cue to zero out glove
        prompt = constants.ZERO_OUT_GLOVE
        globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        #time.sleep(2)
        globals.new_glove_angle_received = False # clear flag before proceeding

    return # Only returns once glove has been zeroed out

def check_glove_angle(desired_angle):
    global glove_received_yaw
    angle = 180
    debug_print = True

    globals.new_glove_angle_received = False # initialize flag

    while abs(angle - desired_angle) > constants.ANGLE_THRESHOLD:
        while (globals.new_glove_angle_received == False): # block until new glove angle received
            continue

        angle = glove_received_yaw
        print(f"Received {angle}, want {desired_angle}")

        if (angle - desired_angle) > 0:
            if debug_print:
                print("\t\tTurn hand left")
            
            # Send audio cue
            prompt = constants.TURN_LEFT
            globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
            #time.sleep(2)
        else:
            if debug_print:
                print("\t\tTurn hand right")
            
            # Send audio cue
            prompt = constants.TURN_RIGHT
            globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
            #time.sleep(2)
        
        #time.sleep(1)
        globals.new_glove_angle_received = False # clear flag before proceeding
    
    return # Only returns once angle is correct enough

def check_glove_distance():
    global glove_received_dist
    distance = 180
    debug_print = True

    globals.new_glove_dist_received = False # initialize flag
    
    while abs(distance - constants.DESIRED_DISTANCE) > constants.DISTANCE_THRESHOLD:
        while (globals.new_glove_dist_received == False): # block until new glove distance received
            pass

        distance = glove_received_dist
        
        if (distance - constants.DESIRED_DISTANCE) > constants.DISTANCE_THRESHOLD:
            if debug_print:
                print("\t\tMove hand forward")

            # Send audio cue
            prompt = constants.MOVE_FORWARD
            globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        else:
            if debug_print:
                print("\t\tMove hand backward")

            # Send audio cue
            prompt = constants.MOVE_BACKWARD
            globals.HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        
        #time.sleep(1)
        globals.new_glove_dist_received = False # clear flag before proceeding

    return # Only returns once distance is correct enough

