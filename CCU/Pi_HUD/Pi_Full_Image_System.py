"""Example of how to create a Central device/GATT Client"""
from enum import IntEnum
import struct

from bluezero import adapter
from bluezero import central
import threading
import time 
import sys
import cv2
import numpy as np
import os

def comp_vision(image_path, final_image_name):
    # reading image
    img = cv2.imread(image_path)
    ##cv2.imshow("OG", img)
    #cv2.waitKey(0)
    if img is None:
        print('No image found')
        return
    #hsv for white color detection and mask generation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    white_lower = np.array([0,0,0]) #000
    white_upper = np.array([180,90,255]) #30,255,255
    mask = cv2.inRange(hsv, white_lower, white_upper)

    #cv2.imshow("Mask", mask)
    cv2.waitKey(0)

    #noise filtering for mask
    kernel = np.ones((7,7),np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) #EXPERIMENTAL
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    #cv2.imshow("Mask -filtered", mask)
    cv2.waitKey(0)

    #mask application
    segmented_image = cv2.bitwise_and(img, img, mask=mask)
    #cv2.imshow("Masked image", segmented_image)
    cv2.waitKey(0)

    # converting image into grayscale and blurred image
    gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY) #required for transforms, and reduces math
    blur = cv2.GaussianBlur(gray, (7,7), 0) #7x7 is the kernel used. Used for noise reduction

    #cv2.imshow("blurred image", blur)
    cv2.waitKey(0)

    #find circles in masked image -> white circules
    # Old values 140 22
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1.5, 15, param1=200
            ,param2=27, minRadius=14, maxRadius=35) #min radius was 17

    
    radius = 0
    x = 0
    y = 0
    white_parameter = 190 #trial and error #was 150
    #draw circles
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            #get color of the center pixel, as well as four other pixels in the circle
            correct_color_counter = 0
            center_pixel_color = img[i[1]][i[0]]
            upper_pixel_color = img[i[1] + (i[2]//2)][i[0]]
            lower_pixel_color = img[i[1] - i[2]//2][i[0]]
            right_pixel_color = img[i[1]][i[0] + (i[2]//2)]
            left_pixel_color = img[i[1]][i[0] - i[2]//2]
            
            #if 3 pixels approximate to white, then its the ball
            if(((center_pixel_color[0] > white_parameter) and (center_pixel_color[1] > white_parameter) and (center_pixel_color[2] > white_parameter))):
                correct_color_counter = correct_color_counter + 1
            if((upper_pixel_color[0] > white_parameter) and (upper_pixel_color[1] > white_parameter) and (upper_pixel_color[2] > white_parameter)):
                correct_color_counter = correct_color_counter + 1
            if((lower_pixel_color[0] > white_parameter) and (lower_pixel_color[1] > white_parameter) and (lower_pixel_color[2] > white_parameter)):   
                correct_color_counter = correct_color_counter + 1
            if((left_pixel_color[0] > white_parameter) and (left_pixel_color[1] > white_parameter) and (left_pixel_color[2] > white_parameter)):   
                correct_color_counter = correct_color_counter + 1
            if((right_pixel_color[0] > white_parameter) and (right_pixel_color[1] > white_parameter) and (right_pixel_color[2] > white_parameter)):   
                correct_color_counter = correct_color_counter + 1    
            
            if correct_color_counter >= 3:
                cv2.circle(segmented_image, (i[0],i[1]), i[2],(0,255,0),3)
                #store coordinates
                x = i[0]
                y = i[1]
                radius = i[2]
            else:
                cv2.circle(segmented_image, (i[0],i[1]), i[2],(0,0,255),3) #not the cue ball
            #cv2.circle(img, (i[0],i[1]), i[2],(255,0,255),3)
    else:
        print('No circles')

    #show image
    ##cv2.imshow("Ball detection -segmented", segmented_image)
    #cv2.waitKey(0)

    #crop and show cue ball
    if(x):
        lowX =  x - (radius -3) #the plus 3 are so that we ensure only the ball is visible, its the reverse of a buffer
        highX = x + (radius -3)
        lowY = y - (radius   - 3)
        highY = y + (radius -3)
        print(f'The coordinates are {lowX}: {highX} and {lowY}: {highY}')
        cropped_image = img[lowY: highY, lowX: highX]
        ##cv2.imshow("cropped image", cropped_image)
        #cv2.waitKey(0)
        
        #hsv for red color detection
        hsv_laser = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        
        #pink mask
        green_lower = np.array([35,0,0]) #155 0 0
        green_upper = np.array([75,255,255]) #180 120 255
        mask_laser = cv2.inRange(hsv_laser, green_lower, green_upper)

        ##cv2.imshow("Mask for Laser", mask_laser)
        #cv2.waitKey(0)

        #noise filtering for mask
        kernel_laser = np.ones((2,2),np.uint8)
        mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_CLOSE, kernel_laser) #EXPERIMENTAL
        mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_OPEN, kernel_laser) 
        #cv2.imshow("Mask -filtered Laser", mask_laser)
        cv2.waitKey(0)
        
        aser_x = 0
        laser_y = 0
        laser_found = False
        biggest_G = 0
        #gray_ball = cv2.cvtColor(cropped_image,cv2.COLOR_BGR2GRAY)
        ##cv2.imshow("grayball", gray_ball)
        #cv2.waitKey(0)
        #ret,thresh = cv2.threshold(gray_ball, 205, 255, cv2.THRESH_BINARY_INV)
        ##cv2.imshow("threshold", thresh)
        #cv2.waitKey(0)

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
                and pixel_val_g>135 and pixel_val_b >135): #prevents detecting table as well
                    laser_x = cx
                    laser_y = cy
                    laser_found = True
                    #lowest_B = cropped_image[cy][cx][0]
                    biggest_G  =cropped_image[cy][cx][1]
                    cv2.circle(cropped_image, (cx,cy),1, (0,255,0), -1)
                else:
                    print(f'fuck my life. BGR is {cropped_image[cy][cx][0]} {cropped_image[cy][cx][1]} {cropped_image[cy][cx][2]}')
        if(laser_found):
            laser_x = (laser_x/(highX - lowX)* 30.0 - 15.0)//1.0
            laser_y = (-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0   
            print(f'The LASER coordinates are ({laser_x},{laser_y})')
            cv2.imwrite(final_image_name,cropped_image)
        else:
            print("No laser found")
        
        ##cv2.imshow("Contours", cropped_image)
        #cv2.waitKey(0)
    else:
        print('no balls found!')
    #exit
    cv2.destroyAllWindows()

connected = False
monitor = None #This is a temporary name for the client/Central object
bt_thread = None
number_char = None
notification_cb_set = False
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


SERVER_SRV = '4fafc201-1fb5-459e-8fcc-c5c9c331914b' #Assuming this is server uuid
NUM_CHAR_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
#BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'
#HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'


class HeartRateMeasurementFlags(IntEnum):
    HEART_RATE_VALUE_FORMAT_UINT16 = 0b00000001
    SENSOR_CONTACT_DETECTED = 0b00000010
    SENSOR_CONTACT_SUPPORTED = 0b00000100
    ENERGY_EXPENDED_PRESENT = 0b00001000
    RR_INTERVALS_PRESENT = 0b00010000


class BodySensorLocation(IntEnum):
    OTHER = 0
    CHEST = 1
    WRIST = 2
    FINGER = 3
    HAND = 4
    EAR_LOBE = 5
    FOOT = 6


class HeartRateControlPoint(IntEnum):
    RESET_ENERGY_EXPENDED = 1


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


def on_new_number(iface, changed_props, invalidated_props):
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
    
    #print(f'The value is {value} its length is {len(value)}')
    #number = int(value[0] ) #struct.unpack(fmt, bytes(payload[0:struct.calcsize(fmt)])) REMOVED MENA
    #received_integers.append(number.to_bytes(4, 'little'))
    
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
    
    
    #print(f'received number is {number} and in bytes it is: {hex(received_integers[-1])} and The value is {value}')
    #print(f"Received the number {number}. The interface is {iface} ")


def connect_and_run(dev=None, device_address=None):
    """
    Main function intneded to show usage of central.Central
    :param dev: Device to connect to if scan was performed
    :param device_address: instead, connect to a specific MAC address
    """
    # Create Interface to Central
    global number_char
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
            number_char = monitor.add_characteristic(SERVER_SRV, NUM_CHAR_UUID)
            #number_char.add_characteristic_cb(on_new_number)
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
    number_char.start_notify()
    global notification_cb_set
    if not notification_cb_set:
        print('Setting callback for notifications')
        number_char.add_characteristic_cb(on_new_number)
        notification_cb_set = True

    try:
        # Startup in async mode to enable notify, etc
        monitor.run()
    except KeyboardInterrupt:
        print("Disconnecting")

    #comment out for now TODO
    #print('Disconnecting...')
    #number_char.stop_notify()
    #monitor.disconnect()
    print('Exiting bluetooth thread!')


if __name__ == '__main__':
    print('Start of script')
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
            if(received_integers and bytes([received_integers[-1]]) == bytes([217]) and bytes([received_integers[-2]]) == bytes([255])):
                if (os.path.isfile('fuck_it_we_ball.jpeg')):
                    os.remove('fuck_it_we_ball.jpeg')
                with open("fuck_it_we_ball.jpeg", "wb") as fp:
                    for integer in received_integers:
                        fp.write(bytes([integer]))
                print("Done!")
                received_integers = []
                comp_vision('fuck_it_we_ball.jpeg', 'final_contours.jpeg')
            #elif (received_integers):
            #    print(f"last in array is {bytes([received_integers[-1]])} and second to last is {bytes([received_integers[-2]])}. should be {bytes([217])} and {bytes([255])}")   

        # Only demo the first device found
        #break #TODO For now we break after first one