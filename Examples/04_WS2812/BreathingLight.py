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
        self.stop_event = threading.Event() 

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
        while self.lightMode == 'police' and not self.stop_event.is_set():  # 添加停止事件检查
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
        while self.lightMode == 'breath' and not self.stop_event.is_set():  # 添加停止事件检查
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
        while not self.stop_event.is_set():
            self.__flag.wait()
            self.lightChange()


class RobotLight(threading.Thread):
    def __init__(self):
        self.left_R = 7
        self.left_G = 0
        self.left_B = 8
        self.right_R = 5
        self.right_G = 6
        self.right_B = 1
        self.Left_G = PWM(pin=self.left_R, initial_value=1.0, frequency=2000)
        self.Left_B = PWM(pin=self.left_G, initial_value=1.0, frequency=2000)
        self.Left_R = PWM(pin=self.left_B, initial_value=1.0, frequency=2000)
        self.Right_G = PWM(pin=self.right_R, initial_value=1.0, frequency=2000)
        self.Right_B = PWM(pin=self.right_G, initial_value=1.0, frequency=2000)
        self.Right_R = PWM(pin=self.right_B, initial_value=1.0, frequency=2000)

    def setRGBColor(self, LED_num, R, G, B):
        if LED_num == 1:
            R_val = map(R, 0, 255, 0, 1.00)
            G_val = map(G, 0, 255, 0, 1.00)
            B_val = map(B, 0, 255, 0, 1.00)
            self.Left_R.value = 1.0 - R_val
            self.Left_G.value = 1.0 - G_val
            self.Left_B.value = 1.0 - B_val
        elif LED_num == 2:
            R_val = map(R, 0, 255, 0, 1.00)
            G_val = map(G, 0, 255, 0, 1.00)
            B_val = map(B, 0, 255, 0, 1.00)
            self.Right_R.value = 1.0 - R_val
            self.Right_G.value = 1.0 - G_val
            self.Right_B.value = 1.0 - B_val

    def both_on(self, R, G, B):
        self.setRGBColor(1, R, G, B)
        self.setRGBColor(2, R, G, B)

    def RGB_left_on(self, R, G, B):
        self.setRGBColor(1, R, G, B)
        self.setRGBColor(2, 0, 0, 0)

    def RGB_right_on(self, R, G, B):
        self.setRGBColor(1, 0, 0, 0)
        self.setRGBColor(2, R, G, B)

    def both_off(self):
        self.setRGBColor(1, 0, 0, 0)
        self.setRGBColor(2, 0, 0, 0)


if __name__ == '__main__':
    led = RobotWS2812()
    led.start()
    try:
        led.breath(128, 124, 128)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        led.pause()
        led.stop_event.set() 
        print("The program has terminated and the WS2812 light bar has been turned off.")
        sys.exit(0)
