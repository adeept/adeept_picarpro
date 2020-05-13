#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# File name   : client.py
# Description : client  
# Website	 : www.gewbot.com
# Author	  : William
# Date		: 2019/08/28

from socket import *
import sys
import time
import threading as thread
import tkinter as tk
import math
import json

try:
	import cv2
	import zmq
	import base64
	import numpy as np
except:
	print("Couldn't import OpenCV, you need to install it first.")

OSD_X = 0#1
OSD_Y = 0
advanced_OSD = 0

PT_stu = 0
UD_stu = 0
HA_stu = 0
GA_stu = 0


def global_init():
	global DS_stu, TS_stu, color_bg, color_text, color_btn, color_line, color_can, color_oval, target_color
	global speed, ip_stu, Switch_3, Switch_2, Switch_1, servo_stu, function_stu
	DS_stu = 0
	TS_stu = 0

	color_bg='#000000'		#Set background color
	color_text='#E1F5FE'	  #Set text color
	color_btn='#0277BD'	   #Set button color
	color_line='#01579B'	  #Set line color
	color_can='#212121'	   #Set canvas color
	color_oval='#2196F3'	  #Set oval color
	target_color='#FF6D00'
	speed = 1
	ip_stu=1

	Switch_3 = 0
	Switch_2 = 0
	Switch_1 = 0

	servo_stu = 0
	function_stu = 0


global_init()


########>>>>>VIDEO<<<<<########
def RGB_to_Hex(r, g, b):
	return ('#'+str(hex(r))[-2:]+str(hex(g))[-2:]+str(hex(b))[-2:]).replace('x','0').upper()


def rgb2hsv(r, g, b):
	r, g, b  = r/255.0, g/255.0, b/255.0
	mx = max(r, g, b)
	mn = min(r, g, b)
	df = mx-mn
	if mx == mn:
		h = 0
	elif mx == r:
		h = (60*((g-b)/df) + 360) % 360
	elif mx == g:
		h = (60*((b-r)/df) + 120) % 360
	elif mx == b:
		h = (60*((r-g)/df) + 240) % 360
	if mx == 0:
		s = 0
	else:
		s = (df/mx)*100
	v = mx*100
	h=h/360*255
	return str(int(h))+' '+str(int(s))+' '+str(int(v))


def video_thread():
	global footage_socket, font, frame_num, fps
	context = zmq.Context()
	footage_socket = context.socket(zmq.SUB)
	footage_socket.bind('tcp://*:5555')
	footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

	font = cv2.FONT_HERSHEY_SIMPLEX

	frame_num = 0
	fps = 0


def getposBgr(event, x, y, flags, param):
	if event==cv2.EVENT_LBUTTONDOWN:
		getBGR = source[y, x]
		var_R.set(getBGR[2])
		var_G.set(getBGR[1])
		var_B.set(getBGR[0])
		# tcpClicSock.send(('FCSET %s'%rgb2hsv(int(var_R.get()), int(var_G.get()), int(var_B.get()))).encode())
		canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
		print("BGR is", getBGR)
		print("HSV is", HSVimg[y, x])
		tcpClicSock.send(('FCSET %s %s %s'%(HSVimg[y, x][0], HSVimg[y, x][1], HSVimg[y, x][2])).encode())
		# print("HSV genOut is", rgb2hsv(int(var_R.get()), int(var_G.get()), int(var_B.get())))


def getposHsv(event, x, y, flags, param):
	if event==cv2.EVENT_LBUTTONDOWN:
		print("HSV is", HSVimg[y, x])
		tcpClicSock.send(('FCSET %s %s %s'%(HSVimg[y, x][0], HSVimg[y, x][1], HSVimg[y, x][2])).encode())
		getBGR = source[y, x]
		var_R.set(getBGR[2])
		var_G.set(getBGR[1])
		var_B.set(getBGR[0])
		canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))


def get_FPS():
	global frame_num, fps
	while 1:
		try:
			time.sleep(1)
			fps = frame_num
			frame_num = 0
		except:
			time.sleep(1)


def advanced_OSD_add(draw_on, X, Y):#1
	error_X = X*10
	error_Y = Y*6-2
	#if error_Y > 0:
	X_s = int(200+120-120*math.cos(math.radians(error_Y)))
	Y_s = int(240+120*math.sin(math.radians(error_Y))-error_X*3)

	X_e = int(320+120*math.cos(math.radians(error_Y)))
	Y_e = int(240-120*math.sin(math.radians(error_Y))-error_X*3)
	cv2.line(draw_on,(X_s,Y_s),(X_e,Y_e),(0,255,0),2)
	cv2.putText(draw_on,('horizontal line'),(X_e+10,Y_e), font, 0.5,(0,255,0),1,cv2.LINE_AA)

	cv2.line(draw_on,(X_s,Y_s+270),(X_e,Y_e+270),(0,255,0),2)
	cv2.putText(draw_on,('Down'),(X_e+10,Y_e+270), font, 0.5,(0,255,0),1,cv2.LINE_AA)

	cv2.line(draw_on,(X_s,Y_s-270),(X_e,Y_e-270),(0,255,0),2)
	cv2.putText(draw_on,('Up'),(X_e+10,Y_e-270), font, 0.5,(0,255,0),1,cv2.LINE_AA)

	X_s_short = int(260+60-60*math.cos(math.radians(error_Y)))
	Y_s_short = int(240+60*math.sin(math.radians(error_Y))-error_X*3)

	X_e_short = int(320+60*math.cos(math.radians(error_Y)))
	Y_e_short = int(240-60*math.sin(math.radians(error_Y))-error_X*3)

	cv2.line(draw_on,(X_s_short,Y_s_short+90),(X_e_short,Y_e_short+90),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short+180),(X_e_short,Y_e_short+180),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short+360),(X_e_short,Y_e_short+360),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short+450),(X_e_short,Y_e_short+450),(0,255,0))

	cv2.line(draw_on,(X_s_short,Y_s_short-90),(X_e_short,Y_e_short-90),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short-180),(X_e_short,Y_e_short-180),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short-360),(X_e_short,Y_e_short-360),(0,255,0))
	cv2.line(draw_on,(X_s_short,Y_s_short-450),(X_e_short,Y_e_short-450),(0,255,0))


