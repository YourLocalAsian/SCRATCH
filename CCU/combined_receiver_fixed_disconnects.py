from enum import IntEnum
import struct

from bluezero import adapter
from bluezero import central
import threading
import time 
import sys
import random
import cv2
import numpy as np
import pdb

#connected flags
HUD_connected = False
stick_connected = False
glove_connected = False

#central device
HUD_monitor = None 
glove_monitor = None
stick_monitor = None 
bt_thread = None

#NOTE: the idea here is that I will have three different central devices, but I ll try running only one glib loop (one thread). I dont see anything 
#           connecting the loop to a specific central object, so my guess is that whenever any device sends new data, the loop will catch that, and potentially
#           pass it to whoever subscribed to this data (i.e the correct central of the three). If this works, we will only have 1 BT thread and 1 main thread!

#HUD charachteristics and variables
HUD_mode_char = None
HUD_power_char = None
HUD_poi_x_char = None
HUD_poi_y_char = None
HUD_angle_char = None
HUD_fsm_char = None
HUD_audio_char = None
HUD_image_char = None
HUD_notification_cb_set = False
image_counter = 0
received_integers = []

#Glove Characteristics
glove_yaw_char = None
glove_distance_char = None
glove_notification_cb_set = False

#HUD Characteristics
stick_acc_char = None
stick_roll_char = None
stick_pitch_char = None
stick_yaw_char = None
stick_button_char = None
stick_fms_char = None
stick_notification_cb_set = False

#HUD UUIDs
HUD_SERVER_SRV = '843b4b1e-a8e9-11ed-afa1-0242ac120002' 
HUD_MODE_CHAR_UUID = '10c4bfee-a8e9-11ed-afa1-0242ac120002'
HUD_POWER_CHAR_UUID = '10c4c44e-a8e9-11ed-afa1-0242ac120002'
HUD_POI_X_CHAR_UUID = '10c4c69c-a8e9-11ed-afa1-0242ac120002'
HUD_POI_Y_CHAR_UUID = '10c4c696-a8e9-11ed-afa1-0242ac120002'
HUD_ANGLE_CHAR_UUID = '10c4c886-a8e9-11ed-afa1-0242ac120002'
HUD_AUDIO_CHAR_UUID = '10c4ce76-a8e9-11ed-afa1-0242ac120002'
HUD_IMAGE_CHAR_UUID = '10c4d3a8-a8e9-11ed-afa1-0242ac120002'
HUD_FSM_CHAR_UUID = '10c4d3a9-a8e9-11ed-afa1-0242ac120002'

#Glove UUIDs
GLOVE_SERVER_SRV = 'bb9246d2-98fc-11ed-a8fc-0242ac120002' 
GLOVE_YAW_CHAR_UUID = 'bb924d12-98fc-11ed-a8fc-0242ac120002'
GLOVE_DISTANCE_CHAR_UUID = 'bb925050-98fc-11ed-a8fc-0242ac120002'

#Stick UUIDs
STICK_SERVER_SRV = '91bad492-b950-4226-aa2b-4ede9fa42f59' 
STICK_ACC_CHAR_UUID = 'ca73b3ba-39f6-4ab3-91ae-186dc9577d99'
STICK_ROLL_CHAR_UUID = '1d710a64-929a-11ed-a1eb-0242ac120002'
STICK_PITCH_CHAR_UUID = '1d710d8e-929a-11ed-a1eb-0242ac120002'
STICK_YAW_CHAR_UUID = '1d710f6e-929a-11ed-a1eb-0242ac120002'
STICK_BUTTON_CHAR_UUID = '1d7110c2-929a-11ed-a1eb-0242ac120002'
STICK_FMS_CHAR_UUID = '1d7111da-929a-11ed-a1eb-0242ac120002'

