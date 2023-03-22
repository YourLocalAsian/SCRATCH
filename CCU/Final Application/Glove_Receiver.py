from Settings import *

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
    
    global new_glove_angle_received, glove_received_yaw
    
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
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
    print(f"Received the yaw value {glove_received_yaw}.")

    # Set flag that yaw received
    new_glove_angle_received = True
    
    return

def glove_on_new_button(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global new_glove_dist_received, glove_received_dist
    
    value = changed_props.get('Value', None)
    if not value:
        print("\'Value\' not found!")
        return

    # Convert byte stream into int
    number = int(value[1])
    number = (number << 8) + int(value[0])

    # Store distance value
    glove_received_dist = number
    print(f"Received the distance value {glove_received_dist}.")

    # Set flag that dist received
    new_glove_dist_received = True

    return

# Checking functions
def check_glove_zeroed():
    global HUD_audio_char, new_glove_angle_received, glove_received_yaw
    angle = 180
    debug_print = True

    new_glove_angle_received = False # initialize flag

    while abs(angle) > ANGLE_THRESHOLD:
        while (new_glove_angle_received == False): # block until new glove angle received
            pass
        
        angle = glove_received_yaw
        
        # Send audio cue to zero out glove
        prompt = ZERO_OUT_GLOVE
        HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        time.sleep(2)
        new_glove_angle_received = False # clear flag before proceeding

    return # Only returns once glove has been zeroed out

def check_glove_angle(desired_angle):
    global HUD_audio_char, new_glove_angle_received, glove_received_yaw
    angle = 180
    debug_print = True

    new_glove_angle_received = False # initialize flag

    while abs(angle - desired_angle) > ANGLE_THRESHOLD:
        while (new_glove_angle_received == False): # block until new glove angle received
            pass
        
        angle = glove_received_yaw

        if (angle - desired_angle) > 0:
            if debug_print:
                print("\t\tTurn hand left")
            
            # Send audio cue
            prompt = TURN_LEFT
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        else:
            if debug_print:
                print("\t\tTurn hand right")
            
            # Send audio cue
            prompt = TURN_RIGHT
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        
        time.sleep(1)
        new_glove_angle_received = False # clear flag before proceeding
    
    return # Only returns once angle is correct enough

def check_glove_distance():
    global HUD_audio_char, new_glove_dist_received, glove_received_dist
    distance = 180
    debug_print = True

    new_glove_dist_received = False # initialize flag
    
    while abs(distance - DESIRED_DISTANCE) > DISTANCE_THRESHOLD:
        while (new_glove_dist_received == False): # block until new glove distance received
            pass

        distance = glove_received_dist
        
        if (distance - DESIRED_DISTANCE) > DISTANCE_THRESHOLD:
            if debug_print:
                print("\t\tMove hand forward")

            # Send audio cue
            prompt = MOVE_FORWARD
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        else:
            if debug_print:
                print("\t\tMove hand backward")

            # Send audio cue
            prompt = MOVE_BACKWARD
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        
        time.sleep(1)
        new_glove_dist_received = False # clear flag before proceeding

    return # Only returns once distance is correct enough

def glove_on_disconnect(self):
    global glove_connected
    #global bt_thread
    
    """Disconnect from the remote device."""
    print('GLOVE Disconnected!')  
    print('Stopping notify')
    for character in glove_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    glove_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this
    
    #flag setting
    glove_connected = False
    #print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    # Attempt to scan and reconnect
    print("Server disconnected. Sleeping for five seconds, then attemting to reconnect...")
    time.sleep(5)
    for dongle in adapter.Adapter.available():
        devices = central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='glove') #TODO Change the scan function to accept what to scan for?
            print('Found our device!')
        for dev in devices:
            if GLOVE_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, 'glove')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break
