#!/usr/bin/env/python
# File name   : camera_pi2.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/22
import io
import time
import cv2
from picamera2 import Picamera2, Preview
import libcamera 
from base_camera import BaseCamera


hflip = 0
vflip = 0

class Camera(BaseCamera):
    @staticmethod
    def frames():
        picam2 = Picamera2() 
        
        preview_config = picam2.preview_configuration
        preview_config.size = (640, 480)
        preview_config.format = 'RGB888'  # 'XRGB8888', 'XBGR8888', 'RGB888', 'BGR888', 'YUV420'
        preview_config.transform = libcamera.Transform(hflip=hflip, vflip=vflip)
        preview_config.colour_space = libcamera.ColorSpace.Sycc()
        preview_config.buffer_count = 4
        preview_config.queue = True
        # if not camera.isOpened():
        if not picam2.is_open:
            raise RuntimeError('Could not start camera.')

        try:
            picam2.start()
        except Exception as e:
            print(f"\033[38;5;1mError:\033[0m\n{e}")
            print("\nPlease check whether the camera is connected well,  \
                  and disable the \"legacy camera driver\" on raspi-config")
        while True:
            start_time = time.time()
            # read current frame
            img = picam2.capture_array()
            if cv2.imencode('.jpg', img)[0]:
                yield cv2.imencode('.jpg', img)[1].tobytes()
    