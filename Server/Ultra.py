#!/usr/bin/python3
# File name   : Ultrasonic.py
# Description : Detection distance and tracking with ultrasonic
# Website     : www.adeept.com
# Author      : Adeept
# Date        : 2025/03/25

from gpiozero import DistanceSensor
from time import sleep

Tr = 11
Ec =  8
sensor = DistanceSensor(echo=Ec, trigger=Tr,max_distance=2) # Maximum detection distance 2m.

def checkdist():
    value = (sensor.distance) * 100  # Unit: cm
    return round(value, 2)

if __name__ == "__main__":
    while True:
        distance = checkdist() 
        print("%.2f cm" %distance)
        sleep(0.05)