def opencv_r():
	global frame_num, source, HSVimg
	while True:
		try:
			frame = footage_socket.recv_string()
			img = base64.b64decode(frame)
			npimg = np.frombuffer(img, dtype=np.uint8)
			source = cv2.imdecode(npimg, 1)
			cv2.putText(source,('PC FPS: %s'%fps),(40,20), font, 0.5,(255,255,255),1,cv2.LINE_AA)

			
			try:
				cv2.putText(source,('CPU Temperature: %s'%CPU_TEP),(370,350), font, 0.5,(128,255,128),1,cv2.LINE_AA)
				cv2.putText(source,('CPU Usage: %s'%CPU_USE),(370,380), font, 0.5,(128,255,128),1,cv2.LINE_AA)
				cv2.putText(source,('RAM Usage: %s'%RAM_USE),(370,410), font, 0.5,(128,255,128),1,cv2.LINE_AA)

				cv2.rectangle(source, (167, 320), (473, 330), (255,255,255))

				DIR_show = int(CAR_DIR)
				if DIR_show > 0:
					cv2.rectangle(source, ((320-DIR_show), 323), (320, 327), (255,255,255))
				elif DIR_show < 0:
					cv2.rectangle(source, (320, 323), ((320-DIR_show), 327), (255,255,255))


				#cv2.line(source,(320,240),(260,300),(255,255,255),1)
				#cv2.line(source,(210,300),(260,300),(255,255,255),1)

				#cv2.putText(source,('%sm'%ultra_data),(210,290), font, 0.5,(255,255,255),1,cv2.LINE_AA)
			except:
				pass

			if advanced_OSD:#1
				advanced_OSD_add(source, OSD_X, OSD_Y)
			
			#cv2.putText(source,('%sm'%ultra_data),(210,290), font, 0.5,(255,255,255),1,cv2.LINE_AA)
			cv2.imshow("Stream", source)
			cv2.setMouseCallback("Stream", getposBgr)

			HSVimg = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
			cv2.imshow("StreamHSV", HSVimg)
			cv2.setMouseCallback("StreamHSV", getposHsv)

			frame_num += 1
			cv2.waitKey(1)

		except:
			time.sleep(0.5)
			break

fps_threading=thread.Thread(target=get_FPS)		 #Define a thread for FPV and OpenCV
fps_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
fps_threading.start()									 #Thread starts

video_threading=thread.Thread(target=video_thread)		 #Define a thread for FPV and OpenCV
video_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
video_threading.start()									 #Thread starts

########>>>>>VIDEO<<<<<########


def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
	newline=""
	str_num=str(new_num)
	with open("ip.txt","r") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				line = initial+"%s" %(str_num)
			newline += line
	with open("ip.txt","w") as f:
		f.writelines(newline)	#Call this function to replace data in '.txt' file


def num_import(initial):			#Call this function to import data from '.txt' file
	with open("ip.txt") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				r=line
	begin=len(list(initial))
	snum=r[begin:]
	n=snum
	return n	


def connection_thread():
	global Switch_3, Switch_2, Switch_1, function_stu, OSD_X, OSD_Y, OSD_info, advanced_OSD, car_info
	while 1:
		car_info = (tcpClicSock.recv(BUFSIZ)).decode()
		if not car_info:
			continue
		elif 'Switch_3_on' in car_info:
			Switch_3 = 1
			Btn_Switch_3.config(bg='#4CAF50')

		elif 'Switch_2_on' in car_info:
			Switch_2 = 1
			Btn_Switch_2.config(bg='#4CAF50')

		elif 'Switch_1_on' in car_info:
			Switch_1 = 1
			Btn_Switch_1.config(bg='#4CAF50')

		elif 'Switch_3_off' in car_info:
			Switch_3 = 0
			Btn_Switch_3.config(bg=color_btn)

		elif 'Switch_2_off' in car_info:
			Switch_2 = 0
			Btn_Switch_2.config(bg=color_btn)

		elif 'Switch_1_off' in car_info:
			Switch_1 = 0
			Btn_Switch_1.config(bg=color_btn)

		elif 'ultra' in car_info:
			print('ultrasonic radar')
			print(car_info)

			# while 1:
			# 	new_info = (tcpClicSock.recv(BUFSIZ)).decode()
			# 	print('....................xxxxxxxxxxxxx......................')
			# 	print(new_info)
			# 	car_info += new_info
			# 	if 'finish' in new_info:
			# 		break

			new_number2view(30,290,json.loads(car_info))


		elif 'function_1_on' in car_info:
			function_stu = 1
			Btn_function_1.config(bg='#4CAF50')

		elif 'function_2_on' in car_info:
			function_stu = 1
			Btn_function_2.config(bg='#4CAF50')

		elif 'function_3_on' in car_info:
			function_stu = 1
			Btn_function_3.config(bg='#4CAF50')

		elif 'function_4_on' in car_info:
			function_stu = 1
			Btn_function_4.config(bg='#4CAF50')
			advanced_OSD = 1

		elif 'function_5_on' in car_info:
			function_stu = 1
			Btn_function_5.config(bg='#4CAF50')

		elif 'function_6_on' in car_info:
			function_stu = 1
			Btn_function_6.config(bg='#4CAF50')
			# advanced_OSD = 1	#bug happend

		elif 'function_1_off' in car_info:
			function_stu = 0
			Btn_function_1.config(bg=color_btn)

		elif 'function_2_off' in car_info:
			function_stu = 0
			Btn_function_2.config(bg=color_btn)

		elif 'function_3_off' in car_info:
			function_stu = 0
			Btn_function_3.config(bg=color_btn)

		elif 'function_4_off' in car_info:
			function_stu = 0
			Btn_function_4.config(bg=color_btn)
			advanced_OSD = 0

		elif 'function_5_off' in car_info:
			function_stu = 0
			Btn_function_5.config(bg=color_btn)

		elif 'function_6_off' in car_info:
			function_stu = 0
			Btn_function_6.config(bg=color_btn)
			# advanced_OSD = 0	#bug

		elif 'CVFL_on' in car_info:
			function_stu = 1
			Btn_CVFL.config(bg='#4CAF50')

		elif 'CVFL_off' in car_info:
			function_stu = 0
			Btn_CVFL.config(bg='#212121')

		elif 'OSD' in car_info:
			OSD_info = car_info.split()
			try:
				OSD_X = float(OSD_info[1])
				OSD_Y = float(OSD_info[2])
			except:
				pass


