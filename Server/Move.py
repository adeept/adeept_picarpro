#!/usr/bin/env/python3
# File name   : Move.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/25
import time
from gpiozero import Motor, OutputDevice

Motor_A_EN    = 4
Motor_B_EN    = 17

Motor_A_Pin1  = 26
Motor_A_Pin2  = 21
Motor_B_Pin1  = 27
Motor_B_Pin2  = 18



motor_left = Motor(forward=Motor_B_Pin2, backward=Motor_B_Pin1, enable=Motor_B_EN)
motor_right = Motor(forward=Motor_A_Pin2, backward=Motor_A_Pin1, enable=Motor_A_EN)

def motorStop():#Motor stops
    motor_left.stop()
    motor_right.stop()


def setup():#Motor initialization
    pass


def move(speed, direction, turn, radius=0.6):   # 0 < radius <= 1
    speed = speed / 100 
    if direction == 'forward':
        if turn == 'right':
            motor_left.backward(speed * radius)
            motor_right.forward(speed)
        elif turn == 'left':
            motor_left.forward(speed)
            motor_right.backward(speed * radius)
        else:
            motor_left.forward(speed)
            motor_right.forward(speed)
    elif direction == 'backward':
        if turn == 'right':
            motor_left.forward(speed * radius)
            motor_right.backward(speed)
        elif turn == 'left':
            motor_left.backward(speed)
            motor_right.forward(speed * radius)
        else:
            motor_left.backward(speed)
            motor_right.backward(speed)
    elif direction == 'no':
        if turn == 'right':
            motor_left.backward(speed)
            motor_right.forward(speed)
        elif turn == 'left':
            motor_left.forward(speed)
            motor_right.backward(speed)
        else:
            motorStop()
    else:
        pass


def destroy():
    motorStop()

def video_Tracking_Move(speed, direction):   # 0 < radius <= 1  
    #speed:0~100. direction:1/-1.
    if speed == 0:
        motorStop() #all motor stop.
    else:
        if direction == 1: 			# forward
            move(speed, 'forward', 'no', 0.5)

        elif direction == -1: 		# backward
            move.move(speed, 'backward', 'no', 0.5)

if __name__ == '__main__':
    try:
        speed_set = 50
        setup()
        for i in range(10):
            move(speed_set, 'forward', 'no', 0.8)
            print("Forward")
            time.sleep(2)
            move(speed_set, 'backward', 'no', 0.8)
            print("backward")
            time.sleep(2)

        destroy()
    except KeyboardInterrupt:
        destroy()
    
