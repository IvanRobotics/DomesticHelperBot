
import time
import cv2
import numpy as np
from Arm_Lib import Arm_Device
import speech_recognition as sr  

Arm = Arm_Device()

w = 640
h = 480
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

x_bias = 130
rad_bias = 30
x_now = 0
x_mid= 320
rad_now = 0
rad_mid = 70
control_flag = 0
xmin = 314
xmax = 326

def initialPos():
    
    #initial position
    look_at = [90, 135, 0, 0, 90, 30]
    arm_move_6(look_at, 1000)
    time.sleep(1)

def arm_move_6(p, s_time = 500):
    for i in range(6):
        id = i + 1
        Arm.Arm_serial_servo_write(id, p[i], s_time)
        time.sleep(.01)
    time.sleep(s_time/1000)

  
def Car_Stop():
    pass

def grab():
#                     5    4   3   2 
    servoAngle2_5 = [270, 75, 60 , 15]
    count = 5
    for angle in servoAngle2_5: 
        print(count, angle)
        Arm.Arm_serial_servo_write(count, angle, 1000)
        time.sleep(1)
        count -=1
    Arm.Arm_serial_servo_write(6, 180, 1000)      

def passing():
     
 
    tick = 2
 #                2   3   4  5   6
    servoAngle = [90, 90, 60, 90, 180]
    for ang in servoAngle:
        print(tick, ang)
        Arm.Arm_serial_servo_write(tick, ang, 1000)
        time.sleep(1)
        tick +=1
        
def release():
    
    Arm.Arm_serial_servo_write(6, 0, 1000)
    time.sleep(1)
    
def run(colorinput):
    
    #observation position

    look_at = [90, 90, 25, 25, 90, 30]
    arm_move_6(look_at, 1000)
    time.sleep(1)
    
    global x_bias
    global rad_bias
    global x_now
    global y_now
    global rad_now
    global control_flag
    global initial_angle 
    
    
    

    
    initial_angle  = 90
    while True:
        _, frame = cap.read()
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
            lower = np.array([0, 50, 70])
            upper = np.array([9, 255, 255])
            

        whiteandblack = cv2.inRange(hsvspace, lower, upper)
        kernal = np.ones((3,3))
        smoothresult = cv2.erode(whiteandblack, kernal, iterations=2)
        contour = cv2.findContours(smoothresult.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(contour) > 0:
            area = max(contour, key=cv2.contourArea)
            (x, y), rad = cv2.minEnclosingCircle(area)
            if int(rad) > 20:
                control_flag = 1
                x_now = x
                rad_now = rad
                print('x: ', int(x_now), 'y :', int(y))
                
                
############################control##################################
                if control_flag == 1:
                    if x_now  < xmin:
                        #initial_angle+=1
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
                        control_flag =2
                        
                        
                if control_flag == 2:
                    print('grab the object')
                    grab()
                    time.sleep(1)
                    print('passing the object')
                    passing()
                    time.sleep(1)
                    break
                        

                        
            else:
                control_flag = 0
                print('Nothing dect!')
                Car_Stop()
        else:
            pass
            
        
        ####################For Testing########################################
        cv2.imshow('frame', frame)
        #cv2.imshow('Gaussian',Gaussian)
        #cv2.imshow('whiteandblack',whiteandblack)
        #cv2.imshow('smoothresult',smoothresult)
        ####################Quit#######################################
        if cv2.waitKey(5) & 0xFF == 27: #ESC
                break
######################shut down everything, close windows#########################
def destroy():
    Car_Stop()
   
    
    cap.release()
    cv2.destroyAllWindows()
    
    
    
    
    
if __name__ == '__main__':


    r =sr.Recognizer()  
    r.energy_threshold = 6000
    
    mic= sr.Microphone()
    commandLibrary = ['green', 'yellow','red','exit','release']
    colorLibrary = ['green', 'yellow','red']
    initialPos()
    
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source,duration =0.5)
            print('speak')
            audio = r.listen(source)
            #time.sleep(0.1)  
            
        try:
            print("You said " + r.recognize_google(audio, language ='en-US'))
            userinput = str(r.recognize_google(audio))
            userinput = userinput.lower()
            if userinput in commandLibrary:
                Arm.Arm_Buzzer_On(1)
                if userinput in colorLibrary:
                    print('Your input is ', userinput )
                    run(userinput)
                
                if userinput =='release':
                    release()
                    time.sleep(10)
                    initialPos()
                    
                if userinput =='exit':
                    initialPos()
                    break
                    
            else:
                print('Enter the correct input: ', commandLibrary)
                audio = r.listen(source) 
                
            print('system completed')
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except KeyboardInterrupt:
            destroy()
            
            
