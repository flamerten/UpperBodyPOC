# Running this file will read the 6 IMUs when the button is pressed.
# Button is push button, so some debouncing is needed.

import time

from adafruit_lsm6ds import Rate, AccelRange, GyroRange
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX #refer to https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/examples/lsm6ds_ism330dhcx_simpletest.py
import adafruit_tca9548a
import board
import busio
import digitalio
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

BUTTON = board.D21

trigger = digitalio.DigitalInOut(BUTTON)
trigger.direction = digitalio.Direction.INPUT
trigger.pull = digitalio.Pull.DOWN
trigger_status = False #initially system does not record unless pressed

i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)

#Scan for the sensors connected and add the objects to the list
SensorObjects = []
SensorNames = []

for channel in range(0,3):
    Sensor1 = ISM330DHCX(tca[channel],address = const(0x6A))
    Sensor2 = ISM330DHCX(tca[channel],address = const(0x6B))

    SensorObjects.append(Sensor1)
    SensorObjects.append(Sensor2)
    SensorNames.append(str(channel) + "-" + "0x6A")
    SensorNames.append(str(channel) + "-" + "0x6B")

"""
for channel in range(8):
    if tca[channel].try_lock():
        addresses = tca[channel].scan()
        for address in addresses:
            if address == 0x6a or address == 0x6b: #6b when jumpers soldered, else 6b
                Sensor = ISM330DHCX(tca[channel],address)
                SensorObjects.append(str(Sensor))
                SensorNames.append(str(channel) + "-" + str(hex(address)))
        tca[channel].unlock()
"""


print("Sensors connected to TCA")
for name in SensorNames:
    print(name)

time.sleep(2)

#Try to collect data for first sensor

sensor = SensorObjects[0]
for i in range(20):
    print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
    print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
    print("")
    time.sleep(0.5)


#while(trigger.value == 0):
#    time.sleep(0.1)
