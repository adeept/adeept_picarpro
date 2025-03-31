#!/usr/bin/env/python
# File name   : TimeOled.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/22
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import datetime
import time

# Create an I2C object
i2c = busio.I2C(board.SCL, board.SDA)

# Create an SSD1306 OLED device object with a screen resolution of 128x64
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Load the font
font = ImageFont.load_default()

try:
    while True:
        # Clear the screen
        oled.fill(0)

        # Create a blank image
        image = Image.new('1', (oled.width, oled.height))

        # Create a drawing object
        draw = ImageDraw.Draw(image)

        # Get the current time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # Draw the date on the first line
        draw.text((0, 0), f"Date: {date_str}", font=font, fill=255)

        # Get the height of the first line
        bbox_date = draw.textbbox((0, 0), f"Date: {date_str}", font=font)
        date_height = bbox_date[3] - bbox_date[1]

        # Draw the time on the second line with some offset
        offset = 5  # You can adjust this value as needed
        draw.text((0, date_height + offset), f"Time: {time_str}", font=font, fill=255)

        # Display the image on the OLED screen
        oled.image(image)
        oled.show()

        # Pause for 1 second
        time.sleep(1)

except KeyboardInterrupt:
    # Clear the screen
    oled.fill(0)
    oled.show()