import cv2
import numpy as np

# reading image
img = cv2.imread('../sample3_3_3v.jpeg')
cv2.imshow("OG", img)
cv2.waitKey(0)

#hsv for white color detection and mask generation
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
white_lower = np.array([0,0,0]) #000
white_upper = np.array([30,255,255]) #30,255,255
mask = cv2.inRange(hsv, white_lower, white_upper)

cv2.imshow("Mask", mask)
cv2.waitKey(0)

#noise filtering for mask
kernel = np.ones((7,7),np.uint8)
#mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) #EXPERIMENTAL
#mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
cv2.imshow("Mask -filtered", mask)
cv2.waitKey(0)

#mask application
segmented_image = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow("Masked image", segmented_image)
cv2.waitKey(0)

# converting image into grayscale and blurred image
gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY) #required for transforms, and reduces math
blur = cv2.GaussianBlur(gray, (7,7), 0) #7x7 is the kernel used. Used for noise reduction

cv2.imshow("blurred image", blur)
cv2.waitKey(0)

#find circles in masked image -> white circules
# Old values 140 22
circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1.5, 15, param1=200
           ,param2=27, minRadius=17, maxRadius=35)

circles = np.uint16(np.around(circles))

radius = 0
x = 0
y = 0
white_parameter = 150 #trial and error
#draw circles
if circles is not None:
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
cv2.imshow("Ball detection -segmented", segmented_image)
cv2.waitKey(0)

#crop and show cue ball
if(x):
    lowX =  x - radius +3 #the plus 3 are so that we ensure only the ball is visible, its the reverse of a buffer
    highX = x + radius -3
    lowY = y - radius  +3
    highY = y + radius -3
    print(f'The coordinates are {lowX}: {highX} and {lowY}: {highY}')
    cropped_image = img[lowY: highY, lowX: highX]
    cv2.imshow("cropped image", cropped_image)
    cv2.waitKey(0)
    
    #hsv for red color detection
    hsv_laser = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    
    #pink mask
    red_lower = np.array([155,0,0]) #155 0 0
    red_upper = np.array([180,120,255]) #180 120 255
    mask_laser = cv2.inRange(hsv_laser, red_lower, red_upper)

    cv2.imshow("Mask for Laser", mask_laser)
    cv2.waitKey(0)

    #noise filtering for mask
    kernel_laser = np.ones((2,2),np.uint8)
    mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_CLOSE, kernel_laser) #EXPERIMENTAL
    #mask_laser = cv2.morphologyEx(mask_laser, cv2.MORPH_OPEN, kernel_laser) 
    cv2.imshow("Mask -filtered Laser", mask_laser)
    cv2.waitKey(0)

    #mask application
#    segmented_image_laser = cv2.bitwise_and(cropped_image, cropped_image, mask=mask_laser)
#    cv2.imshow("Masked image Laser", segmented_image_laser)
#    cv2.waitKey(0)

#    segmented_image_gray_laser = cv2.cvtColor(segmented_image_laser, cv2.COLOR_BGR2GRAY)
#    cv2.imshow(" Gray Masked image Laser", segmented_image_gray_laser)
#    cv2.waitKey(0)

#    circles_laser = cv2.HoughCircles(segmented_image_gray_laser, cv2.HOUGH_GRADIENT, 1.5, 5, param1=210
#           ,param2=4, minRadius=2, maxRadius=7)
    
    laser_x = 0
    laser_y = 0
    laser_found = False
    lowest_G = 255
    lowest_B = 255
    #gray_ball = cv2.cvtColor(cropped_image,cv2.COLOR_BGR2GRAY)
    #cv2.imshow("grayball", gray_ball)
    #cv2.waitKey(0)
    #thresh = cv2.adaptiveThreshold(gray_ball, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 0)
    #cv2.imshow("threshold", thresh)
    #cv2.waitKey(0)

    contours, hier = cv2.findContours(mask_laser, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        M = cv2.moments(i)
        if M['m00'] != 0:
            #cv2.drawContours(cropped_image, [i], -1, (255,0,0), 2)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            if(cropped_image[cy][cx][0] < lowest_B and cropped_image[cy][cx][1] < lowest_G #must be the reddest thing
               and cropped_image[cy][cx][0] >135 and cropped_image[cy][cx][1] >135): #prevents detecting table as well
                laser_x = cx
                laser_y = cy
                laser_found = True
                lowest_B = cropped_image[cy][cx][0]
                lowest_G  =cropped_image[cy][cx][1]
            cv2.circle(cropped_image, (cx,cy),1, (0,0,0), -1)
    if(laser_found):
        cv2.circle(cropped_image, (laser_x,laser_y),1, (0,255,0), -1)
        laser_x = (laser_x/(highX - lowX)* 30.0 - 15.0)//1.0
        laser_y = (-(laser_y/(highY - lowY)* 30.0) + 15.0)//1.0   
        print(f'The LASER coordinates are ({laser_x},{laser_y})')
    else:
        print("No laser found")
    
    cv2.imshow("Contours", cropped_image)
    cv2.waitKey(0)

    
#    if circles_laser is not None:
#        circles_laser = np.uint16(np.around(circles_laser))
#        for i in circles_laser[0,:]:
#            if (not (cropped_image[i[1]][i[0]][0] > 180 and cropped_image[i[1]][i[0]][1] > 180) #if not white pixel
#                 and (cropped_image[i[1]][i[0]][0] > 130 and cropped_image[i[1]][i[0]][1] > 130)): #and not table 
#                cv2.circle(cropped_image,(i[0],i[1]), i[2], (0,0,0), 1)
#                cv2.circle(segmented_image_gray_laser,(i[0],i[1]), i[2], (255,0,0), 1)
#                print(f'LASER. x is {i[0]} and y is {i[1]}')
#                laser_x = (i[0]/(highX - lowX)* 30.0 - 15.0)//1.0
#                laser_y = (-(i[1]/(highY - lowY)* 30.0) + 15.0)//1.0
#            else:
#                print('white, so probably in cue ball')
#                cv2.circle(cropped_image,(i[0],i[1]), i[2], (0,0,255), 1)

#    #show circles
#    cv2.imshow(" circles +Gray Masked image Laser", segmented_image_gray_laser)
#    cv2.waitKey(0)

    #show laser
#    cv2.imshow("Laser", cropped_image)
#    cv2.waitKey(0)
    
    
else:
    print('no balls found!')



#exit
cv2.destroyAllWindows()