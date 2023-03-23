from Settings import *
from HUD_Receiver import *
from Glove_Receiver import *
from Stick_Receiver import *

# Connection Functions
def scan_for_devices(
        adapter_address=None,
        device_address=None,
        timeout=5.0,
        name = 'stick'):
    """
    Called to scan for BLE devices advertising the Heartrate Service UUID
    If there are multiple adapters on your system, this will scan using
    all dongles unless an adapter is specfied through its MAC address
    :param adapter_address: limit scanning to this adapter MAC address
    :param hrm_address: scan for a specific peripheral MAC address
    :param timeout: how long to search for devices in seconds
    :return: generator of Devices that match the search parameters
    """
    # If there are multiple adapters on your system, this will scan using
    # all dongles unless an adapter is specified through its MAC address
    for dongle in adapter.Adapter.available():
        # Filter dongles by adapter_address if specified
        if adapter_address and adapter_address.upper() != dongle.address():
            continue
        
        #MENA reset before scanning to not pickup old results
       # central.Central.available(dongle.address) = None

        # Actually listen to nearby advertisements for timeout seconds
        dongle.nearby_discovery(timeout=timeout)

        # Iterate through discovered devices
        for dev in central.Central.available(dongle.address):
            # Filter devices if we specified a HRM address
            if device_address and device_address == dev.address:
                yield dev

            # Otherwise, return devices that advertised the HRM Service UUID
            if (name == 'stick' and STICK_SERVER_SRV.lower() in dev.uuids) or (name == 'glove' and GLOVE_SERVER_SRV.lower() in dev.uuids) or (name == 'HUD' and HUD_SERVER_SRV.lower() in dev.uuids):
                print("Found a device with the SRV uuid. Yielding it...")
                yield dev

