"""Example of how to create a Central device/GATT Client"""
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
actual_x = 0
actual_y = 0
received_integers = []

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
        print('No circles')

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
        global actual_x
        global actual_y
        actual_x = 50
        actual_y = 0
        if(laser_found):
            cv2.circle(cropped_image, (laser_x,laser_y),1, (0,255,0), -1)
            laser_x = (laser_x/(highX - lowX)* 30.0 - 15.0)//1.0
            laser_y = (-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0   
            actual_x = int(laser_x)
            actual_y = int(laser_y)
            print(f'The LASER coordinates are ({laser_x},{laser_y})')
            cv2.imwrite(final_image_name, cropped_image)
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
            else:
                print('No laser found at all')
        
        #cv2.imshow("Contours", cropped_image)
        #cv2.waitKey(0)
    else:
        print('no balls found!')
    #exit
    cv2.destroyAllWindows()


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
    #print(f'length of received integers is {len(received_integers)}')

    global image_counter
    if(received_integers and bytes([received_integers[-1]]) == bytes([217]) and bytes([received_integers[-2]]) == bytes([255])):
        with open(f"HUD_receiver_test_{image_counter}.jpeg", "wb") as fp:
            for integer in received_integers:
                fp.write(bytes([integer]))
        print("Done!")
        comp_vision(f"HUD_receiver_test_{image_counter}.jpeg", f"HUD_receiver_test_contours_{image_counter}.jpeg")
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

                    time.sleep(1) #wait to simulate game mode selection SHOULD I MAKE THIS LONGER?
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
                        #target
                        pow = random.randint(0,5)
                        poi_x = random.randint(-15, 15)
                        poi_y = random.randint(-15,15)
                        print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                        power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                        poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                        poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                        time.sleep(3)
                        
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
                        time.sleep(12) #should receive image
                        
                        #post shot feedback
                        state = 4
                        print('Setting state to 4')
                        fsm_char.write_value(state.to_bytes(1, byteorder='big', signed = False))
                        #time.sleep(3)
                        pow = random.randint(0,5)
                        poi_x = int(actual_x)
                        poi_y = int(actual_y)
                        print(f'Sending power, x and y to be {pow}, {poi_x}, {poi_y}')
                        power_char.write_value(pow.to_bytes(1, byteorder='big', signed = False))
                        poi_x_char.write_value(poi_x.to_bytes(4, byteorder='big', signed = True))
                        poi_y_char.write_value(poi_y.to_bytes(4, byteorder='big', signed = True))
                        
                        #here user inspects his performance
                        time.sleep(8)

                    sys.exit() #done
