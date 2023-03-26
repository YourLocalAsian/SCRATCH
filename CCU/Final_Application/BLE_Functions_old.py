import Settings
import time
import HUD_Receiver_old as HUD_Receiver
import Stick_Receiver_old as Stick_Receiver
import Glove_Receiver_old as Glove_Receiver

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
    for dongle in Settings.adapter.Adapter.available():
        # Filter dongles by adapter_address if specified
        if adapter_address and adapter_address.upper() != dongle.address():
            continue
        
        #MENA reset before scanning to not pickup old results
       # central.Central.available(dongle.address) = None

        # Actually listen to nearby advertisements for timeout seconds
        dongle.nearby_discovery(timeout=timeout)

        # Iterate through discovered devices
        for dev in Settings.central.Central.available(dongle.address):
            # Filter devices if we specified a HRM address
            if device_address and device_address == dev.address:
                yield dev

            # Otherwise, return devices that advertised the HRM Service UUID
            if (name == 'stick' and Settings.STICK_SERVER_SRV.lower() in dev.uuids) or (name == 'glove' and Settings.GLOVE_SERVER_SRV.lower() in dev.uuids) or (name == 'HUD' and Settings.HUD_SERVER_SRV.lower() in dev.uuids):
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
        if Settings.HUD_monitor is None: #ADDED this IF
            print('Creating new HUD Central Object...')
            Settings.HUD_monitor = Settings.central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('HUD Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            Settings.HUD_mode_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_MODE_CHAR_UUID)
            Settings.HUD_power_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_POWER_CHAR_UUID)
            Settings.HUD_poi_x_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_POI_X_CHAR_UUID)
            Settings.HUD_poi_y_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_POI_Y_CHAR_UUID)
            Settings.HUD_angle_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_ANGLE_CHAR_UUID)
            Settings.HUD_audio_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_AUDIO_CHAR_UUID)
            Settings.HUD_image_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_IMAGE_CHAR_UUID)
            Settings.HUD_fsm_char = Settings.HUD_monitor.add_characteristic(Settings.HUD_SERVER_SRV, Settings.HUD_FSM_CHAR_UUID)

        print("Connecting to " + dev.alias)
        Settings.HUD_monitor.connect()

        if not Settings.HUD_monitor.connected:
            print("Didn't connect to device!")
            return
        
        Settings.HUD_connected = True
        Settings.HUD_monitor.dongle.on_disconnect = HUD_on_disconnect
        print('HUD Connection successful!')

        # Enable heart rate notifications
        Settings.HUD_image_char.start_notify()

        if not Settings.HUD_notification_cb_set:
            print('Setting callback for notifications for HUD')
            Settings.HUD_image_char.add_characteristic_cb(HUD_Receiver.HUD_on_new_image)
            Settings.HUD_notification_cb_set = True


    elif name == 'stick':
        if Settings.stick_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            Settings.stick_monitor = Settings.central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            Settings.stick_acc_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_ACC_CHAR_UUID)
            Settings.stick_roll_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_ROLL_CHAR_UUID)
            Settings.stick_pitch_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_PITCH_CHAR_UUID)
            Settings.stick_fsm_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_FSM_CHAR_UUID)
            Settings.stick_yaw_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_YAW_CHAR_UUID)
            Settings.stick_button_char = Settings.stick_monitor.add_characteristic(Settings.STICK_SERVER_SRV, Settings.STICK_BUTTON_CHAR_UUID)

        print("Connecting to " + dev.alias)
        Settings.stick_monitor.connect()

        if not Settings.stick_monitor.connected:
            print("Didn't connect to device!")
            return
        Settings.stick_connected = True
        Settings.stick_monitor.dongle.on_disconnect = stick_on_disconnect
        print('Stick Connection successful!')

        Settings.stick_roll_char.start_notify()
        Settings.stick_pitch_char.start_notify()
        Settings.stick_acc_char.start_notify()
        Settings.stick_yaw_char.start_notify()
        Settings.stick_button_char.start_notify()
        Settings.stick_fsm_char.start_notify()

        if not Settings.stick_notification_cb_set:
            print('Setting callback for stick notifications')
            Settings.stick_acc_char.add_characteristic_cb(Stick_Receiver.stick_on_new_acc)
            Settings.stick_roll_char.add_characteristic_cb(Stick_Receiver.stick_on_new_roll)
            Settings.stick_pitch_char.add_characteristic_cb(Stick_Receiver.stick_on_new_pitch)
            Settings.stick_yaw_char.add_characteristic_cb(Stick_Receiver.stick_on_new_yaw)
            Settings.stick_button_char.add_characteristic_cb(Stick_Receiver.stick_on_new_button)
            Settings.stick_fsm_char.add_characteristic_cb(Stick_Receiver.stick_on_new_fsm)
            Settings.stick_notification_cb_set = True
        
        try:
            # Startup in async mode to enable notify, etc
            Settings.stick_monitor.run()
        except KeyboardInterrupt:
            print("Disconnecting and exiting ...")

    elif name == 'glove':
        if Settings.glove_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            Settings.glove_monitor = Settings.central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('glove Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            Settings.glove_yaw_char = Settings.glove_monitor.add_characteristic(Settings.GLOVE_SERVER_SRV, Settings.GLOVE_YAW_CHAR_UUID)
            Settings.glove_distance_char = Settings.glove_monitor.add_characteristic(Settings.GLOVE_SERVER_SRV, Settings.GLOVE_DISTANCE_CHAR_UUID)

        print('connecting to glove')    
        Settings.glove_monitor.connect()

        # Check if Connected Successfully
        if not Settings.glove_monitor.connected:
            print("Didn't connect to glove device!")
            return
        Settings.glove_connected = True
        Settings.glove_monitor.dongle.on_disconnect = glove_on_disconnect
        print('Connection successful!')

        # Enable heart rate notifications
        Settings.glove_yaw_char.start_notify()
        Settings.glove_distance_char.start_notify()

        if not Settings.glove_notification_cb_set:
            print('Setting callback for notifications for glove')
            Settings.glove_yaw_char.add_characteristic_cb(Glove_Receiver.glove_on_new_yaw)
            Settings.glove_distance_char.add_characteristic_cb(Glove_Receiver.glove_on_new_distance)
            Settings.glove_notification_cb_set = True
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
            bt_thread = Settings.threading.Thread(target=connect_and_run, args=[dev, None,'stick'])
            bt_thread.start()
            print( f"The thread is {bt_thread}")
            break

def connect_to_everything():
    connect_to_HUD()
    connect_to_glove()
    connect_to_stick()

# Disconnection Functions
def HUD_on_disconnect(self):
    """Disconnect from the remote device."""
    print('HUD Disconnected!')  
    print('Stopping notify')
    for character in Settings.HUD_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    Settings.HUD_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this #commented out since only Settings.stick_monitor will be running the glib loop
    
      
    #flag setting
    Settings.HUD_connected = False
    #print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for five seconds, then attemting to reconnect...")
    time.sleep(5)
    for dongle in Settings.adapter.Adapter.available():
        devices = Settings.central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='HUD')
            print('Found our device!')
        for dev in devices:
            if Settings.HUD_SERVER_SRV.lower() in dev.uuids:
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
    for character in Settings.stick_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    Settings.stick_monitor.disconnect()   
    Settings.stick_monitor.quit() #bt_thread should exit after this
    
    #flag setting
    Settings.stick_connected = False
    print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for five seconds, then attemting to reconnect...")
    time.sleep(5)
    for dongle in Settings.adapter.Adapter.available():
        devices = Settings.central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='stick')
            print('Found our device!')
        for dev in devices:
            if Settings.STICK_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                bt_thread = Settings.threading.Thread(target=connect_and_run, args=[dev, 'stick'])
                bt_thread.start()
                print(f"Just started thread {bt_thread}")
                break
        break

def glove_on_disconnect(self):
    """Disconnect from the remote device."""
    print('GLOVE Disconnected!')  
    print('Stopping notify')
    for character in Settings.glove_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    Settings.glove_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    Settings.glove_connected = False
    #print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for five seconds, then attemting to reconnect...")
    time.sleep(5)
    for dongle in Settings.adapter.Adapter.available():
        devices = Settings.central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='glove') #TODO Change the scan function to accept what to scan for?
            print('Found our device!')
        for dev in devices:
            if Settings.GLOVE_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, 'glove')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break