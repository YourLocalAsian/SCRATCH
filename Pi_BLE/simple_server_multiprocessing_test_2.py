"""Example of how to create a Peripheral device/GATT Server"""
# Standard modules
import logging
import random
import threading
import time

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter
from bluezero import peripheral
from bluezero import device

# constants
# Custom service uuid
    #CPU_TMP_SRVC = '12341000-1234-1234-1234-123456789abc'
# https://www.bluetooth.com/specifications/assigned-numbers/
# Bluetooth SIG adopted UUID for Temperature characteristic
    #CPU_TMP_CHRC = '2A6E'
# Bluetooth SIG adopted UUID for Characteristic Presentation Format
    #CPU_FMT_DSCP = '2904'

characteristic_ref = None
number_sender = None
connected = False

def read_value():
    """
    Example read callback. Value returned needs to be a list of bytes/integers
    in little endian format.

    This one does a mock reading CPU temperature callback.
    Return list of integer values.
    Bluetooth expects the values to be in little endian format and the
    temperature characteristic to be an sint16 (signed & 2 octets) and that
    is what dictates the values to be used in the int.to_bytes method call.

    :return: list of uint8 values
    """
    cpu_value = random.randrange(0,7,1) #random.randrange(3200, 5310, 10) / 100
    return list(int(cpu_value).to_bytes(2,
                                              byteorder='little', signed=True))


def update_value(characteristic):
    """
    Example of callback to send notifications

    :param characteristic:
    :return: boolean to indicate if timer should continue
    """
    # read/calculate new value.
    new_value = read_value()
    # Causes characteristic to be updated and send notification
    characteristic.set_value(new_value)
    # Return True to continue notifying. Return a False will stop notifications
    # Getting the value from the characteristic of if it is notifying
    return characteristic.is_notifying


def notify_callback(notifying, characteristic):
    """
    Noitificaton callback example. In this case used to start a timer event
    which calls the update callback ever 2 seconds

    :param notifying: boolean for start or stop of notifications
    :param characteristic: The python object for this characteristic
    """
    if notifying:
        print('First time calling update value')
        #async_tools.add_timer_seconds(2, update_value, characteristic)
        global characteristic_ref 
        characteristic_ref = characteristic
        print('assigned charac, {}'.format(characteristic_ref))
        update_value(characteristic_ref)
    else:
        print("Not notifying")

def on_connect(dev):
    global connected
    connected = True

def on_disconnect(dev):
    global connected
    connected = False

def main(adapter_address):
    """Creation of peripheral"""
    logger = logging.getLogger('localGATT')
    logger.setLevel(logging.DEBUG)

    # Example of the output from read_value
    print('Number to be sent is {}\u00B0C'.format(
        int.from_bytes(read_value(), byteorder='little', signed=True)/100))
    
    global number_sender
    # Create peripheral
    if number_sender is None:
        number_sender = peripheral.Peripheral(adapter_address,
                                        local_name='Number_Sender',
                                        appearance=1344)
        # Add service
        number_sender.add_service(srv_id=1, uuid='4fafc201-1fb5-459e-8fcc-c5c9c331914b', primary=True)
        # Add characteristic
        number_sender.add_characteristic(srv_id=1, chr_id=1, uuid='beb5483e-36e1-4688-b7f5-ea07361b26a8',
                                   value=[], notifying=True,
                                   flags=['notify'],
                                   read_callback=read_value,
                                   write_callback=None,
                                   notify_callback=notify_callback
                                   )
        # Add descriptor
        number_sender.add_descriptor(srv_id=1, chr_id=1, dsc_id=1, uuid='00000000-0000-0000-0000-000000002902',
                               value=[0x0E, 0xFE, 0x2F, 0x27, 0x01, 0x00,
                                      0x00],
                               flags=['read'])

        number_sender.on_connect = on_connect
        number_sender.on_disconnect = on_disconnect
        global characteristic_ref
        characteristic_ref = number_sender.characteristics[0]

        # Publish peripheral and start event loop
        number_sender.publish()
        print('After publishing')


if __name__ == '__main__':
    # Get the default adapter address and pass it to main
    add = list(adapter.Adapter.available())[0].address 
    
    #main(list(adapter.Adapter.available())[0].address)
    while True:
        try:
            bt_thread = threading.Thread(target=main, args =[add])
            bt_thread.start()
            while not connected:
                print('waiting for connection')
                time.sleep(2)
            while connected:
                print('updating value...')
                update_value(characteristic_ref)
                time.sleep(5)
        except: #if an exception occurs, will disconnect from all peripherals, then attempt to restart bluetooth and connect to the peripheral
            for dev in device.Device.available():
                if(dev.connected):
                    dev.disconnect()
                    print(f"Disconnecting {dev.name}")
        

    