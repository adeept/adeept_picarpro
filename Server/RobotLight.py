#!/usr/bin/env/python3
# File name   : FlowingLights.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/26
import time
import sys
from gpiozero import PWMOutputDevice as PWM
from rpi_ws281x import *
import threading



base_colors = [
    (0, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 128, 255),
    (192, 192, 192),
    (192, 192, 0),
    (128, 128, 128),
    (128, 0, 0),
    (128, 128, 0),
    (0, 128, 0),
    (0, 128, 128)
]



def generate_color_sequences():
    color_sequences = []
    for i in range(len(base_colors)):
        new_sequence = base_colors[i:] + base_colors[:i]
        color_sequences.append(new_sequence)
    return color_sequences


def check_rpi_model():
    _, result = run_command("cat /proc/device-tree/model |awk '{print $3}'")
    result = result.strip()
    if result == '3':
        return 3
    elif result == '4':
        return 4
    elif result == '5':
        return 5
    else:
        return None


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result


def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class RobotWS2812(threading.Thread):
    def __init__(self):
        self.LED_COUNT = 16
        self.LED_PIN = 12
        self.LED_FREQ_HZ = 800000
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 255
        self.LED_INVERT = False
        self.LED_CHANNEL = 0
        self.colorBreathR = 0
        self.colorBreathG = 0
        self.colorBreathB = 0
        self.breathSteps = 10
        self.lightMode = 'none'
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()
        super().__init__()
        self.__flag = threading.Event()
        self.__flag.clear()

    def setColor(self, R, G, B):
        color = Color(int(R), int(G), int(B))
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def setDifferentColors(self, colors):
        max_led = min(len(colors), self.LED_COUNT)
        for i in range(max_led):
            r, g, b = colors[i]
            self.strip.setPixelColor(i, Color(int(r), int(g), int(b)))
        self.strip.show()

    def setSomeColor(self, R, G, B, ID):
        color = Color(int(R), int(G), int(B))
        for i in ID:
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def pause(self):
        self.lightMode = 'none'
        self.setColor(0, 0, 0)
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def police(self):
        self.lightMode = 'police'
        self.resume()

    def policeProcessing(self):
        while self.lightMode == 'police':
            for i in range(3):
                self.setSomeColor(0, 0, 255, list(range(12)))
                self.setColor(0, 0, 255)
                time.sleep(0.05)
                self.setSomeColor(0, 0, 0, list(range(12)))
                self.setColor(0, 0, 0)
                time.sleep(0.05)
            if self.lightMode != 'police':
                break
            time.sleep(0.3)
            for i in range(3):
                self.setSomeColor(255, 0, 0, list(range(12)))
                self.setColor(255, 0, 0)
                time.sleep(0.05)
                self.setSomeColor(0, 0, 0, list(range(12)))
                self.setColor(0, 0, 0)
                time.sleep(0.05)
            time.sleep(0.3)

    def breath(self, R_input, G_input, B_input):
        self.lightMode = 'breath'
        self.colorBreathR = R_input
        self.colorBreathG = G_input
        self.colorBreathB = B_input
        self.resume()

    def breathProcessing(self):
        while self.lightMode == 'breath':
            for i in range(self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR * i / self.breathSteps, self.colorBreathG * i / self.breathSteps, self.colorBreathB * i / self.breathSteps)
                time.sleep(0.03)
            for i in range(self.breathSteps):
                if self.lightMode != 'breath':
                    break
                self.setColor(self.colorBreathR - (self.colorBreathR * i / self.breathSteps), self.colorBreathG - (self.colorBreathG * i / self.breathSteps), self.colorBreathB - (self.colorBreathB * i / self.breathSteps))
                time.sleep(0.03)

    def lightChange(self):
        if self.lightMode == 'none':
            self.pause()
        elif self.lightMode == 'police':
            self.policeProcessing()
        elif self.lightMode == 'breath':
            self.breathProcessing()

    def run(self):
        while True:
            self.__flag.wait()
            self.lightChange()

if __name__ == '__main__':
    RL = RobotWS2812()
    RL.start()
    color_sequences = generate_color_sequences()
    try:
        while True:
            for sequence in color_sequences:
                RL.setDifferentColors(sequence)
                time.sleep(0.3)
    except KeyboardInterrupt:
        RL.pause()
        print("The program has terminated and the WS2812 light bar has been turned off.")
        sys.exit(0)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
