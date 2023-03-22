from Settings import *

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
    print(f'Value is {value}')
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
    print(f"Received the acc value {number}.")

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
    print(number)
    binn = bin(number)
    print(f"Binary value is {binn}")
    number = (number << 8) + int(value[2])
    number = (number << 8) + int(value[1]) 
    number = (number << 8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"Received the roll value {int(number)}.")

def stick_on_new_pitch(iface, changed_props, invalidated_props):
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
    print(f"Received the pitch value {number}.")

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
    print(f"Received the yaw value {number}.")

def stick_on_new_button(iface, changed_props, invalidated_props):
    """
    Callback used to receive notification events from the device.
    :param iface: dbus advanced data
    :param changed_props: updated properties for this event, contains Value
    :param invalidated_props: dvus advanced data
    """
    global stick_received_button, new_stick_button_received
    
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
    print(f"Received the button value {stick_received_button}.")

    # Set flag that button received
    new_stick_button_received = True


def stick_on_new_fsm(iface, changed_props, invalidated_props):
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
    print(f"Received the fsm value {number}. Setting state to 5")
    x = 5
    stick_fsm_char.write_value(x.to_bytes(1,byteorder='big', signed=False))

# Checking functions
def check_stick_pitch():
    global ANGLE_THRESHOLD, HUD_audio_char
    global new_stick_pitch_received, stick_received_pitch
    pitch = 180
    debug_print = True

    new_stick_pitch_received = False # initialize flag

    while abs(pitch) > ANGLE_THRESHOLD:
        while (new_stick_pitch_received == False): # block until new stick pitch received
            pass
        
        pitch = stick_received_pitch
        
        if pitch > 0:
            if debug_print:
                print("\t\Tilt stick down")
                time.sleep(1)
            # Send audio cue
            prompt = AIM_LOWER
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))
        else:
            if debug_print:
                print("\t\tTilt stick up")
                time.sleep(1)
            # Send audio cue
            prompt = AIM_HIGHER
            HUD_audio_char.write_value(prompt.to_bytes(1, byteorder='big', signed = False))

        time.sleep(1)
        new_stick_pitch_received = False # clear flag before proceeding

    return

def stick_on_disconnect(self):
    global bt_thread
    """Disconnect from the remote device."""
    print('STICK Disconnected!')  
    print('Stopping notify')
    for character in stick_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    stick_monitor.disconnect()   
    stick_monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    global stick_connected
    stick_connected = False
    print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for five seconds, then attemting to reconnect...")
    time.sleep(5)
    for dongle in adapter.Adapter.available():
        devices = central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='stick')
            print('Found our device!')
        for dev in devices:
            if STICK_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                bt_thread = threading.Thread(target=connect_and_run, args=[dev, 'stick'])
                bt_thread.start()
                print(f"Just started thread {bt_thread}")
                break
        break