def Info_receive():
	global CPU_TEP,CPU_USE,RAM_USE,CAR_DIR
	HOST = ''
	INFO_PORT = 2256							#Define port serial 
	ADDR = (HOST, INFO_PORT)
	InfoSock = socket(AF_INET, SOCK_STREAM)
	InfoSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	InfoSock.bind(ADDR)
	InfoSock.listen(5)					  #Start server,waiting for client
	InfoSock, addr = InfoSock.accept()
	print('Info connected')
	while 1:
		try:
			info_data = ''
			info_data = str(InfoSock.recv(BUFSIZ).decode())
			info_get = info_data.split()
			CPU_TEP,CPU_USE,RAM_USE,CAR_DIR= info_get
			CPU_TEP_lab.config(text='CPU Temp: %s℃'%CPU_TEP)
			CPU_USE_lab.config(text='CPU Usage: %s'%CPU_USE)
			RAM_lab.config(text='RAM Usage: %s'%RAM_USE)
		except:
			pass


def socket_connect():	 #Call this function to connect with the server
	global ADDR,tcpClicSock,BUFSIZ,ip_stu,ipaddr
	ip_adr=E1.get()	   #Get the IP address from Entry

	if ip_adr == '':	  #If no input IP address in Entry,import a default IP
		ip_adr=num_import('IP:')
		l_ip_4.config(text='Connecting')
		l_ip_4.config(bg='#FF8F00')
		l_ip_5.config(text='Default:%s'%ip_adr)
		pass
	
	SERVER_IP = ip_adr
	SERVER_PORT = 10223   #Define port serial 
	BUFSIZ = 1024		 #Define buffer size
	ADDR = (SERVER_IP, SERVER_PORT)
	tcpClicSock = socket(AF_INET, SOCK_STREAM) #Set connection value for socket

	for i in range (1,6): #Try 5 times if disconnected
		#try:
		if ip_stu == 1:
			print("Connecting to server @ %s:%d..." %(SERVER_IP, SERVER_PORT))
			print("Connecting")
			tcpClicSock.connect(ADDR)		#Connection with the server
		
			print("Connected")
		
			l_ip_5.config(text='IP:%s'%ip_adr)
			l_ip_4.config(text='Connected')
			l_ip_4.config(bg='#558B2F')

			replace_num('IP:',ip_adr)
			E1.config(state='disabled')	  #Disable the Entry
			Btn14.config(state='disabled')   #Disable the Entry
			
			ip_stu=0						 #'0' means connected

			connection_threading=thread.Thread(target=connection_thread)		 #Define a thread for FPV and OpenCV
			connection_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
			connection_threading.start()									 #Thread starts

			info_threading=thread.Thread(target=Info_receive)		 #Define a thread for FPV and OpenCV
			info_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
			info_threading.start()									 #Thread starts

			video_threading=thread.Thread(target=opencv_r)		 #Define a thread for FPV and OpenCV
			video_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
			video_threading.start()									 #Thread starts

			break
		else:
			print("Cannot connecting to server,try it latter!")
			l_ip_4.config(text='Try %d/5 time(s)'%i)
			l_ip_4.config(bg='#EF6C00')
			print('Try %d/5 time(s)'%i)
			ip_stu=1
			time.sleep(1)
			continue

	if ip_stu == 1:
		l_ip_4.config(text='Disconnected')
		l_ip_4.config(bg='#F44336')


def connect(event):	   #Call this function to connect with the server
	if ip_stu == 1:
		sc=thread.Thread(target=socket_connect) #Define a thread for connection
		sc.setDaemon(True)					  #'True' means it is a front thread,it would close when the mainloop() closes
		sc.start()							  #Thread starts


def scale_send(event):
	time.sleep(0.03)
	tcpClicSock.send(('wsB %s'%var_Speed.get()).encode())


