import socket
import RPi.GPIO as GPIO

host = "localhost"
port = 5000

s = socket.socket()
s.bind((host, port))
s.listen(1)
print("Server is listening")

c, addr = s.accept()


def valCheckDir(value):
    if value > 100 :
        value = 100
        return 1, (value), abs(value)
    elif value < -100:
        value = -100
        return 0, (value), abs(value)
    elif value >= 0:
        return 1, (value), abs(value)
    elif value < 0:
        return 0, (value), abs(value)
    
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)# PWM 0
GPIO.setup(13, GPIO.OUT)# PWM
GPIO.setup(16, GPIO.OUT)

#6, 15, 26
GPIO.setup(6, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

p12 = GPIO.PWM(12, 100)
p13 = GPIO.PWM(13, 100)
p16 = GPIO.PWM(16, 100)

motorLeft = 0
motorRight = 0
motorUpDown = 0
dirMotorLeft = 1    #0 back 1 fw ,, 6,15,26
dirMotorRight = 1
dirMotorUpDown = 1
writeLeft =0
writeRight = 0
writeUpDown =0

step = 5

while True:
    val = c.recv(6).decode()
    if val == 'w':
        motorLeft += step
        motorRight += step
    elif val =='s':
        motorLeft -= step
        motorRight -=step
    elif val == 'a':
        motorLeft -=step
        motorRight +=step
    elif val == 'd':
        motorLeft += step
        motorRight -= step
    elif val == '2':
        motorUpDown -= step
    elif val == '8':
        motorUpDown += step
    elif val == 'SPACE':
        motorUpDown = 0
        x = int((motorLeft+motorRight)/2)
        motorRight = x
        motorLeft = x
    elif val == 'BYE':
        motorRight = 0
        motorLeft = 0
        motorUpDown = -150
        print("Asked to close server.")
        s.close()
        s.detach()
    elif val == '0':
        motorLeft = 0
        motorRight = 0
        motorUpDown = 0
        
    dirMotorLeft, motorLeft, writeLeft = valCheckDir(motorLeft)
    dirMotorRight, motorRight, writeRight = valCheckDir(motorRight)
    dirMotorUpDown, motorUpDown, writeUpDown = valCheckDir(motorUpDown)

    print("%s %i motorLeft %s %i motorRight %s %i motorUpDown" %(motorLeft, dirMotorLeft,motorRight, dirMotorRight,motorUpDown, dirMotorUpDown))
    #print("%s writeLeft %s writeRight %s writeUpDown" %(writeLeft,writeRight,writeUpDown))

    GPIO.output(6, dirMotorLeft)
    GPIO.output(15, dirMotorRight)
    GPIO.output(26, dirMotorUpDown)

    p12.start(writeLeft)
    p13.start(writeRight)
    p16.start(writeUpDown)

