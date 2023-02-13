"""Example of how to create a Central device/GATT Client"""
from enum import IntEnum
import struct

from bluezero import adapter
from bluezero import central
import threading
import time 

# Documentation can be found on Bluetooth.com
# https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/

# There are also published xml specifications for possible values
# For the Service:
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.service.heart_rate.xml

# For the Characteristics:
# Heart Rate Measurement
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.heart_rate_measurement.xml
# Body Sensor Location
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.body_sensor_location.xml
# Heart Rate Control Point
# https://github.com/oesmith/gatt-xml/blob/master/org.bluetooth.characteristic.heart_rate_control_point.xml

connected = False
monitor = None #This is a temporary name for the client/Central object
bt_thread = None
acc_char = None
roll_char = None
pitch_char = None
yaw_char = None
button_char = None
fms_char = None
notification_cb_set = False

def on_disconnect(self):
    global bt_thread
    """Disconnect from the remote device."""
    print('Disconnected!')  
    print('Stopping notify')
    for character in monitor._characteristics:
        character.stop_notify()  
    print('Disconnecting...')  
    monitor.disconnect()   
    
    #TEST to see if there are different bus names for this
    #print(monitor.rmt_device.services_available)
    #monitor.dongle.stop_discovery()

    monitor.quit() #bt_thread should exit after this
    #monitor.rmt_device.bus = None 
    
      
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


SERVER_SRV = '91bad492-b950-4226-aa2b-4ede9fa42f59' 
ACC_CHAR_UUID = 'ca73b3ba-39f6-4ab3-91ae-186dc9577d99'
ROLL_CHAR_UUID = '1d710a64-929a-11ed-a1eb-0242ac120002'
PITCH_CHAR_UUID = '1d710d8e-929a-11ed-a1eb-0242ac120002'
YAW_CHAR_UUID = '1d710f6e-929a-11ed-a1eb-0242ac120002'
BUTTON_CHAR_UUID = '1d7110c2-929a-11ed-a1eb-0242ac120002'
FMS_CHAR_UUID = '1d7111da-929a-11ed-a1eb-0242ac120002'
#BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'
#HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'


#class HeartRateMeasurementFlags(IntEnum):
#    HEART_RATE_VALUE_FORMAT_UINT16 = 0b00000001
#    SENSOR_CONTACT_DETECTED = 0b00000010
#    SENSOR_CONTACT_SUPPORTED = 0b00000100
#    ENERGY_EXPENDED_PRESENT = 0b00001000
#    RR_INTERVALS_PRESENT = 0b00010000


#class BodySensorLocation(IntEnum):
#    OTHER = 0
#    CHEST = 1
#    WRIST = 2
#    FINGER = 3
#    HAND = 4
#    EAR_LOBE = 5
#    FOOT = 6


#class HeartRateControlPoint(IntEnum):
#    RESET_ENERGY_EXPENDED = 1


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

def on_new_acc(iface, changed_props, invalidated_props):
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
    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"Received the acc value {number}.")

def on_new_roll(iface, changed_props, invalidated_props):
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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    print(number)
    binn = bin(number)
    print(f"Binary value is {binn}")
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1]) 
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"Received the roll value {int(number)}.")

def on_new_pitch(iface, changed_props, invalidated_props):
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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"Received the pitch value {number}.")

def on_new_yaw(iface, changed_props, invalidated_props):
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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"Received the yaw value {number}.")

def on_new_button(iface, changed_props, invalidated_props):
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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    print(f"Received the button value {number}.")

def on_new_fms(iface, changed_props, invalidated_props):
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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    print(f"Received the fms value {number}. Setting state to 5")
    x = 5
    fms_char.write_value(x.to_bytes(1,byteorder='big', signed=False))


def connect_and_run(dev=None, device_address=None):
    """
    Main function intneded to show usage of central.Central
    :param dev: Device to connect to if scan was performed
    :param device_address: instead, connect to a specific MAC address
    """
    # Create Interface to Central
    global acc_char
    global roll_char
    global pitch_char
    global yaw_char
    global button_char
    global fms_char
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
            acc_char = monitor.add_characteristic(SERVER_SRV, ACC_CHAR_UUID)
            roll_char = monitor.add_characteristic(SERVER_SRV, ROLL_CHAR_UUID)
            pitch_char = monitor.add_characteristic(SERVER_SRV, PITCH_CHAR_UUID)
            fms_char = monitor.add_characteristic(SERVER_SRV, FMS_CHAR_UUID)
            yaw_char = monitor.add_characteristic(SERVER_SRV, YAW_CHAR_UUID)
            button_char = monitor.add_characteristic(SERVER_SRV, BUTTON_CHAR_UUID)
            #yaw_char.add_characteristic_cb(on_new_number)
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
    roll_char.start_notify()
    pitch_char.start_notify()
    acc_char.start_notify()
    yaw_char.start_notify()
    button_char.start_notify()
    fms_char.start_notify()

    global notification_cb_set
    if not notification_cb_set:
        print('Setting callback for notifications')
        acc_char.add_characteristic_cb(on_new_acc)
        roll_char.add_characteristic_cb(on_new_roll)
        pitch_char.add_characteristic_cb(on_new_pitch)
        yaw_char.add_characteristic_cb(on_new_yaw)
        button_char.add_characteristic_cb(on_new_button)
        fms_char.add_characteristic_cb(on_new_fms)
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
                print('Doing stuff')
                time.sleep(4)

        # Only demo the first device found
        #break #TODO For now we break after first one