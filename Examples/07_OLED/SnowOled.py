#!/usr/bin/env/python
# File name   : SnowOled.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/22
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw
import random
import time

# Create an I2C object
i2c = busio.I2C(board.SCL, board.SDA)

# Create an SSD1306 OLED device object with a screen resolution of 128x64
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Define the Snowflake class
class Snowflake:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def fall(self):
        self.y += self.speed
        if self.y > oled.height:
            self.y = 0
            self.x = random.randint(0, oled.width)

    def draw(self, draw):
        draw.point((self.x, self.y), fill=255)

# Define the Star class
class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.brightness = random.choice([0, 255])

    def twinkle(self):
        if random.random() < 0.1:  # 10% chance to change brightness
            self.brightness = 255 if self.brightness == 0 else 0

    def draw(self, draw):
        draw.point((self.x, self.y), fill=self.brightness)

# Create lists of snowflakes and stars
snowflakes = [Snowflake(random.randint(0, oled.width), random.randint(0, oled.height), random.randint(1, 3)) for _ in range(20)]
stars = [Star(random.randint(0, oled.width), random.randint(0, oled.height)) for _ in range(10)]

try:
    while True:
        # Clear the screen
        oled.fill(0)

        # Create a blank image
        image = Image.new('1', (oled.width, oled.height))

        # Create a drawing object
        draw = ImageDraw.Draw(image)

        # Update and draw the snowflakes
        for snowflake in snowflakes:
            snowflake.fall()
            snowflake.draw(draw)

        # Update and draw the stars
        for star in stars:
            star.twinkle()
            star.draw(draw)

        # Display the image on the OLED screen
        oled.image(image)
        oled.show()

        # Pause for a while
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clear the screen
    oled.fill(0)
    oled.show()