def servo_buttons(x,y):
	def call_up(event):
		global UD_stu
		if UD_stu == 0:
			tcpClicSock.send(('up').encode())
			UD_stu = 1

	def call_down(event):
		global UD_stu
		if UD_stu == 0:
			tcpClicSock.send(('down').encode())
			UD_stu = 1

	def call_UDstop(event):
		global UD_stu
		tcpClicSock.send(('UDstop').encode())
		UD_stu = 0


	def call_lookleft(event):
		global PT_stu
		if PT_stu == 0:
			tcpClicSock.send(('lookleft').encode())
			PT_stu = 1

	def call_lookright(event):
		global PT_stu
		if PT_stu == 0:
			tcpClicSock.send(('lookright').encode())
			PT_stu = 1

	def call_LRstop(event):
		global PT_stu
		tcpClicSock.send(('LRstop').encode())
		PT_stu = 0


	def call_handup(event):
		global HA_stu
		if HA_stu == 0:
			tcpClicSock.send(('handup').encode())
			HA_stu = 1

	def call_handdown(event):
		global HA_stu
		if HA_stu == 0:
			tcpClicSock.send(('handdown').encode())
			HA_stu = 1

	def call_HAstop(event):
		global HA_stu
		tcpClicSock.send(('HAstop').encode())
		HA_stu = 0


	def call_grab(event):
		global GA_stu
		if GA_stu == 0:
			tcpClicSock.send(('grab').encode())
			GA_stu = 1

	def call_loose(event):
		global GA_stu
		if GA_stu == 0:
			tcpClicSock.send(('loose').encode())
			GA_stu = 1

	def call_stop(event):
		global GA_stu
		tcpClicSock.send(('stop').encode())
		GA_stu = 0



	def call_home(event):
		tcpClicSock.send(('home').encode())
		time.sleep(0.15)

	Btn_0 = tk.Button(root, width=8, text='Left',fg=color_text,bg=color_btn,relief='ridge')
	Btn_0.place(x=x,y=y+35)
	Btn_0.bind('<ButtonPress-1>', call_lookleft)
	Btn_0.bind('<ButtonRelease-1>', call_LRstop)
	root.bind('<KeyPress-j>', call_lookleft)
	root.bind('<KeyRelease-j>', call_LRstop)

	Btn_1 = tk.Button(root, width=8, text='Up',fg=color_text,bg=color_btn,relief='ridge')
	Btn_1.place(x=x+70,y=y)
	Btn_1.bind('<ButtonPress-1>', call_up)
	Btn_1.bind('<ButtonRelease-1>', call_UDstop)
	root.bind('<KeyPress-i>', call_up)
	root.bind('<KeyRelease-i>', call_UDstop) 

	Btn_1 = tk.Button(root, width=8, text='Down',fg=color_text,bg=color_btn,relief='ridge')
	Btn_1.place(x=x+70,y=y+35)
	Btn_1.bind('<ButtonPress-1>', call_down)
	Btn_1.bind('<ButtonRelease-1>', call_UDstop)
	root.bind('<KeyPress-k>', call_down)
	root.bind('<KeyRelease-k>', call_UDstop)

	Btn_2 = tk.Button(root, width=8, text='Right',fg=color_text,bg=color_btn,relief='ridge')
	Btn_2.place(x=x+140,y=y+35)
	Btn_2.bind('<ButtonPress-1>', call_lookright)
	Btn_2.bind('<ButtonRelease-1>', call_LRstop)
	root.bind('<KeyPress-l>', call_lookright) 
	root.bind('<KeyRelease-l>', call_LRstop)

	Btn_3 = tk.Button(root, width=8, text='Grab',fg=color_text,bg=color_btn,relief='ridge')
	Btn_3.place(x=x,y=y)
	Btn_3.bind('<ButtonPress-1>', call_grab)
	Btn_3.bind('<ButtonRelease-1>', call_stop)
	root.bind('<KeyPress-u>', call_grab) 
	root.bind('<KeyRelease-u>', call_stop) 

	Btn_4 = tk.Button(root, width=8, text='Loose',fg=color_text,bg=color_btn,relief='ridge')
	Btn_4.place(x=x+140,y=y)
	Btn_4.bind('<ButtonPress-1>', call_loose)
	Btn_4.bind('<ButtonRelease-1>', call_stop)
	root.bind('<KeyPress-o>', call_loose) 
	root.bind('<KeyRelease-o>', call_stop)

	Btn_5 = tk.Button(root, width=8, text='H_Down',fg=color_text,bg=color_btn,relief='ridge')
	Btn_5.place(x=x,y=y-55)
	Btn_5.bind('<ButtonPress-1>', call_handdown)
	Btn_5.bind('<ButtonRelease-1>', call_HAstop)
	root.bind('<KeyPress-n>', call_handdown) 
	root.bind('<KeyRelease-n>', call_HAstop)

	Btn_6 = tk.Button(root, width=8, text='H_Up',fg=color_text,bg=color_btn,relief='ridge')
	Btn_6.place(x=x,y=y-55-35)
	Btn_6.bind('<ButtonPress-1>', call_handup)
	Btn_6.bind('<ButtonRelease-1>', call_HAstop)
	root.bind('<KeyPress-m>', call_handup)
	root.bind('<KeyRelease-m>', call_HAstop)

	root.bind('<KeyPress-h>', call_home)


