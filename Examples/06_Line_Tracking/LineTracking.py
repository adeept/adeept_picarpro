#!/usr/bin/env/python
# File name   : LineTracking.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/22

import time
from gpiozero import InputDevice

line_pin_left = 19
line_pin_middle = 16
line_pin_right = 20

left = InputDevice(pin=line_pin_left)
middle = InputDevice(pin=line_pin_middle)
right = InputDevice(pin=line_pin_right)

def run():
    status_right = right.value
    status_middle = middle.value
    status_left = left.value
    print('left: %d   middle: %d   right: %d' %(status_left,status_middle,status_right))


if __name__ == '__main__':
    try:
      while 1:
        run()
        time.sleep(0.3)
    except KeyboardInterrupt:
        pass
