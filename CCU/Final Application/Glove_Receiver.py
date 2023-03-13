from Settings import *

def glove_on_new_yaw(iface, changed_props, invalidated_props):
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
    if (number > 180): #ASK LUKE
        number -= 4294967296
    print(f"Received the yaw value {number}.")

def glove_on_new_button(iface, changed_props, invalidated_props):
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

    number = int(value[1])
    number = (number << 8) + int(value[0])
    print(f"Received the button value {number}.")