def motor_buttons(x,y):
	def call_left(event):
		global TS_stu
		if TS_stu == 0:
			tcpClicSock.send(('left').encode())
			TS_stu = 1

	def call_right(event):
		global TS_stu
		if TS_stu == 0:
			tcpClicSock.send(('right').encode())
			TS_stu = 1

	def call_forward(event):
		global DS_stu
		if DS_stu == 0:
			tcpClicSock.send(('forward').encode())
			DS_stu = 1

	def call_backward(event):
		global DS_stu
		if DS_stu == 0:
			tcpClicSock.send(('backward').encode())
			DS_stu = 1

	def call_DS(event):
		global DS_stu
		tcpClicSock.send(('DS').encode())
		DS_stu = 0

	def call_TS(event):
		global TS_stu
		tcpClicSock.send(('TS').encode())
		TS_stu = 0

	def call_AR(event):
		tcpClicSock.send(('AR').encode())

	def call_PT(event):
		tcpClicSock.send(('PT').encode())

	Btn_AR = tk.Button(root, width=8, text='ARM',fg=color_text,bg=color_btn,relief='ridge')
	Btn_AR.place(x=x,y=y)
	Btn_AR.bind('<ButtonPress-1>', call_AR)

	Btn_PT = tk.Button(root, width=8, text='PT',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PT.place(x=x+140,y=y)
	Btn_PT.bind('<ButtonPress-1>', call_PT)

	Btn_0 = tk.Button(root, width=8, text='Left',fg=color_text,bg=color_btn,relief='ridge')
	Btn_0.place(x=x,y=y+35)
	Btn_0.bind('<ButtonPress-1>', call_left)
	Btn_0.bind('<ButtonRelease-1>', call_TS)
	root.bind('<KeyPress-a>', call_left)
	root.bind('<KeyRelease-a>', call_TS)

	Btn_1 = tk.Button(root, width=8, text='Forward',fg=color_text,bg=color_btn,relief='ridge')
	Btn_1.place(x=x+70,y=y)
	Btn_1.bind('<ButtonPress-1>', call_forward)
	Btn_1.bind('<ButtonRelease-1>', call_DS)
	root.bind('<KeyPress-w>', call_forward)
	root.bind('<KeyRelease-w>', call_DS) 

	Btn_1 = tk.Button(root, width=8, text='Backward',fg=color_text,bg=color_btn,relief='ridge')
	Btn_1.place(x=x+70,y=y+35)
	Btn_1.bind('<ButtonPress-1>', call_backward)
	Btn_1.bind('<ButtonRelease-1>', call_DS)
	root.bind('<KeyPress-s>', call_backward)
	root.bind('<KeyRelease-s>', call_DS)

	Btn_2 = tk.Button(root, width=8, text='Right',fg=color_text,bg=color_btn,relief='ridge')
	Btn_2.place(x=x+140,y=y+35)
	Btn_2.bind('<ButtonPress-1>', call_right)
	Btn_2.bind('<ButtonRelease-1>', call_TS)
	root.bind('<KeyPress-d>', call_right) 
	root.bind('<KeyRelease-d>', call_TS) 


def information_screen(x,y):
	global CPU_TEP_lab, CPU_USE_lab, RAM_lab, l_ip_4, l_ip_5
	CPU_TEP_lab=tk.Label(root,width=18,text='CPU Temp:',fg=color_text,bg='#212121')
	CPU_TEP_lab.place(x=x,y=y)						 #Define a Label and put it in position

	CPU_USE_lab=tk.Label(root,width=18,text='CPU Usage:',fg=color_text,bg='#212121')
	CPU_USE_lab.place(x=x,y=y+30)						 #Define a Label and put it in position

	RAM_lab=tk.Label(root,width=18,text='RAM Usage:',fg=color_text,bg='#212121')
	RAM_lab.place(x=x,y=y+60)						 #Define a Label and put it in position

	l_ip_4=tk.Label(root,width=18,text='Disconnected',fg=color_text,bg='#F44336')
	l_ip_4.place(x=x,y=y+95)						 #Define a Label and put it in position

	l_ip_5=tk.Label(root,width=18,text='Use default IP',fg=color_text,bg=color_btn)
	l_ip_5.place(x=x,y=y+130)						 #Define a Label and put it in position


def connent_input(x,y):
	global E1, Btn14
	E1 = tk.Entry(root,show=None,width=16,bg="#37474F",fg='#eceff1')
	E1.place(x=x+5,y=y+25)							 #Define a Entry and put it in position

	l_ip_3=tk.Label(root,width=10,text='IP Address:',fg=color_text,bg='#000000')
	l_ip_3.place(x=x,y=y)						 #Define a Label and put it in position

	Btn14= tk.Button(root, width=8,height=2, text='Connect',fg=color_text,bg=color_btn,relief='ridge')
	Btn14.place(x=x+130,y=y)						  #Define a Button and put it in position

	root.bind('<Return>', connect)
	Btn14.bind('<ButtonPress-1>', connect)


def switch_button(x,y):
	global Btn_Switch_1, Btn_Switch_2, Btn_Switch_3
	def call_Switch_1(event):
		if Switch_1 == 0:
			tcpClicSock.send(('Switch_1_on').encode())
		else:
			tcpClicSock.send(('Switch_1_off').encode())


	def call_Switch_2(event):
		if Switch_2 == 0:
			tcpClicSock.send(('Switch_2_on').encode())
		else:
			tcpClicSock.send(('Switch_2_off').encode())


	def call_Switch_3(event):
		if Switch_3 == 0:
			tcpClicSock.send(('Switch_3_on').encode())
		else:
			tcpClicSock.send(('Switch_3_off').encode())

	Btn_Switch_1 = tk.Button(root, width=8, text='Port 1',fg=color_text,bg=color_btn,relief='ridge')
	Btn_Switch_2 = tk.Button(root, width=8, text='Port 2',fg=color_text,bg=color_btn,relief='ridge')
	Btn_Switch_3 = tk.Button(root, width=8, text='Port 3',fg=color_text,bg=color_btn,relief='ridge')

	Btn_Switch_1.place(x=x,y=y)
	Btn_Switch_2.place(x=x+70,y=y)
	Btn_Switch_3.place(x=x+140,y=y)

	Btn_Switch_1.bind('<ButtonPress-1>', call_Switch_1)
	Btn_Switch_2.bind('<ButtonPress-1>', call_Switch_2)
	Btn_Switch_3.bind('<ButtonPress-1>', call_Switch_3)


def scale(x,y,w):
	global var_Speed
	var_Speed = tk.StringVar()
	var_Speed.set(100)

	Scale_B = tk.Scale(root,label=None,
	from_=60,to=100,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=10,variable=var_Speed,troughcolor='#448AFF',command=scale_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_B.place(x=x,y=y)							#Define a Scale and put it in position

	canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
	canvas_cover.place(x=x,y=y+30)


def ultrasonic_radar(x,y):
	x_range = 2
	can_scan = tk.Canvas(root,bg=color_can,height=250,width=320,highlightthickness=0) #define a canvas
	can_scan.place(x=x,y=y) #Place the canvas
	line = can_scan.create_line(0,62,320,62,fill='darkgray')   #Draw a line on canvas
	line = can_scan.create_line(0,124,320,124,fill='darkgray') #Draw a line on canvas
	line = can_scan.create_line(0,186,320,186,fill='darkgray') #Draw a line on canvas
	line = can_scan.create_line(160,0,160,250,fill='darkgray') #Draw a line on canvas
	line = can_scan.create_line(80,0,80,250,fill='darkgray')   #Draw a line on canvas
	line = can_scan.create_line(240,0,240,250,fill='darkgray') #Draw a line on canvas

	can_tex_11=can_scan.create_text((27,178),text='%sm'%round((x_range/4),2),fill='#aeea00')	 #Create a text on canvas
	can_tex_12=can_scan.create_text((27,116),text='%sm'%round((x_range/2),2),fill='#aeea00')	 #Create a text on canvas
	can_tex_13=can_scan.create_text((27,54),text='%sm'%round((x_range*0.75),2),fill='#aeea00')  #Create a text on canvas


def new_number2view(x,y,info):
	print(info)
	x_range = 2

	info = info[1:-1]

	total_number = len(info)
	print(total_number)

	can_scan_1 = tk.Canvas(root,bg=color_can,height=250,width=320,highlightthickness=0) #define a canvas
	can_scan_1.place(x=x,y=y) #Place the canvas
	line = can_scan_1.create_line(0,62,320,62,fill='darkgray')   #Draw a line on canvas
	line = can_scan_1.create_line(0,124,320,124,fill='darkgray') #Draw a line on canvas
	line = can_scan_1.create_line(0,186,320,186,fill='darkgray') #Draw a line on canvas
	line = can_scan_1.create_line(160,0,160,250,fill='darkgray') #Draw a line on canvas
	line = can_scan_1.create_line(80,0,80,250,fill='darkgray')   #Draw a line on canvas
	line = can_scan_1.create_line(240,0,240,250,fill='darkgray') #Draw a line on canvas

	for i in range (0,total_number):   #Scale the result to the size as canvas
		dis_info_get = info[i]
		dis_info_get = float(dis_info_get)
		if dis_info_get > 0:
			len_dis_1 = int((dis_info_get/x_range)*250)						  #600 is the height of canvas
			pos	 = int((i/total_number)*320)								#740 is the width of canvas
			pos_ra  = int(((i/total_number)*140)+20)						   #Scale the direction range to (20-160)
			len_dis = int(len_dis_1*(math.sin(math.radians(pos_ra))))		   #len_dis is the height of the line

			x0_l,y0_l,x1_l,y1_l=pos,(250-len_dis),pos,(250-len_dis)			 #The position of line
			x0,y0,x1,y1=(pos+3),(250-len_dis+3),(pos-3),(250-len_dis-3)		 #The position of arc

			if pos <= 160:													  #Scale the whole picture to a shape of sector
				pos = 160-abs(int(len_dis_1*(math.cos(math.radians(pos_ra)))))
				x1_l= (x1_l-math.cos(math.radians(pos_ra))*130)
			else:
				pos = abs(int(len_dis_1*(math.cos(math.radians(pos_ra)))))+160
				x1_l= x1_l+abs(math.cos(math.radians(pos_ra))*130)

			y1_l = y1_l-abs(math.sin(math.radians(pos_ra))*130)			  #Orientation of line

			line = can_scan_1.create_line(pos,y0_l,x1_l,y1_l,fill=color_line)   #Draw a line on canvas
			point_scan = can_scan_1.create_oval((pos+3),y0,(pos-3),y1,fill=color_oval,outline=color_oval) #Draw a arc on canvas

			can_tex_11=can_scan_1.create_text((27,178),text='%sm'%round((x_range/4),2),fill='#aeea00')	 #Create a text on canvas
			can_tex_12=can_scan_1.create_text((27,116),text='%sm'%round((x_range/2),2),fill='#aeea00')	 #Create a text on canvas
			can_tex_13=can_scan_1.create_text((27,54),text='%sm'%round((x_range*0.75),2),fill='#aeea00')  #Create a text on canvas


def scale_FL(x,y,w):
	global Btn_CVFL
	def lip1_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('lip1 %s'%var_lip1.get()).encode())

	def lip2_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('lip2 %s'%var_lip2.get()).encode())

	def err_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('err %s'%var_err.get()).encode())

	def call_Render(event):
		tcpClicSock.send(('Render').encode())

	def call_CVFL(event):
		tcpClicSock.send(('CVFL').encode())

	def call_WB(event):
		tcpClicSock.send(('WBswitch').encode())

	Scale_lip1 = tk.Scale(root,label=None,
	from_=0,to=480,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_lip1,troughcolor='#212121',command=lip1_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_lip1.place(x=x,y=y)							#Define a Scale and put it in position

	Scale_lip2 = tk.Scale(root,label=None,
	from_=0,to=480,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_lip2,troughcolor='#212121',command=lip2_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_lip2.place(x=x,y=y+30)							#Define a Scale and put it in position

	Scale_err = tk.Scale(root,label=None,
	from_=0,to=200,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_err,troughcolor='#212121',command=err_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_err.place(x=x,y=y+60)							#Define a Scale and put it in position

	canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
	canvas_cover.place(x=x,y=y+90)

	Btn_Render = tk.Button(root, width=10, text='Render',fg=color_text,bg='#212121',relief='ridge')
	Btn_Render.place(x=x+w+111,y=y+20)
	Btn_Render.bind('<ButtonPress-1>', call_Render)

	Btn_CVFL = tk.Button(root, width=10, text='CV FL',fg=color_text,bg='#212121',relief='ridge')
	Btn_CVFL.place(x=x+w+21,y=y+20)
	Btn_CVFL.bind('<ButtonPress-1>', call_CVFL)

	Btn_WB = tk.Button(root, width=23, text='LineColorSwitch',fg=color_text,bg='#212121',relief='ridge')
	Btn_WB.place(x=x+w+21,y=y+60)
	Btn_WB.bind('<ButtonPress-1>', call_WB)


def scale_FC(x,y,w):
	global canvas_show
	def R_send(event):
		canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
		time.sleep(0.03)
		# tcpClicSock.send(('hsvH %s'%var_R.get()).encode())

	def G_send(event):
		canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
		time.sleep(0.03)
		# tcpClicSock.send(('hsvS %s'%var_G.get()).encode())

	def B_send(event):
		canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
		time.sleep(0.03)
		# tcpClicSock.send(('hsvV %s'%var_B.get()).encode())

	def call_SET(event):
		tcpClicSock.send(('FCSET %s'%rgb2hsv(int(var_R.get()), int(var_G.get()), int(var_B.get()))).encode())

	Scale_R = tk.Scale(root,label=None,
	from_=0,to=255,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_R,troughcolor='#FF1744',command=R_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_R.place(x=x,y=y)							#Define a Scale and put it in position

	Scale_G = tk.Scale(root,label=None,
	from_=0,to=255,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_G,troughcolor='#00E676',command=G_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_G.place(x=x,y=y+30)							#Define a Scale and put it in position

	Scale_B = tk.Scale(root,label=None,
	from_=0,to=255,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_B,troughcolor='#2979FF',command=B_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_B.place(x=x,y=y+60)							#Define a Scale and put it in position

	canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
	canvas_cover.place(x=x,y=y+90)

	canvas_show=tk.Canvas(root,bg=RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())),height=35,width=170,highlightthickness=0)
	canvas_show.place(x=w+x+21,y=y+15)

	Btn_WB = tk.Button(root, width=23, text='Color Set',fg=color_text,bg='#212121',relief='ridge')
	Btn_WB.place(x=x+w+21,y=y+60)
	Btn_WB.bind('<ButtonPress-1>', call_SET)


def scale_ExpCom(x,y,w):#Z
	def EC_send(event):
		tcpClicSock.send(('setEC %s'%var_ec.get()).encode())
		time.sleep(0.03)

	def EC_default(event):
		var_ec.set(0)
		tcpClicSock.send(('defEC').encode())


	Scale_ExpCom = tk.Scale(root,label='Exposure Compensation Level',
	from_=-25,to=25,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_ec,troughcolor='#212121',command=EC_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_ExpCom.place(x=x,y=y)							#Define a Scale and put it in position

	canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
	canvas_cover.place(x=x,y=y+50)

	Btn_dEC = tk.Button(root, width=23,height=2, text='Set Default Exposure\nCompensation Level',fg=color_text,bg='#212121',relief='ridge')
	Btn_dEC.place(x=x+w+21,y=y+3)
	Btn_dEC.bind('<ButtonPress-1>', EC_default)


def function_buttons(x,y):
	global function_stu, Btn_function_1, Btn_function_2, Btn_function_3, Btn_function_4, Btn_function_5, Btn_function_6, Btn_function_7
	def call_function_1(event):
		if function_stu == 0:
			tcpClicSock.send(('function_1_on').encode())
		else:
			tcpClicSock.send(('function_1_off').encode())

	def call_function_2(event):
		if function_stu == 0:
			tcpClicSock.send(('function_2_on').encode())
		else:
			tcpClicSock.send(('function_2_off').encode())

	def call_function_3(event):
		if function_stu == 0:
			tcpClicSock.send(('function_3_on').encode())
		else:
			tcpClicSock.send(('function_3_off').encode())

	def call_function_4(event):
		if function_stu == 0:
			tcpClicSock.send(('function_4_on').encode())
		else:
			tcpClicSock.send(('function_4_off').encode())

	def call_function_5(event):
		if function_stu == 0:
			tcpClicSock.send(('function_5_on').encode())
		else:
			tcpClicSock.send(('function_5_off').encode())

	def call_function_6(event):
		if function_stu == 0:
			tcpClicSock.send(('function_6_on').encode())
		else:
			tcpClicSock.send(('function_6_off').encode())

	def call_function_7(event):
		if function_stu == 0:
			tcpClicSock.send(('function_7_on').encode())
		else:
			tcpClicSock.send(('function_7_off').encode())

	Btn_function_1 = tk.Button(root, width=8, text='RadarScan',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_2 = tk.Button(root, width=8, text='FindColor',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_3 = tk.Button(root, width=8, text='MotionGet',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_4 = tk.Button(root, width=8, text='Police',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_5 = tk.Button(root, width=8, text='Automatic',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_6 = tk.Button(root, width=8, text='SteadyCam',fg=color_text,bg=color_btn,relief='ridge')
	Btn_function_7 = tk.Button(root, width=8, text='Instruction',fg=color_text,bg=color_btn,relief='ridge')

	Btn_function_1.place(x=x,y=y)
	Btn_function_2.place(x=x,y=y+35)
	Btn_function_3.place(x=x,y=y+70)
	Btn_function_4.place(x=x,y=y+105)
	Btn_function_5.place(x=x,y=y+140)
	Btn_function_6.place(x=x,y=y+175)
	Btn_function_7.place(x=x,y=y+221)

	Btn_function_1.bind('<ButtonPress-1>', call_function_1)
	Btn_function_2.bind('<ButtonPress-1>', call_function_2)
	Btn_function_3.bind('<ButtonPress-1>', call_function_3)
	Btn_function_4.bind('<ButtonPress-1>', call_function_4)
	Btn_function_5.bind('<ButtonPress-1>', call_function_5)
	Btn_function_6.bind('<ButtonPress-1>', call_function_6)
	Btn_function_7.bind('<ButtonPress-1>', call_function_7)


def config_buttons(x,y):
	def call_SiLeft(event):
		tcpClicSock.send(('SiLeft').encode())

	def call_SiRight(event):
		tcpClicSock.send(('SiRight').encode())

	def call_SetGearMiddle(event):
		tcpClicSock.send(('PWM0MS').encode())

	def call_PWM1MS(event):
		tcpClicSock.send(('PWM1MS').encode())

	def call_PWM2MS(event):
		tcpClicSock.send(('PWM2MS').encode())

	def call_PWM3MS(event):
		tcpClicSock.send(('PWM3MS').encode())

	def call_PWM4MS(event):
		tcpClicSock.send(('PWM4MS').encode())

	def call_MoveInit(event):
		tcpClicSock.send(('PWMINIT').encode())

	def call_PWMDefault(event):
		tcpClicSock.send(('PWMD').encode())

	Btn_SiLeft = tk.Button(root, width=16, text='<PWM0 Turn Left',fg=color_text,bg=color_btn,relief='ridge')
	Btn_SiLeft.place(x=x,y=y)
	Btn_SiLeft.bind('<ButtonPress-1>', call_SiLeft)

	Btn_SiRight = tk.Button(root, width=16, text='PWM0 Turn Right>',fg=color_text,bg=color_btn,relief='ridge')
	Btn_SiRight.place(x=x+300,y=y)
	Btn_SiRight.bind('<ButtonPress-1>', call_SiRight)

	Btn_SetGearMiddle = tk.Button(root, width=16, text='<PWM0 Middle Set>',fg=color_text,bg=color_btn,relief='ridge')
	Btn_SetGearMiddle.place(x=x+150,y=y)
	Btn_SetGearMiddle.bind('<ButtonPress-1>', call_SetGearMiddle)

	Btn_PWM1MS = tk.Button(root, width=16, text='PWM1 Middle Set',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWM1MS.place(x=x,y=y+70)
	Btn_PWM1MS.bind('<ButtonPress-1>', call_PWM1MS)

	Btn_PWM2MS = tk.Button(root, width=16, text='PWM2 Middle Set',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWM2MS.place(x=x+150,y=y+70)
	Btn_PWM2MS.bind('<ButtonPress-1>', call_PWM2MS)

	Btn_PWM3MS = tk.Button(root, width=16, text='PWM3 Middle Set',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWM3MS.place(x=x+300,y=y+70)
	Btn_PWM3MS.bind('<ButtonPress-1>', call_PWM3MS)

	Btn_PWM4MS = tk.Button(root, width=16, text='PWM4 Middle Set',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWM4MS.place(x=x,y=y+140)
	Btn_PWM4MS.bind('<ButtonPress-1>', call_PWM4MS)

	Btn_PWM5MS = tk.Button(root, width=16, text='Move to InitPos',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWM5MS.place(x=x+150,y=y+140)
	Btn_PWM5MS.bind('<ButtonPress-1>', call_MoveInit)

	Btn_PWMDefault = tk.Button(root, width=16, text='PWM Default Set',fg=color_text,bg=color_btn,relief='ridge')
	Btn_PWMDefault.place(x=x+300,y=y+140)
	Btn_PWMDefault.bind('<ButtonPress-1>', call_PWMDefault)



def loop():
	global root, var_lip1, var_lip2, var_err, var_R, var_G, var_B, var_ec#Z
	root = tk.Tk()			
	root.title('GTank GUI')	  
	root.geometry('920x570')  #Z
	root.config(bg=color_bg)  

	var_lip1 = tk.StringVar()
	var_lip1.set(440)
	var_lip2 = tk.StringVar()
	var_lip2.set(380)
	var_err = tk.StringVar()
	var_err.set(20)

	var_R = tk.StringVar()
	var_R.set(80)
	var_G = tk.StringVar()
	var_G.set(80)
	var_B = tk.StringVar()
	var_B.set(80)

	var_ec = tk.StringVar() #Z
	var_ec.set(0)			#Z

	try:
		logo =tk.PhotoImage(file = 'logo.png')
		l_logo=tk.Label(root,image = logo,bg=color_bg)
		l_logo.place(x=30,y=13)
	except:
		pass

	motor_buttons(30,105)

	information_screen(330,15)

	connent_input(125,15)

	switch_button(30,195)

	servo_buttons(255,195)

	scale(30,230,203)

	ultrasonic_radar(30,290)

	function_buttons(395,290)

	scale_FL(470,0,238)

	scale_FC(470,135,238)

	scale_ExpCom(470,290,238) #Z

	config_buttons(470,360)

	root.mainloop()


if __name__ == '__main__':
	loop()
