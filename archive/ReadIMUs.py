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
import os

#Wiring - maybe should import it instead if here
#rot_type, label, tca channel + i2c option
sensor_map = (
    (0,'pelvis_imu'    ,'0'),
    (0,'torso_imu'     ,'0b'),
    (1,'femur_l_imu'   ,'9'),
    (1,'tibia_l_imu'   ,'9'),
    (3,'calcn_l_imu'   ,'9'),
    (2,'femur_r_imu'   ,'9'),
    (2,'tibia_r_imu'   ,'9'),
    (3,'calcn_r_imu'   ,'9'),
    (1,'humerus_l_imu' ,'1'),    #Bicep
    (1,'ulna_l_imu'    ,'1b'),   #Forearm
    (1,'hand_l_imu'    ,'9'),
    (2,'humerus_r_imu' ,'2'),
    (2,'ulna_r_imu'    ,'2b'),
    (2,'hand_r_imu'    ,'9'),
)

#Sensor Map Helper
rate = 40 #Hz > reco based on no. sensors
Sample_Delay = 1/rate
calibrate_sensors = True


BUTTON = board.D21

trigger = digitalio.DigitalInOut(BUTTON)
trigger.direction = digitalio.Direction.INPUT
trigger.pull = digitalio.Pull.DOWN
trigger_status = False #initially system does not record unless pressed

i2c = busio.I2C(board.SCL, board.SDA)
tca = adafruit_tca9548a.TCA9548A(i2c)


def RecordSensors(init_time,signals_per_sensor,home_dir):
    """
    Based on ReadIMU function in the workers.py file
    """

    sensor_list = [] #Sensor Object
    sensor_ind_list = [] #Channel with 1b or not
    sensor_number = []
    sensor_cnt = 0
    sensor_rot = []
    sensor_label_list = []

    #Was not able to scan and then add, some sort of hang bug

    SensorObjects = []
    SensorNames = [] #useful for debugging

    for row in sensor_map:
        
        Row_Channel_I2C = row[3]
        Row_BodyPart_Name = row[1]
        Row_Rot_Type = row[2]

        if Row_Channel_I2C != 9:
            channel = int(Row_Channel_I2C[0])
            if len(Row_Channel_I2C) > 1:
                Sensor = ISM330DHCX(tca[channel],address = const(0x6B))
                SensorNames.append(str(channel) + "-" + "0x6B")
            else:
                Sensor = ISM330DHCX(tca[channel],address = const(0x6A))
                SensorNames.append(str(channel) + "-" + "0x6A")
            
            #Set sensors to same default values
            Sensor.accelerometer_range = AccelRange.RANGE_8G
            Sensor.gyro_range = GyroRange.RANGE_2000_DPS

            
            sensor_list.append(Sensor)
            sensor_ind_list.append(Row_Channel_I2C)
            len_sensor_list = len(sensor_ind_list)
            sensor_number.append(sensor_cnt)
            sensor_cnt += 1
            sensor_rot.append(Row_Rot_Type) 
            sensor_label_list.append(Row_BodyPart_Name)

    header_text = 'time\t'
    for label in sensor_label_list:
        header_text = header_text + '\t' + label
    header_text = header_text + '\n'
    num_sensors = len(sensor_number)

    # load fake data and figure out number of sensors

    "Need to figure out what is init_time and signals per sensor(i think this is 6)"

    quat_cal_offset = int(init_time*rate) # array for data for calibrating sensors
    #cwd = os.getcwd() cwd does not seem to be used
    sensor_vec = np.zeros(num_sensors*signals_per_sensor)
    scaling = np.ones(num_sensors*signals_per_sensor)
    offsets = np.zeros(num_sensors*signals_per_sensor)
    imu_data = np.zeros((quat_cal_offset, num_sensors*signals_per_sensor))
    fake_data_len = 0

    cal_dir = home_dir+'calibration'
    gyro_file = '/gyro_offsets.npy'
    if calibrate_sensors or not os.path.exists(cal_dir): # also check if calibration folder exists, else create dir and calibrate
        print("Calibrating sensors!")
        try: # create calibration dir
            os.makedirs(cal_dir)
        except:
            pass
        calibrating_sensors(cal_dir, gyro_file, rate, sensor_list)
    
    offsets = np.load(cal_dir+gyro_file)# loading calibration vec

def calibrating_sensors(cal_dir, gyro_file, rate, sensor_list, calibration_time=10.0, signals_per_sensor=6):
    dt = 1/rate
    num_samples = int(calibration_time//dt)
    num_sensors = len(sensor_list)
    cal_data = np.zeros((num_samples, 6*num_sensors))
    time_start = time.time()
    sample_cnt = 0
    while sample_cnt < num_samples:
        cur_time = time.time()
        if cur_time >= time_start + dt: # time for next reading
            time_start = cur_time
            for j, s in enumerate(sensor_list):
                s_off = j*signals_per_sensor
                cal_data[sample_cnt, s_off+3:s_off+6] = s.gyro
            sample_cnt += 1
    gyro_offset = -1.0*np.mean(cal_data,axis=0)
    np.save(cal_dir+gyro_file, gyro_offset)

SensorObjects = RecordSensors()

time.sleep(2)

#Collect data for each sensor
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
