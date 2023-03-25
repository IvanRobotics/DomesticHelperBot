from pycreate2 import Create2
import time
import serial

# initialize variables and ports
port = "/dev/ttyUSB0"
bot = Create2(port)
ser = serial.Serial(port, baudrate = 115200)
sensors = bot.get_sensors()
wheel2center = 113.5
wheelSpeed = 200
forwardSpeed = 100
singleWheelTime = 3.1415926 * wheel2center / wheelSpeed
tolerance = singleWheelTime * 0.05
singleWheelTime = singleWheelTime + tolerance
move = 0


def displayBatteryLife(flag):
    if flag == 1:
        print('battery', sensors.battery_capacity*100/3000,'%')
    else:
        print(' ')
def beep(song_num):
    Song = []
    song0 = [59, 64, 62, 32, 69, 96, 67, 64, 62, 32, 60, 96, 59, 64, 59, 32, 59, 32, 60, 32, 62, 32, 64, 96, 62, 96]
    song1 = [76, 16, 76, 16, 76, 32, 76, 16, 76, 16, 76, 32, 76, 16, 79, 16, 72, 16, 74, 16, 76, 32, 77, 16, 77, 16, 77, 16, 77, 32, 77, 16]
    song2 = [76, 12, 76, 12, 20, 12, 76, 12, 20, 12, 72, 12, 76, 12, 20, 12, 79, 12, 20, 36, 67, 12, 20, 36]
    song3 = [72, 12, 20, 24, 67, 12, 20, 24, 64, 24, 69, 16, 71, 16, 69, 16, 68, 24, 70, 24, 68, 24, 67, 12, 65, 12, 67, 48]
    Song.append(song0)
    Song.append(song1)
    Song.append(song2)
    Song.append(song3)

    # song number can be 0-3
    bot.createSong(song_num, Song[song_num])
    time.sleep(0.1)
    songDuration = bot.playSong(song_num)
    time.sleep(songDuration)
    
    
def getbumpSensor():
    ser.write(b'\x8E\x07')
    time.sleep(0.2)
    while ser.inWaiting()!=0:
        response = []
        response.append(hex(ord(ser.read())))
        if int(response[0],16)>0:
            return 1
        else:
            return 0

def driveForward(forwardSpeed):
    #roomba travels straight
    bot.drive_direct(forwardSpeed,forwardSpeed)
    time.sleep(5)
    
def driveBackward(forwardSpeed):
    #roomba travels straight
    bot.drive_direct(-forwardSpeed,-forwardSpeed)
    time.sleep(5)
 
def Uturn(wheelSpeed):
    bot.drive_direct(wheelSpeed, -wheelSpeed)
    time.sleep(singleWheelTime)
    

 ###################################
    #Program starts#
bot.start()
bot.safe()
#bot.full()
move = 1
time.sleep(0.1)
print(sensors.light_bumper)

while move:
# roobma drives straight
    beep(2)
    driveForward(forwardSpeed)
    
    if sensors.light_bumper_left <=5 or sensors.light_bumper_right <=5:
       beep(1)
       
    print('left', sensors.light_bumper_left, 'right',sensors.light_bumper_right)
    #roobma turns 180 degrees
    Uturn(wheelSpeed)
    #roomba travles straight
    driveForward(forwardSpeed)
    
    
    
    
    #roomba turns 180 degrees
    Uturn(wheelSpeed)
    #roomba stops
    bot.drive_stop()
    # play singal song - stop 
    beep(3)
    #display battery life
    displayBatteryLife(1)

    
    
    #print(sensors.light_bumper)
    move = 0

print('program ends')
