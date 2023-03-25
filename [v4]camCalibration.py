import time
import cv2
import numpy as np
import threading
from Arm_Lib import Arm_Device
import speech_recognition as sr 
from pycreate2 import Create2
import time
import serial
from Arm_Lib import Arm_Device


Arm = Arm_Device()
def arm_move_6(p, s_time = 500):
    for i in range(6):
        id = i + 1
        Arm.Arm_serial_servo_write(id, p[i], s_time)
        time.sleep(.01)
    time.sleep(s_time/1000)
def CamCalibration(colorinput ='yellow', previewName ='None', camID = 2):
    #cv2.namedWindow(previewName)
    look_at = [90, 90, 25, 25, 90, 30]
    arm_move_6(look_at, 1000)
    time.sleep(1)
    cap = cv2.VideoCapture(camID)
    camID = int(camID)
    if camID  == 0:
        print('robot arm camera is activated')
        initial_angle  = 90
        x_bias = 130
        rad_bias = 30
        x_now = 0
        x_mid= 320
        rad_now = 0
        rad_mid = 70
        control_flag = 0
        xmin = 314
        xmax = 326
    
    if camID  == 2:
        print('roomba camera is activated')
        initial_angle  = 90
        x_bias = 100
        rad_bias = 30
        x_now = 0
        rad_now = 0
        rad_mid = 70
        xmin = 310
        xmax = 330
        
        
    while True:
        #cv2.imshow(previewName, frame)
        rval, frame = cap.read()
        frame = cv2.rectangle(frame, (260,180), (380, 300),(255, 255, 255), 1)
        frame = cv2.rectangle(frame, (xmin,0), (xmax,480),(255,255,255),1)
        ########################image processing###########################
        Gaussian = cv2.GaussianBlur(frame, (5, 5), 0)
        hsvspace = cv2.cvtColor(Gaussian, cv2.COLOR_BGR2HSV)
        lower = np.zeros(3)
        upper = np.zeros(3)
        
        if colorinput  == 'green':
            lower = np.array([35, 43, 35])
            upper = np.array([90, 255, 255])
            
        
        if colorinput =='yellow':
            lower = np.array([25, 50, 70])
            upper = np.array([35, 255, 255])
           

        if colorinput =='red':
            lower = np.array([160, 100, 20])
            upper = np.array([179, 255, 255])
            

        whiteandblack = cv2.inRange(hsvspace, lower, upper)
        kernal = np.ones((3,3))
        smoothresult = cv2.erode(whiteandblack, kernal, iterations=2)
        contour = cv2.findContours(smoothresult.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        if len(contour) > 0:
            area = max(contour, key=cv2.contourArea)
            (x, y), rad = cv2.minEnclosingCircle(area)
            if int(rad)> 20 and camID == 0:
                x_now = x
                rad_now = rad
                print(f'x:{x}, y:{y}, rad:{rad}')
                
                
    ############################control##################################
                if camID == 0:
                    if x_now  < xmin:
                        print('lefttward!')
                        
                        Arm.Arm_serial_servo_write(1, initial_angle, 1000)
                        initial_angle+= 0.5
                        time.sleep(0.5)
                        
                        
                    elif x_now > xmax:
                        
                        #initial_angle -=1
                        print('rightward!')
                        Arm.Arm_serial_servo_write(1, initial_angle, 1000)
                        initial_angle-=0.5
                        time.sleep(0.5)
                        
                    
                    elif x_now <xmax and x_now > xmin:
                        print('grab the object')
                        grab()
                        time.sleep(1)
                        print('passing the object')
                        passing()
                        time.sleep(1)
                        break
                    
            if int(rad) > 20 and int(rad) <=100 and camID == 2:
                x_now = x
                rad_now = rad
                print(f'x:{x}, y:{y}, rad:{rad}')
                
                
    ############################control##################################
                                
                if camID == 2:
                        if x_now + x_bias < xmin   :
                            print('turn right')
                            rightTurn(10, 0.1)
                            
                            
                        elif x_now > xmax + x_bias:
                            print('turn left')
                            leftTurn(10, 0.1)
                            
                            
                        
                        elif x_now <xmax + x_bias and x_now + x_bias > xmin:
                            print('driving forward')
                            driveForward(forwardSpeed, 5)
                        
                            
            if int(rad)>100 and int(rad)<= 120 and  camID == 2:
                    print('roomba slows down to 40')
                    driveForward(40,2)
                    time.sleep(1)
                    
            if int(rad)>120 and camID == 2:
                    print('roomba slows down to 30')
                    driveForward(30,2)
                    time.sleep(1)
                    
                    Car_Stop()
                    print('roomba has arrived at the toolbox')
                    time.sleep(1)
                    break
                    
                    
                    
            else:
                time.sleep(1)
                print('Nothing detect!')
                print('please calibrate the camera to find the color!')
                
                
                
        else:
            pass
        
        
                
            
        ####################For Testing########################################
        cv2.imshow('frame', frame)
        #cv2.imshow('Gaussian',Gaussian)
        #cv2.imshow('whiteandblack',whiteandblack)
        #cv2.imshow('smoothresult',smoothresult)
            
        key = cv2.waitKey(20)
        if key == 27:
            break   
      
    cap.release()
    cv2.destroyAllWindows()
    
CamCalibration()
