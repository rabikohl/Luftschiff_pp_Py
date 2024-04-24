import socket #pip install sockets
import RPi.GPIO as GPIO # sudo apt-get install rpi.gpio
import smbus #pip install smbus
import math


def read_byte(reg):
    return bus.read_byte_data(address, reg)


def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


def runAccel():
    print("Gyroskop")
    print("--------")

    gyroskop_xout = read_word_2c(0x43)
    gyroskop_yout = read_word_2c(0x45)  # V02
    gyroskop_zout = read_word_2c(0x47)

    B = gyroskop_xout, gyroskop_yout, gyroskop_zout

    print("gyroskop_xout: "), ("%5d" % gyroskop_xout), (" skaliert: "), (gyroskop_xout / 131)
    print("gyroskop_yout: "), ("%5d" % gyroskop_yout), (" skaliert: "), (gyroskop_yout / 131)
    print("gyroskop_zout: "), ("%5d" % gyroskop_zout), (" skaliert: "), (gyroskop_zout / 131)

    print()
    print("Beschleunigungssensor")
    print("---------------------")

    beschleunigung_xout = read_word_2c(0x3b)
    beschleunigung_yout = read_word_2c(0x3d)
    beschleunigung_zout = read_word_2c(0x3f)

    beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
    beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
    beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0

    A = beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert
    print("beschleunigung_xout: "), ("%6d" % beschleunigung_xout), (" skaliert: "), beschleunigung_xout_skaliert
    print("beschleunigung_yout: "), ("%6d" % beschleunigung_yout), (" skaliert: "), beschleunigung_yout_skaliert
    print("beschleunigung_zout: "), ("%6d" % beschleunigung_zout), (" skaliert: "), beschleunigung_zout_skaliert

    print("X Rotation: "), get_x_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert,
                                          beschleunigung_zout_skaliert)
    print("Y Rotation: "), get_y_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert,
                                          beschleunigung_zout_skaliert)

    return A, B


def valCheckDir(value):
    if value > 100:
        value = 100
        return 1, (value), abs(value)
    elif value < -100:
        value = -100
        return 0, (value), abs(value)
    elif value >= 0:
        return 1, (value), abs(value)
    elif value < 0:
        return 0, (value), abs(value)

bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68  # via i2cdetect

def main():
    # Register
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    
    print("Server is running...")
    # Aktivieren, um das Modul ansprechen zu koennen
    bus.write_byte_data(address, power_mgmt_1, 0)

    HOST = "192.168.137.139"  # Use IP-address of device running server instance!!!
    # HOST = "localhost"  # Use this for debugging (launching client & server on same machine) only!!!
    PORT = 5000  # Change this if necessary to other value

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        conn, addr = s.accept()

        while True:

            print(f"Connected by {addr}")

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(12, GPIO.OUT)  # PWM 0
            GPIO.setup(13, GPIO.OUT)  # PWM
            GPIO.setup(16, GPIO.OUT)

            # 6, 15, 26
            GPIO.setup(6, GPIO.OUT)  # links
            GPIO.setup(15, GPIO.OUT)  # rechts
            GPIO.setup(26, GPIO.OUT)  # obenunten

            p12 = GPIO.PWM(12, 100)  # links
            p13 = GPIO.PWM(13, 100)  # rechts
            p16 = GPIO.PWM(16, 100)  # hochrunter

            motorLeft = 0
            motorRight = 0
            motorUpDown = 0
            dirMotorLeft = 1  # 0 back 1 fw ,, 6,15,26
            dirMotorRight = 1
            dirMotorUpDown = 1
            writeLeft = 0
            writeRight = 0
            writeUpDown = 0

            step = 5

            print("Waiting for values...")
            val = conn.recv(6).decode()
            print("Values received: ", val)
            if val == 'w':
                motorLeft += step
                motorRight += step
            elif val == 's':
                motorLeft -= step
                motorRight -= step
            elif val == 'a':
                motorLeft -= step
                motorRight += step
            elif val == 'd':
                motorLeft += step
                motorRight -= step
            elif val == '2':
                motorUpDown -= step
            elif val == '8':
                motorUpDown += step
            elif val == 'SPACE':
                motorUpDown = 0
                x = int((motorLeft + motorRight) / 2)
                motorRight = x
                motorLeft = x
            elif val == 'BYE':
                motorRight = 0
                motorLeft = 0
                motorUpDown = -150
                print("Asked to close server.")
                break
            elif val == '0':
                motorLeft = 0
                motorRight = 0
                motorUpDown = 0

            dirMotorLeft, motorLeft, writeLeft = valCheckDir(motorLeft)
            dirMotorRight, motorRight, writeRight = valCheckDir(motorRight)
            dirMotorUpDown, motorUpDown, writeUpDown = valCheckDir(motorUpDown)

            print("%s %i motorLeft %s %i motorRight %s %i motorUpDown" % (
                motorLeft, dirMotorLeft, motorRight, dirMotorRight, motorUpDown, dirMotorUpDown))
            # print("%s writeLeft %s writeRight %s writeUpDown" %(writeLeft,writeRight,writeUpDown))

            GPIO.output(6, dirMotorLeft)
            GPIO.output(15, dirMotorRight)
            GPIO.output(26, dirMotorUpDown)

            p12.start(writeLeft)
            p13.start(writeRight)
            p16.start(writeUpDown)

        conn.close()

        print("Ready to shut down...")
        s.shutdown(socket.SHUT_RDWR)
        s.close()


if __name__ == "__main__":
    main()
