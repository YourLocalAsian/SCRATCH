"""Example of how to create a Central device/GATT Client"""
from enum import IntEnum
import struct

from bluezero import adapter
from bluezero import central
import threading
import time 
import sys
import random


connected = False
monitor = None #This is a temporary name for the client/Central object
bt_thread = None
mode_char = None
power_char = None
poi_x_char = None
poi_y_char = None
angle_char = None
fsm_char = None
audio_char = None
image_char = None
notification_cb_set = False
image_counter = 0
received_integers = []

def on_disconnect(self):
    global bt_thread
    """Disconnect from the remote device."""
    print('Disconnected!')  
    print('Stopping notify')
    for character in monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    monitor.disconnect()   
    monitor.quit() #bt_thread should exit after this
    
      
    #flag setting
    global connected
    connected = False
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
            devices = scan_for_devices()
            print('Found our device!')
        for dev in devices:
            if SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                bt_thread = threading.Thread(target=connect_and_run, args=[dev])
                bt_thread.start()
                print(f"Just started thread {bt_thread}")
                break
        break


SERVER_SRV = '843b4b1e-a8e9-11ed-afa1-0242ac120002' 
MODE_CHAR_UUID = '10c4bfee-a8e9-11ed-afa1-0242ac120002'
POWER_CHAR_UUID = '10c4c44e-a8e9-11ed-afa1-0242ac120002'
POI_X_CHAR_UUID = '10c4c69c-a8e9-11ed-afa1-0242ac120002'
POI_Y_CHAR_UUID = '10c4c696-a8e9-11ed-afa1-0242ac120002'
ANGLE_CHAR_UUID = '10c4c886-a8e9-11ed-afa1-0242ac120002'
AUDIO_CHAR_UUID = '10c4ce76-a8e9-11ed-afa1-0242ac120002'
IMAGE_CHAR_UUID = '10c4d3a8-a8e9-11ed-afa1-0242ac120002'
FSM_CHAR_UUID = '10c4d3a9-a8e9-11ed-afa1-0242ac120002'




def scan_for_devices(
        adapter_address=None,
        device_address=None,
        timeout=5.0):
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
            if SERVER_SRV.lower() in dev.uuids:
                print("Found a device with the SRV uuid. Yielding it...")
                yield dev

def on_new_image(iface, changed_props, invalidated_props):
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
    
    global received_integers

    #print(f'The value is {value} its length is {len(value)}')
    #number = int(value[0] ) #struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    #received_integers.append(number.to_bytes(4, 'little'))
    #print(f'The value is {value} its length is {len(value)}')
    
    
    if (len(value) > 7):
        received_integers.append(value[7])
    if (len(value) > 6):
        received_integers.append(value[6])
    if (len(value) > 5):
        received_integers.append(value[5])
    if (len(value) > 4):
        received_integers.append(value[4])
    if (len(value) > 3):
        received_integers.append(value[3])
    if (len(value) > 2):
        received_integers.append(value[2])
    if (len(value) > 1):
        received_integers.append(value[1])
    if (len(value) > 0):
        received_integers.append(value[0])
    if (len(value) > 15):
        received_integers.append(value[15])
    if (len(value) > 14):
        received_integers.append(value[14])
    if (len(value) > 13):
        received_integers.append(value[13])
    if (len(value) > 12):
        received_integers.append(value[12])
    if (len(value) > 11):
        received_integers.append(value[11])
    if (len(value) > 10):
        received_integers.append(value[10])
    if (len(value) > 9):
        received_integers.append(value[9])
    if (len(value) > 8):
        received_integers.append(value[8])
    if (len(value) > 19):
        received_integers.append(value[19])
    if (len(value) > 18):
        received_integers.append(value[18])
    if (len(value) > 17):
        received_integers.append(value[17])
    if (len(value) > 16):
        received_integers.append(value[16])

    global image_counter
    if(received_integers and bytes([received_integers[-1]]) == bytes([217]) and bytes([received_integers[-2]]) == bytes([255])):
        with open(f"HUD_receiver_test_{image_counter}.jpeg", "wb") as fp:
            for integer in received_integers:
                fp.write(bytes([integer]))
        print("Done!")
        received_integers = []
        image_counter +=1

