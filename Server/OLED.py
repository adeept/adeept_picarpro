#!/usr/bin/env/python
# File name   : OLED.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date		  : 2025/03/25

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
import time
import threading

try:
	serial = i2c(port=1, address=0x3C)
	device = ssd1306(serial, rotate=0)
except:
	print('OLED disconnected\n')


text_1 = 'GEWBOT.COM'
text_2 = 'IP:CONNECTING'
text_3 = '<ARM> OR <PT> MODE'
text_4 = 'MPU6050 DETECTING'
text_5 = 'FUNCTION OFF'
text_6 = 'Message:None'

class OLED_ctrl(threading.Thread):
	def __init__(self, *args, **kwargs):
		super(OLED_ctrl, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.set()	  
		self.__running = threading.Event()	
		self.__running.set()	

	def run(self):
		while self.__running.isSet():
			self.__flag.wait()	
			with canvas(device) as draw:
				draw.text((0, 0), text_1, fill="white")
				draw.text((0, 10), text_2, fill="white")
				draw.text((0, 20), text_3, fill="white")
				draw.text((0, 30), text_4, fill="white")
				draw.text((0, 40), text_5, fill="white")
				draw.text((0, 50), text_6, fill="white")
			print('loop')
			self.pause()

	def pause(self):
		self.__flag.clear()	

	def resume(self):
		self.__flag.set()	

	def stop(self):
		self.__flag.set()	  
		self.__running.clear()		

	def screen_show(self, position, text):
		global text_1, text_2, text_3, text_4, text_5, text_6
		if position == 1:
			text_1 = text
		elif position == 2:
			text_2 = text
		elif position == 3:
			text_3 = text
		elif position == 4:
			text_4 = text
		elif position == 5:
			text_5 = text
		elif position == 6:
			text_6 = text
		self.resume()

if __name__ == '__main__':
	screen = OLED_ctrl()
	screen.start()
	screen.screen_show(1, 'GEWBOT.COM')
	while 1:
		time.sleep(10)
		pass
