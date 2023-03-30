
import sys
import time
import lib.constants as constants
import lib.globals as globals
import threading

from bluezero import adapter, central

sys.path.append("../Final_Application")
import subsystems.HUD_Receiver as HUD_Receiver
import subsystems.Glove_Receiver as Glove_Receiver
import subsystems.Stick_Receiver as Stick_Receiver

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
            if (name == 'stick' and constants.STICK_SERVER_SRV.lower() in dev.uuids) or (name == 'glove' and constants.GLOVE_SERVER_SRV.lower() in dev.uuids) or (name == 'HUD' and constants.HUD_SERVER_SRV.lower() in dev.uuids):
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
        if globals.HUD_monitor is None: #ADDED this IF
            print('Creating new HUD Central Object...')
            globals.HUD_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('HUD Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            globals.HUD_mode_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_MODE_CHAR_UUID)
            globals.HUD_power_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_POWER_CHAR_UUID)
            globals.HUD_poi_x_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_POI_X_CHAR_UUID)
            globals.HUD_poi_y_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_POI_Y_CHAR_UUID)
            globals.HUD_angle_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_ANGLE_CHAR_UUID)
            globals.HUD_audio_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_AUDIO_CHAR_UUID)
            globals.HUD_image_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_IMAGE_CHAR_UUID)
            globals.HUD_fsm_char = globals.HUD_monitor.add_characteristic(constants.HUD_SERVER_SRV, constants.HUD_FSM_CHAR_UUID)

        print("Connecting to " + dev.alias)
        globals.HUD_monitor.connect()

        if not globals.HUD_monitor.connected:
            print("Didn't connect to device!")
            return
        
        globals.HUD_connected = True
        #globals.HUD_monitor.dongle.on_disconnect = HUD_on_disconnect
        print('HUD Connection successful!')

        # Enable heart rate notifications
        globals.HUD_image_char.start_notify()
        print('notifications started for HUD')

        if not globals.HUD_notification_cb_set:
            print('Setting callback for notifications for HUD')
            globals.HUD_image_char.add_characteristic_cb(HUD_Receiver.HUD_on_new_image)
            globals.HUD_notification_cb_set = True


    elif name == 'stick':
        if globals.stick_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            globals.stick_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            globals.stick_acc_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_ACC_CHAR_UUID)
            globals.stick_roll_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_ROLL_CHAR_UUID)
            globals.stick_pitch_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_PITCH_CHAR_UUID)
            globals.stick_fsm_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_FSM_CHAR_UUID)
            globals.stick_yaw_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_YAW_CHAR_UUID)
            globals.stick_button_char = globals.stick_monitor.add_characteristic(constants.STICK_SERVER_SRV, constants.STICK_BUTTON_CHAR_UUID)

        print("Connecting to " + dev.alias)
        globals.stick_monitor.connect()

        if not globals.stick_monitor.connected:
            print("Didn't connect to device!")
            return
        globals.stick_connected = True
        globals.stick_monitor.dongle.on_disconnect = on_disconnect
        print('Stick Connection successful!')

        globals.stick_roll_char.start_notify()
        globals.stick_pitch_char.start_notify()
        globals.stick_acc_char.start_notify()
        globals.stick_yaw_char.start_notify()
        globals.stick_button_char.start_notify()
        globals.stick_fsm_char.start_notify()

        if not globals.stick_notification_cb_set:
            print('Setting callback for stick notifications')
            globals.stick_acc_char.add_characteristic_cb(Stick_Receiver.stick_on_new_acc)
            globals.stick_roll_char.add_characteristic_cb(Stick_Receiver.stick_on_new_roll)
            globals.stick_pitch_char.add_characteristic_cb(Stick_Receiver.stick_on_new_pitch)
            globals.stick_yaw_char.add_characteristic_cb(Stick_Receiver.stick_on_new_yaw)
            globals.stick_button_char.add_characteristic_cb(Stick_Receiver.stick_on_new_button)
            globals.stick_fsm_char.add_characteristic_cb(Stick_Receiver.stick_on_new_fsm)
            globals.stick_notification_cb_set = True
            print("Stick callbacks done")
        
        try:
            # Startup in async mode to enable notify, etc
            globals.stick_monitor.run()
        except KeyboardInterrupt:
            print("Disconnecting and exiting ...")

    elif name == 'glove':
        if globals.glove_monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            globals.glove_monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('glove Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            globals.glove_yaw_char = globals.glove_monitor.add_characteristic(constants.GLOVE_SERVER_SRV, constants.GLOVE_YAW_CHAR_UUID)
            globals.glove_distance_char = globals.glove_monitor.add_characteristic(constants.GLOVE_SERVER_SRV, constants.GLOVE_DISTANCE_CHAR_UUID)

        print('connecting to glove')    
        globals.glove_monitor.connect()

        # Check if Connected Successfully
        if not globals.glove_monitor.connected:
            print("Didn't connect to glove device!")
            return
        globals.glove_connected = True
        #globals.glove_monitor.dongle.on_disconnect = glove_on_disconnect
        print('Connection successful!')

        # Enable heart rate notifications
        globals.glove_yaw_char.start_notify()
        globals.glove_distance_char.start_notify()

        if not globals.glove_notification_cb_set:
            print('Setting callback for notifications for glove')
            globals.glove_yaw_char.add_characteristic_cb(Glove_Receiver.glove_on_new_yaw)
            globals.glove_distance_char.add_characteristic_cb(Glove_Receiver.glove_on_new_distance)
            globals.glove_notification_cb_set = True
    else:
        print('Invalid name in connect_and_run_function')

def connect_to_HUD():
    print("Scanning for HUD")
    devices = scan_for_devices(name='HUD')
    for dev in devices:
        if dev:
            print("HUD Found!")
            connect_and_run(dev=dev,name='HUD')
            break

def connect_to_glove():
    print("Scanning for glove")
    devices = scan_for_devices(name='glove')
    for dev in devices:
        if dev:
            print("glove Found!")
            connect_and_run(dev=dev,name='glove')
            break

def connect_to_stick():
    print("Scanning for stick")
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
def on_disconnect(self):
    if not globals.HUD_monitor.connected:
        HUD_on_disconnect()
    if not globals.glove_monitor.connected:
        glove_on_disconnect()
    if not globals.stick_monitor.connected:
        stick_on_disconnect()

def HUD_on_disconnect():
    """Disconnect from the remote device."""
    print('HUD Disconnected!')  
    print('Stopping notify')
    globals.HUD_image_char.stop_notify()
    # for character in HUD_monitor._characteristics:
    #     character.stop_notify()  
    print('Disconnecting...')  
    globals.HUD_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this #commented out since only stick_monitor will be running the glib loop
    
      
    #flag setting
    globals.HUD_connected = False
    #print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for three seconds, then attempting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None #central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='HUD')
            #print('Found our device!')
        for dev in devices:
            if constants.HUD_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, name='HUD')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break

