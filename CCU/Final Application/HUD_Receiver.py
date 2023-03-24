from BLE_Functions import *
import Settings
import struct
import threading
import time 
import sys
import random
import cv2
import numpy as np

def comp_vision(image_path, final_image_name):
    # Read image from file path
    img = cv2.imread(image_path)
   
    if img is None:
        print('No image found')
        return
    
    # HSV for white color detection and mask generation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    black_lower = np.array([0,0,0]) #0,90,0
    black_upper = np.array([180,255,150]) #12,255,150
    mask = cv2.inRange(hsv, black_lower, black_upper)

    # Noise filtering for mask
    kernel = np.ones((7,7),np.uint8)

    # Mask application
    segmented_image = cv2.bitwise_and(img, img, mask=mask)

    # Converting image into grayscale and blurred image
    gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY) #required for transforms, and reduces math
    blur = cv2.GaussianBlur(gray, (3,3), 0) #7x7 is the kernel used. Used for noise reduction

    # Find circles in masked image -> black circle
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.75 , 30, param1=250
            ,param2=28, minRadius=10, maxRadius=35) #min radius was 17

    radius = 0
    x = 0
    y = 0
    potential_balls = []

    # Find potential black balls
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

    # Find cue ball from potential black balls, then crop and show cue ball
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

        
        # HSV for green color detection
        hsv_laser = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        
        #pink mask
        green_lower = np.array([35,0,150]) #155 0 0
        green_upper = np.array([75,255,255]) #180 120 255
        mask_laser = cv2.inRange(hsv_laser, green_lower, green_upper)

        # Noise filtering for mask
        kernel_laser = np.ones((2,2),np.uint8)
        mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_CLOSE, kernel_laser) #EXPERIMENTAL

        laser_x = 0
        laser_y = 0
        laser_found = False
        biggest_G = 0

        contours, hier = cv2.findContours(mask_laser, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i in contours:
            M = cv2.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                pixel_val_g = cropped_image[cy][cx][1]
                pixel_val_b = cropped_image[cy][cx][0]
                pixel_val_r =cropped_image[cy][cx][2]
                cv2.circle(cropped_image, (cx,cy),1, (0,0,0), -1)
                if (pixel_val_g > biggest_G # must be the greenest thing
                and pixel_val_g >80 and pixel_val_b >80): # prevents detecting table as well
                    laser_x = cx
                    laser_y = cy
                    laser_found = True
                    biggest_G  =cropped_image[cy][cx][1]
                    cv2.circle(cropped_image, (cx,cy),1, (0,255,0), -1)
                else:
                    print(f'BGR is {cropped_image[cy][cx][0]} {cropped_image[cy][cx][1]} {cropped_image[cy][cx][2]}')
        if (laser_found):
            cv2.circle(cropped_image, (laser_x,laser_y),1, (0,255,0), -1)
            laser_x = (laser_x/(highX - lowX)* 30.0 - 15.0)//1.0
            laser_y = (-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0   
            Settings.actual_x = int(laser_x)
            Settings.actual_y = int(laser_y)
            print(f'The LASER coordinates are ({laser_x},{laser_y})')
            cv2.imwrite(final_image_name, cropped_image)
            return (Settings.actual_x, Settings.actual_y)
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
                Settings.actual_x = laser_x
                Settings.actual_y = laser_y
                return (Settings.actual_x, Settings.actual_y)
            else:
                print('No laser found at all')
                return (50,0)

    else:
        print('no balls found!')
        return (50,0)
    
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
    
    # Append bytes in specific order
    if (len(value) > 7):
        Settings.received_integers.append(value[7])
    if (len(value) > 6):
        Settings.received_integers.append(value[6])
    if (len(value) > 5):
        Settings.received_integers.append(value[5])
    if (len(value) > 4):
        Settings.received_integers.append(value[4])
    if (len(value) > 3):
        Settings.received_integers.append(value[3])
    if (len(value) > 2):
        Settings.received_integers.append(value[2])
    if (len(value) > 1):
        Settings.received_integers.append(value[1])
    if (len(value) > 0):
        Settings.received_integers.append(value[0])
    if (len(value) > 15):
        Settings.received_integers.append(value[15])
    if (len(value) > 14):
        Settings.received_integers.append(value[14])
    if (len(value) > 13):
        Settings.received_integers.append(value[13])
    if (len(value) > 12):
        Settings.received_integers.append(value[12])
    if (len(value) > 11):
        Settings.received_integers.append(value[11])
    if (len(value) > 10):
        Settings.received_integers.append(value[10])
    if (len(value) > 9):
        Settings.received_integers.append(value[9])
    if (len(value) > 8):
        Settings.received_integers.append(value[8])
    if (len(value) > 19):
        Settings.received_integers.append(value[19])
    if (len(value) > 18):
        Settings.received_integers.append(value[18])
    if (len(value) > 17):
        Settings.received_integers.append(value[17])
    if (len(value) > 16):
        Settings.received_integers.append(value[16])

    if (Settings.received_integers and bytes([Settings.received_integers[-1]]) == bytes([217]) and bytes([Settings.received_integers[-2]]) == bytes([255])):
        with open(f"HUD_receiver_test_{Settings.image_counter}.jpeg", "wb") as fp:
            for integer in Settings.received_integers:
                fp.write(bytes([integer]))
        print("Done!")
        comp_vision(f"HUD_receiver_test_{Settings.image_counter}.jpeg", f"HUD_receiver_test_contours_{Settings.image_counter}.jpeg")
        Settings.received_integers = []
        Settings.image_counter += 1