def connect_and_run(dev=None, device_address=None, name = 'stick'):
    """
    Main function intneded to show usage of central.Central
    :param dev: Device to connect to if scan was performed
    :param device_address: instead, connect to a specific MAC address
    """
    # Create Interface to Central
    if(name == 'HUD'):
        global HUD_mode_char
        global HUD_power_char
        global HUD_poi_x_char
        global HUD_poi_y_char
        global HUD_angle_char
        global HUD_audio_char
        global HUD_image_char
        global HUD_fsm_char

        global HUD_monitor
        if HUD_monitor is None: #ADDED this IF
            print('Creating new HUD Central Object...')
            HUD_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('HUD Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            HUD_mode_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_MODE_CHAR_UUID)
            HUD_power_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_POWER_CHAR_UUID)
            HUD_poi_x_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_POI_X_CHAR_UUID)
            HUD_poi_y_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_POI_Y_CHAR_UUID)
            HUD_angle_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_ANGLE_CHAR_UUID)
            HUD_audio_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_AUDIO_CHAR_UUID)
            HUD_image_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_IMAGE_CHAR_UUID)
            HUD_fsm_char = HUD_monitor.add_characteristic(HUD_SERVER_SRV, HUD_FSM_CHAR_UUID)

        print("Connecting to " + dev.alias)
        HUD_monitor.connect()

        if not HUD_monitor.connected:
            print("Didn't connect to device!")
            return
        global HUD_connected
        HUD_connected = True
        HUD_monitor.dongle.on_disconnect = HUD_on_disconnect
        print('HUD Connection successful!')

        # Enable heart rate notifications
        HUD_image_char.start_notify()

        global HUD_notification_cb_set
        if not HUD_notification_cb_set:
            print('Setting callback for notifications for HUD')
            HUD_image_char.add_characteristic_cb(HUD_on_new_image)
            HUD_notification_cb_set = True


    elif name == 'stick':
        global stick_acc_char
        global stick_roll_char
        global stick_pitch_char
        global stick_yaw_char
        global stick_button_char
        global stick_fsm_char

        global stick_monitor
        if stick_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            stick_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            stick_acc_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_ACC_CHAR_UUID)
            stick_roll_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_ROLL_CHAR_UUID)
            stick_pitch_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_PITCH_CHAR_UUID)
            stick_fsm_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_FSM_CHAR_UUID)
            stick_yaw_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_YAW_CHAR_UUID)
            stick_button_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_BUTTON_CHAR_UUID)

        print("Connecting to " + dev.alias)
        stick_monitor.connect()

        if not stick_monitor.connected:
            print("Didn't connect to device!")
            return
        global stick_connected
        stick_connected = True
        stick_monitor.dongle.on_disconnect = stick_on_disconnect
        print('Stick Connection successful!')

        stick_roll_char.start_notify()
        stick_pitch_char.start_notify()
        stick_acc_char.start_notify()
        stick_yaw_char.start_notify()
        stick_button_char.start_notify()
        stick_fsm_char.start_notify()

        global stick_notification_cb_set
        if not stick_notification_cb_set:
            print('Setting callback for stick notifications')
            stick_acc_char.add_characteristic_cb(stick_on_new_acc)
            stick_roll_char.add_characteristic_cb(stick_on_new_roll)
            stick_pitch_char.add_characteristic_cb(stick_on_new_pitch)
            stick_yaw_char.add_characteristic_cb(stick_on_new_yaw)
            stick_button_char.add_characteristic_cb(stick_on_new_button)
            stick_fsm_char.add_characteristic_cb(stick_on_new_fsm)
            stick_notification_cb_set = True
        
        try:
            # Startup in async mode to enable notify, etc
            stick_monitor.run()
        except KeyboardInterrupt:
            print("Disconnecting and exiting ...")

    elif name == 'glove':
        global glove_yaw_char
        global glove_distance_char

        global glove_monitor
        if glove_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            glove_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('glove Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            glove_yaw_char = glove_monitor.add_characteristic(GLOVE_SERVER_SRV, GLOVE_YAW_CHAR_UUID)
            glove_distance_char = glove_monitor.add_characteristic(GLOVE_SERVER_SRV, GLOVE_DISTANCE_CHAR_UUID)

        print('connecting to glove')    
        glove_monitor.connect()

        # Check if Connected Successfully
        if not glove_monitor.connected:
            print("Didn't connect to glove device!")
            return
        global glove_connected
        glove_connected = True
        glove_monitor.dongle.on_disconnect = glove_on_disconnect
        print('Connection successful!')

        # Enable heart rate notifications
        glove_yaw_char.start_notify()
        glove_distance_char.start_notify()

        global glove_notification_cb_set
        if not glove_notification_cb_set:
            print('Setting callback for notifications for glove')
            glove_yaw_char.add_characteristic_cb(glove_on_new_yaw)
            glove_distance_char.add_characteristic_cb(glove_on_new_distance)
            glove_notification_cb_set = True
    else:
        print('Invalid name in connect_and_run_function')

def connect_to_HUD():
    devices = scan_for_devices(name='HUD')
    for dev in devices:
        if dev:
            print("HUD Found!")
            connect_and_run(dev=dev,name='HUD')
            break

def connect_to_glove():
    devices = scan_for_devices(name='glove')
    for dev in devices:
        if dev:
            print("glove Found!")
            connect_and_run(dev=dev,name='glove')
            break

def connect_to_stick():
    devices = scan_for_devices(name='stick')
    for dev in devices:
        if dev:
            print("stick Found!")
            bt_thread = threading.Thread(target=connect_and_run, args=[dev, None,'stick'])
            bt_thread.start()
            print( f"The thread is {bt_thread}")
            break

def connect_to_everything():
    connect_to_HUD()
    connect_to_glove()
    connect_to_stick()

# Disconnection Functions
def HUD_on_disconnect(self):
    #global bt_thread
    """Disconnect from the remote device."""
    print('HUD Disconnected!')  
    print('Stopping notify')
    for character in HUD_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    HUD_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this #commented out since only stick_monitor will be running the glib loop
    
      
    #flag setting
    global HUD_connected
    HUD_connected = False
    #print( f"The thread is {bt_thread}")

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
            devices = scan_for_devices(name='HUD')
            print('Found our device!')
        for dev in devices:
            if HUD_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, 'HUD')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break

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

def glove_on_disconnect(self):
    #global bt_thread
    """Disconnect from the remote device."""
    print('GLOVE Disconnected!')  
    print('Stopping notify')
    for character in monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    glove_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    global glove_connected
    glove_connected = False
    #print( f"The thread is {bt_thread}")

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