def stick_on_disconnect():
    global bt_thread
    """Disconnect from the remote device."""
    print('STICK Disconnected!')  
    print('Stopping notify')
    for character in globals.stick_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    globals.stick_monitor.disconnect()   
    globals.stick_monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    globals.stick_connected = False
    print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for three seconds, then attempting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None #central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='stick')
       # print('Found our device!')
        for dev in devices:
            if constants.STICK_SERVER_SRV.lower() in dev.uuids:
                #print('Found our device!')
                bt_thread = threading.Thread(target=connect_and_run, args=[dev, 'stick'])
                bt_thread.start()
                print(f"Just started thread {bt_thread}")
                break
        break

def glove_on_disconnect():
    #global bt_thread
    """Disconnect from the remote device."""
    print('GLOVE Disconnected!')  
    print('Stopping notify')
    for character in globals.glove_monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    globals.glove_monitor.disconnect()   
    #monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    globals.glove_connected = False
    #print( f"The thread is {bt_thread}")

    #while (bt_thread.is_alive()):
    #    continue

    #Attempt to scan and reconnect
    print("Server disconnected. Sleeping for three seconds, then attempting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None#central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='glove') #TODO Change the scan function to accept what to scan for?
       # print('Found our device!')
        for dev in devices:
            if constants.GLOVE_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, name='glove')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break