def connect_and_run(dev=None, device_address=None):
    """
    Main function intneded to show usage of central.Central
    :param dev: Device to connect to if scan was performed
    :param device_address: instead, connect to a specific MAC address
    """
    # Create Interface to Central
    global mode_char
    global power_char
    global poi_x_char
    global poi_y_char
    global angle_char
    global audio_char
    global image_char
    global fsm_char
    if dev:
        print('Dev is being used')
        global monitor
        if monitor is None: #ADDED this IF
            print('Creating new Central Object...')
            monitor = central.Central(
                adapter_addr=dev.adapter,
                device_addr=dev.address)
            #Add the following here instead of after the else
            print('Central created! Adding characteristics...')
            # Characteristics that we're interested must be added to the Central
            # before we connect so they automatically resolve BLE properties
            # Heart Rate Measurement - notify
            mode_char = monitor.add_characteristic(SERVER_SRV, MODE_CHAR_UUID)
            power_char = monitor.add_characteristic(SERVER_SRV, POWER_CHAR_UUID)
            poi_x_char = monitor.add_characteristic(SERVER_SRV, POI_X_CHAR_UUID)
            poi_y_char = monitor.add_characteristic(SERVER_SRV, POI_Y_CHAR_UUID)
            angle_char = monitor.add_characteristic(SERVER_SRV, ANGLE_CHAR_UUID)
            audio_char = monitor.add_characteristic(SERVER_SRV, AUDIO_CHAR_UUID)
            image_char = monitor.add_characteristic(SERVER_SRV, IMAGE_CHAR_UUID)
            fsm_char = monitor.add_characteristic(SERVER_SRV, FSM_CHAR_UUID)
            
    else:
        monitor = central.Central(device_addr=device_address)
    

    # Body Sensor Location - read
    #location_char = monitor.add_characteristic(SERVER_SRV, BODY_SNSR_LOC_UUID)

    # Heart Rate Control Point - write - not always supported
    #control_point_char = monitor.add_characteristic(SERVER_SRV, HR_CTRL_PT_UUID)

    # Now Connect to the Device
    if dev:
        print("Connecting to " + dev.alias)
    else:
        print("Connecting to " + device_address)
    
    #monitor.dongle.powered = False
    #monitor.dongle.powered = True
    
    monitor.connect()

    # Check if Connected Successfully
    if not monitor.connected:
        print("Didn't connect to device!")
        return
    global connected
    connected = True
    monitor.dongle.on_disconnect = on_disconnect
    print('Connection successful!')

    # Enable heart rate notifications
    image_char.start_notify()

    global notification_cb_set
    if not notification_cb_set:
        print('Setting callback for notifications')
        image_char.add_characteristic_cb(on_new_image)
        notification_cb_set = True

    try:
        # Startup in async mode to enable notify, etc
        monitor.run()
    except KeyboardInterrupt:
        print("Disconnecting")

    #comment out for now TODO
    #print('Disconnecting...')
    #yaw_char.stop_notify()
    #monitor.disconnect()
    print('Exiting bluetooth thread!')


if __name__ == '__main__':
    # Discovery nearby heart rate monitors
    devices = scan_for_devices()
    for dev in devices:
        if dev:
            print("Device Found!")

        # Connect to first available heartrate monitor
        #global bt_thread
        bt_thread = threading.Thread(target=connect_and_run, args=[dev])
        bt_thread.start()
        print( f"The thread is {bt_thread}")
        #main program loop
        while True:
            while not connected:
                print("Waiting for connection")
                time.sleep(2)
            while connected:
                if(sys.argv[1] == 'blind'):
                    #Blind mode testing
                    time.sleep(6)
                    mode = 1
                    print("Sending blind mode")
                    mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))
                    time.sleep(4)
                    
                    #send audio commands
                    for i in range(3,7):
                        number = i
                        print("Sending random val")
                        audio_char.write_value(number.to_bytes(1, byteorder='big', signed = False))
                        time.sleep(3)
                    #done
                    sys.exit()
                else:
                    #non blind mode testing
                    time.sleep(3)
                    mode = 2
                    mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))

                    time.sleep(5) #wait to simulate game mode selection SHOULD I MAKE THIS LONGER?
                    mode = 3
                    print("game mode")
                    mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))
                    time.sleep(4)

                    for i in range(0,3):
                        #init
                        state = 0
                        print('Setting state to 0')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                    

                        #send random power and poi numbers
                        pow = random.randint(0,5)
                        poi_x = random.randint(-15, 15)
                        poi_y = random.randint(-15,15)
                        print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                        power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                        poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                        poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                        time.sleep(1)
                        
                        #cycle through states
                        state = 1
                        print('Setting state to 1')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                        time.sleep(1)
                        state = 2
                        print('Setting state to 2')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                        time.sleep(1)
                        state = 3
                        print('Setting state to 3')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                        time.sleep(20) #should receive image
                        
                        #post shot feedback
                        state = 4
                        print('Setting state to 4')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                        pow = random.randint(0,5)
                        poi_x = random.randint(-15, 15)
                        poi_y = random.randint(-15,15)
                        print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                        power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                        poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                        poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                        
                        #here user inspects his performance
                        time.sleep(5)

                    sys.exit() #done