def comp_vision(image_path, final_image_name):
    # reading image
    img = cv2.imread(image_path)
    ###cv2.imshow("OG", img)
    ##cv2.waitKey(0)
    if img is None:
        print('No image found')
        return
    #hsv for white color detection and mask generation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    black_lower = np.array([0,0,0]) #0,90,0
    black_upper = np.array([180,255,150]) #12,255,150
    mask = cv2.inRange(hsv, black_lower, black_upper)

    #cv2.imshow("Mask", mask)
    #cv2.waitKey(0)

    #noise filtering for mask
    kernel = np.ones((7,7),np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) #EXPERIMENTAL
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    #cv2.imshow("Mask -filtered", mask)
    #cv2.waitKey(0)

    #mask application
    segmented_image = cv2.bitwise_and(img, img, mask=mask)
    #cv2.imshow("Masked image", segmented_image)
    #cv2.waitKey(0)

    # converting image into grayscale and blurred image
    gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY) #required for transforms, and reduces math
    blur = cv2.GaussianBlur(gray, (3,3), 0) #7x7 is the kernel used. Used for noise reduction

    #cv2.imshow("blurred image", blur)
    #cv2.waitKey(0)

    #find circles in masked image -> white circules
    # Old values 140 22
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.75 , 30, param1=250
            ,param2=28, minRadius=10, maxRadius=35) #min radius was 17


    radius = 0
    x = 0
    y = 0
    potential_balls = []

    #find potential black balls
    if circles is not None: 
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            #get color of the center pixel, as well as four other pixels in the circle
            if  i[1] - i[2]//2 < 0:
                i[2] = i[1] * 2
                print('Forcing radius to {i[2]}')
            if i[0] + (i[2]//2) > 639:
                i[2] = (639 - i[0]) * 2
                print('Forcing radius to {i[2]}')
            if i[0] - i[2]//2 < 0:
                i[2] = i[0] * 2
                print('Forcing radius to {i[2]}')
            
            if i[0] < 0 or i[0] > 639 or i[1] < 0 or i[1] > 479:
                continue
            
            correct_color_counter = 0
            center_pixel_color = img[i[1]][i[0]]
            lower_pixel_color = img[i[1] - i[2]//2][i[0]]
            right_pixel_color = img[i[1]][i[0] + (i[2]//2)]
            left_pixel_color = img[i[1]][i[0] - i[2]//2]

            
            if ((center_pixel_color[2] > center_pixel_color[0] and center_pixel_color[2] > center_pixel_color[1] and center_pixel_color[2] < 120)):
                correct_color_counter += 1
            if ((lower_pixel_color[2] > lower_pixel_color[0] and lower_pixel_color[2] > lower_pixel_color[1] and lower_pixel_color[2] < 120)):
                correct_color_counter += 1
            if ((right_pixel_color[2] > right_pixel_color[0] and right_pixel_color[2] > right_pixel_color[1] and right_pixel_color[2] < 120)):
                correct_color_counter += 1
            if ((left_pixel_color[2] > left_pixel_color[0] and left_pixel_color[2] > left_pixel_color[1] and left_pixel_color[2] < 120)):
                correct_color_counter += 1

            if correct_color_counter >= 2:
                #store coordinates
                x = i[0]
                y = i[1]
                radius = i[2]
                potential_balls.append((x,y,radius))
                cv2.circle(segmented_image, (i[0],i[1]), i[2],(0,0,255),3) # the cue ball
    else:
        print('No circles found')
        return (50,0)

    #find cue ball from potential black balls, then crop and show cue ball
    if(potential_balls):
        x = 0
        y = 0
        radius = 0
        for i in potential_balls:
            print(i)
            if i[1] > y:
                x = i[0]
                y = i[1]
                radius = i[2]
        cv2.circle(segmented_image, (x,y), radius,(0,255,0),3) # the cue ball
        #show image
        #cv2.imshow("Ball detection -segmented", segmented_image)
        #cv2.waitKey(0)

        lowX =  x - (radius -3) #the plus 3 are so that we ensure only the ball is visible, its the reverse of a buffer
        highX = x + (radius -3)
        lowY = y - (radius  - 3)
        highY = y + (radius -3)
   
        if lowX < 0:
            print('Forcing lowX to 0')
            lowX = 0
        if highX > 639:
            print('Forcing highX to 639')
            highX = 639
        if lowY < 0:
            print('Forcing lowY to 0')
            lowX = 0
        if highY > 479:
            print('Forcing highY to 639')
            highX = 479

        print(f'The coordinates are {lowX}: {highX} and {lowY}: {highY}')
        cropped_image = img[lowY: highY, lowX: highX]
        #cv2.imshow("cropped image", cropped_image)
        #cv2.waitKey(0)
        
        #hsv for red color detection
        hsv_laser = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        
        #pink mask
        green_lower = np.array([35,0,150]) #155 0 0
        green_upper = np.array([75,255,255]) #180 120 255
        mask_laser = cv2.inRange(hsv_laser, green_lower, green_upper)

        #cv2.imshow("Mask for Laser", mask_laser)
        #cv2.waitKey(0)

        #noise filtering for mask
        kernel_laser = np.ones((2,2),np.uint8)
        mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_CLOSE, kernel_laser) #EXPERIMENTAL
        #mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_OPEN, kernel_laser) 
        #cv2.imshow("Mask -filtered Laser", mask_laser)
        #cv2.waitKey(0)

        
        laser_x = 0
        laser_y = 0
        laser_found = False
        biggest_G = 0

        contours, hier = cv2.findContours(mask_laser, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i in contours:
            M = cv2.moments(i)
            if M['m00'] != 0:
                #cv2.drawContours(cropped_image, [i], -1, (255,0,0), 2)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                pixel_val_g = cropped_image[cy][cx][1]
                pixel_val_b = cropped_image[cy][cx][0]
                pixel_val_r =cropped_image[cy][cx][2]
                cv2.circle(cropped_image, (cx,cy),1, (0,0,0), -1)
                if(pixel_val_g > biggest_G #must be the greenest thing
                and pixel_val_g>80 and pixel_val_b >80): #prevents detecting table as well
                    laser_x = cx
                    laser_y = cy
                    laser_found = True
                    #lowest_B = cropped_image[cy][cx][0]
                    biggest_G  =cropped_image[cy][cx][1]
                    cv2.circle(cropped_image, (cx,cy),1, (0,255,0), -1)
                else:
                    print(f'BGR is {cropped_image[cy][cx][0]} {cropped_image[cy][cx][1]} {cropped_image[cy][cx][2]}')
        if(laser_found):
            cv2.circle(cropped_image, (laser_x,laser_y),1, (0,255,0), -1)
            laser_x = (laser_x/(highX - lowX)* 30.0 - 15.0)//1.0
            laser_y = (-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0   
            actual_x = int(laser_x)
            actual_y = int(laser_y)
            print(f'The LASER coordinates are ({laser_x},{laser_y})')
            cv2.imwrite(final_image_name, cropped_image)
            return (actual_x, actual_y)
        else:
            print("No laser found. Trying brute force method")
            white_x_coordinates = []
            white_y_coordinates = []
            print(mask_laser.ndim)
            for i in range(0, len(mask_laser)):
                for j in range(0, len(mask_laser[i])):
                    if mask_laser[i][j] == 255:
                        white_x_coordinates.append(j)
                        white_y_coordinates.append(i)
            if white_x_coordinates:
                laser_x = sum(white_x_coordinates)/len(white_x_coordinates)
                laser_y = sum(white_y_coordinates)/len(white_y_coordinates)
                laser_x = int((laser_x/(highX - lowX)* 30.0 - 15.0)//1.0)
                laser_y = int((-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0 )
                print(f'The LASER coordinates are ({laser_x},{laser_y})')
                cv2.circle(cropped_image, (laser_x,laser_y),1, (0,255,0), -1)
                cv2.imwrite(final_image_name, cropped_image)
                actual_x = laser_x
                actual_y = laser_y
                return (actual_x, actual_y)
            else:
                print('No laser found at all')
                return (50,0)
        
        #cv2.imshow("Contours", cropped_image)
        #cv2.waitKey(0)
    else:
        print('no balls found!')
        return (50,0)

def on_disconnect(self):
    if not HUD_monitor.connected:
        HUD_on_disconnect()
    if not glove_monitor.connected:
        glove_on_disconnect()
    if not stick_monitor.connected:
        stick_on_disconnect()

def HUD_on_disconnect():
    #global bt_thread
    """Disconnect from the remote device."""
    #pdb.set_trace()
    print('HUD Disconnected!')  
    print('Stopping notify')
    HUD_image_char.stop_notify()
    # for character in HUD_monitor._characteristics:
    #     character.stop_notify()  
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
    print("Server disconnected. Sleeping for three seconds, then attemting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None#central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='HUD')
            #print('Found our device!')
        for dev in devices:
            if HUD_SERVER_SRV.lower() in dev.uuids:
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
    print("Server disconnected. Sleeping for three seconds, then attemting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None #central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='stick')
       # print('Found our device!')
        for dev in devices:
            if STICK_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
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
    for character in glove_monitor._characteristics:
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
    print("Server disconnected. Sleeping for three seconds, then attemting to reconnect...")
    time.sleep(3)
    for dongle in adapter.Adapter.available():
        devices = None#central.Central.available(dongle.address)
        while not devices:
            print("Cannot find server. Sleeping for 2s...")
            time.sleep(2)
            devices = scan_for_devices(name='glove') #TODO Change the scan function to accept what to scan for?
       # print('Found our device!')
        for dev in devices:
            if GLOVE_SERVER_SRV.lower() in dev.uuids:
                print('Found our device!')
                connect_and_run(dev, name='glove')
                #bt_thread.start()
                #print(f"Just started thread {bt_thread}")
                break
        break

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

def HUD_on_new_image(iface, changed_props, invalidated_props):
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
    #print(f'length of received integers is {len(received_integers)}')

    global image_counter
    if(received_integers and bytes([received_integers[-1]]) == bytes([217]) and bytes([received_integers[-2]]) == bytes([255])):
        with open(f"HUD_receiver_test_{image_counter}.jpeg", "wb") as fp:
            for integer in received_integers:
                fp.write(bytes([integer]))
        print("IMAGE Done!")
        comp_vision(f"HUD_receiver_test_{image_counter}.jpeg", f"HUD_receiver_test_contours_{image_counter}.jpeg")
        received_integers = []
        image_counter +=1

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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 180): #ASK LUKE
        number -= 4294967296
    print(f"GLOVE Received the yaw value {number}. ")

def glove_on_new_distance(iface, changed_props, invalidated_props):
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

    number = int(value[1] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[0])
    print(f"GLOVE Received the distance value {number}.")


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
    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"STICK Received the acc value {number}.")

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
    print(f"STICK Received the roll value {int(number)}.")

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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"STICK Received the pitch value {number}.")

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

    number = int(value[3] )#struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    number = (number <<8) + int(value[2])
    number = (number <<8) + int(value[1])
    number = (number <<8) + int(value[0])
    number = int(number)
    if (number > 1000000): #ASK LUKE
        number -= 4294967296
    print(f"STICK Received the yaw value {number}.")

def stick_on_new_button(iface, changed_props, invalidated_props):
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
    print(f"STICK Received the button value {number}.")

def stick_on_new_fms(iface, changed_props, invalidated_props):
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
    print(f"STICK Received the fms value {number}. Setting state to 5")
    x = 5
    stick_fms_char.write_value(x.to_bytes(1,byteorder='big', signed=False))

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
        #HUD_monitor.dongle.on_disconnect = HUD_on_disconnect
        print('HUD Connection successful!')

        # Enable heart rate notifications
        HUD_image_char.start_notify()
        print('notifications started for HUD')

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
        global stick_fms_char

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
            stick_fms_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_FMS_CHAR_UUID)
            stick_yaw_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_YAW_CHAR_UUID)
            stick_button_char = stick_monitor.add_characteristic(STICK_SERVER_SRV, STICK_BUTTON_CHAR_UUID)

        print("Connecting to " + dev.alias)
        stick_monitor.connect()

        if not stick_monitor.connected:
            print("Didn't connect to device!")
            return
        global stick_connected
        stick_connected = True
        stick_monitor.dongle.on_disconnect = on_disconnect
        print('Stick Connection successful!')

        stick_roll_char.start_notify()
        stick_pitch_char.start_notify()
        stick_acc_char.start_notify()
        stick_yaw_char.start_notify()
        stick_button_char.start_notify()
        stick_fms_char.start_notify()

        global stick_notification_cb_set
        if not stick_notification_cb_set:
            print('Setting callback for stick notifications')
            stick_acc_char.add_characteristic_cb(stick_on_new_acc)
            stick_roll_char.add_characteristic_cb(stick_on_new_roll)
            stick_pitch_char.add_characteristic_cb(stick_on_new_pitch)
            stick_yaw_char.add_characteristic_cb(stick_on_new_yaw)
            stick_button_char.add_characteristic_cb(stick_on_new_button)
            stick_fms_char.add_characteristic_cb(stick_on_new_fms)
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
        #glove_monitor.dongle.on_disconnect = glove_on_disconnect
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
    
if __name__ == '__main__':
    test = 0
    devices = scan_for_devices(name='HUD')
    for dev in devices:
        if dev:
            print("HUD Found!")
            connect_and_run(dev=dev,name='HUD')
            break
    devices = scan_for_devices(name='glove')
    for dev in devices:
        if dev:
            print("glove Found!")
            connect_and_run(dev=dev,name='glove')
            break
    devices = scan_for_devices(name='stick')
    for dev in devices:
        if dev:
            print("stick Found!")
            bt_thread = threading.Thread(target=connect_and_run, args=[dev, None,'stick'])
            bt_thread.start()
            print( f"The thread is {bt_thread}")
            break

    while True:
        while HUD_connected and stick_connected and glove_connected:
            print('All connected, doing stuff')
            time.sleep(3)
            if (test ==0):
                test += 1
                mode = 2
                HUD_mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))

                time.sleep(1) #wait to simulate game mode selection SHOULD I MAKE THIS LONGER?
                mode = 3
                print("game mode")
                HUD_mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))
                time.sleep(4)

                
                #init
                state = 0
                print('Setting state to 0')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
            

                #send random power and poi numbers
                #target
                pow = random.randint(0,5)
                poi_x = random.randint(-15, 15)
                poi_y = random.randint(-15,15)
                print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                HUD_poi_x_char.write_value(poi_x.to_byt # if (test ==0):
                test += 1
                mode = 2
                HUD_mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))

                time.sleep(1) #wait to simulate game mode selection SHOULD I MAKE THIS LONGER?
                mode = 3
                print("game mode")
                HUD_mode_char.write_value(mode.to_bytes(1,byteorder='big', signed=False))
                time.sleep(4)

                
                #init
                state = 0
                print('Setting state to 0')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
            

                #send random power and poi numbers
                #target
                pow = random.randint(0,5)
                poi_x = random.randint(-15, 15)
                poi_y = random.randint(-15,15)
                print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                time.sleep(3)
                
                #cycle through states
                state = 1
                print('Setting state to 1')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(1)
                state = 2
                print('Setting state to 2')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(1)
                state = 3
                print('Setting state to 3')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(12) #should receive image
                
                #post shot feedback
                state = 4
                print('Setting state to 4')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                #time.sleep(3)
                pow = random.randint(0,5)
                poi_x = random.randint(-15, 15)
                poi_y = random.randint(-15, 15)
                print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))es(4, byteorder='big', signed = True))
                HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                time.sleep(3)
                
                #cycle through states
                state = 1
                print('Setting state to 1')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(1)
                state = 2
                print('Setting state to 2')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(1)
                state = 3
                print('Setting state to 3')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                time.sleep(12) #should receive image
                
                #post shot feedback
                state = 4
                print('Setting state to 4')
                HUD_fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                #time.sleep(3)
                pow = random.randint(0,5)
                poi_x = random.randint(-15, 15)
                poi_y = random.randint(-15, 15)
                print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                HUD_power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                HUD_poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                HUD_poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
        if not HUD_connected:
            print('HUD not connected')
        if not stick_connected:
            print('stick not connected')
        if not glove_connected:
            print('glove not connected')
        time.sleep(3)
