# Running this file will read the 6 IMUs when the button is pressed.
# Button is push button, so some debouncing is needed.

import time

from adafruit_lsm6ds import Rate, AccelRange, GyroRange
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX #refer to https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/examples/lsm6ds_ism330dhcx_simpletest.py
import adafruit_tca9548a
import board
import busio
import numpy as np
import digitalio
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

Comp_Freq = 40 #Hz > reco based on no. sensors
Sample_Delay = 1/40

BUTTON = board.D21

trigger = digitalio.DigitalInOut(BUTTON)
trigger.direction = digitalio.Direction.INPUT
trigger.pull = digitalio.Pull.DOWN
trigger_status = False #initially system does not record unless pressed

i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)


def RecordSensors():
    #Scan for the sensors connected and return a list of Sensor Objects
    SensorObjects = []
    SensorNames = [] #useful for debugging
    for channel in range(8):
        if tca[channel].try_lock():
            addresses = tca[channel].scan()
            for addr in addresses:
                print(str(channel)+":"+str(hex(addr)) + "found")
                if addr != 0x70:
                    Sensor = ISM330DHCX(tca[channel],address = const(hex(addr)))
                    SensorObjects.append(Sensor)
                    SensorNames.append(str(channel) + "-" + str(hex(addr)))

    for n in SensorNames:
        print(n)
    
    return SensorObjects

"""
    for channel in range(0,3):
        Sensor1 = ISM330DHCX(tca[channel],address = const(0x6A))
        Sensor2 = ISM330DHCX(tca[channel],address = const(0x6B))

        SensorObjects.append(Sensor1)
        SensorObjects.append(Sensor2)
        SensorNames.append(str(channel) + "-" + "0x6A")
        SensorNames.append(str(channel) + "-" + "0x6B")
"""

def CalibrateSensors(SensorObjects):
    #move this to a helper file?
    count = 30
    no_sensors = 6
    #Calculate gyro offsets and add it to a npy file
    Offsets = np.zeros(3 * no_sensors)
    for i in range(count):
        res = ()
        for Sensor in SensorObjects:
            res = res + Sensor.gyro

        print(i,res)
        Offsets = Offsets + np.array(res)
        time.sleep(Sample_Delay)
    
    Offsets = Offsets/count #divide by the average
    print("Gyro offset calculation")
    print(Offsets)
    np.save('calibration/gyro_offset.npy',Offsets)



SensorObjects = RecordSensors()

time.sleep(2)

#Try to collect data for first sensor
for i in range(len(SensorObjects)):
    sensor = SensorObjects[i]
    print("Sensor " + str(i), end = "")
    print("Accel: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration), end = "")
    print("Gyro:  X:%.2f, Y: %.2f, Z: %.2f rad/s" % (sensor.gyro), end = "")
    print("")
    time.sleep(0.5)

#CalibrateSensors(SensorObjects)


#while(trigger.value == 0):
#    time.sleep(0.1)
