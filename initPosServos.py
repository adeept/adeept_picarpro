#!/usr/bin/env python3
# File name   : initPosServos.py
# Author	  : Adeept

from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
pwm_servo = PCA9685(i2c, address=0x40)  
pwm_servo.frequency = 50  

servo_num = 16

for i in range(servo_num):
    servo_angle = servo.Servo(
        pwm_servo.channels[i], 
        min_pulse=500, 
        max_pulse=2400,
        actuation_range=180
    )
    servo_angle.angle = 90

pwm_servo.deinit()
