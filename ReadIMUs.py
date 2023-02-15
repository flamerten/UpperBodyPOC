# Running this file will read the 6 IMUs when the button is pressed.
# Button is push button, so some debouncing is needed.

import time

from adafruit_lsm6ds import Rate, AccelRange, GyroRange
from adafruit_lsm6ds import ISM330DHCT as Sensor
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

#Scan for the sensors connected and add it to the list
sensors = []
for channel in range(8):
    if tca[channel].try_lock():
        addresses = tca[channel].scan()
        for address in addresses:
            if address != 0x70:
                sensors.append(str(channel) + "-" + str(hex(address)))
        tca[channel].unlock()


print("Sensors connected to TCA")
for sensor in sensors:
    print(sensor)

#while(trigger.value == 0):
#    time.sleep(0.1)
