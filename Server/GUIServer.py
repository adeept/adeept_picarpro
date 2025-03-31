#!/usr/bin/env/python
# File name   : GUIServer.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date		  : 2025/03/26

import time
import threading
import Move as move
import os
import Info as info
import RPIservo

import Functions as functions
import RobotLight as robotLight
import Switch as switch
import socket
import ast
import FPV
import json

Dv = 1 #Directional variable
OLED_connection = 1
try:
    import OLED
    screen = OLED.OLED_ctrl()
    screen.start()
    screen.screen_show(1, 'ADEEPT.COM')
except:
    OLED_connection = 0
    print('OLED disconnected')
    pass

mark_test = 0

functionMode = 0
speed_set = 50
rad = 0.5
turnWiggle = 60

direction_command = 'no'
turn_command = 'no'


scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()

modeSelect = 'PT'

init_pwm = []
for i in range(8):
    init_pwm.append(scGear.initPos[i])
init_pwm0 = scGear.initPos[0]
init_pwm1 = scGear.initPos[1]
init_pwm2 = scGear.initPos[2]
init_pwm3 = scGear.initPos[3]
init_pwm4 = scGear.initPos[4]

fuc = functions.Functions()
fuc.setup()
fuc.start()

 
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def servoPosInit():
    scGear.initConfig(0,init_pwm[0],1)
    scGear.initConfig(1,init_pwm[1],1)
    scGear.initConfig(2,init_pwm[2],1)
    scGear.initConfig(3,init_pwm[3],1)
    scGear.initConfig(4,init_pwm[4],1)


def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
    global r
    newline=""
    str_num=str(new_num)
    with open(thisPath+"/RPIservo.py","r") as f:
        for line in f.readlines():
            if(line.find(initial) == 0):
                line = initial+"%s" %(str_num+"\n")
            newline += line
    with open(thisPath+"/RPIservo.py","w") as f:
        f.writelines(newline)


def FPV_thread():
    global fpv
    fpv=FPV.FPV()
    fpv.capture_thread(addr[0])


def ap_thread():
    #When using create_ap to turn on the Wi-Fi hotspot, the default IP address is 192.168.12.1. However, you can modify this default setting by using the --dhcp-range option. 
    os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")


def functionSelect(command_input, response):
    global functionMode
    if 'scan' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'SCANNING')
        if modeSelect == 'PT':
            scGear.moveAngle(2, -60  * Dv)
            radar_send = fuc.radarScan()
            radar_array = []
            for i in range(len(radar_send)):
               radar_array.append(radar_send[i][0])
            response['title'] = 'scanResult'
            response['data'] = radar_array
            time.sleep(0.3)
            functionMode = 0

    elif 'findColor' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'FindColor')
        fpv.FindColor(1)
        tcpCliSock.send(('FindColor').encode())

    elif 'motionGet' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'MotionGet')
        fpv.WatchDog(1)
        tcpCliSock.send(('WatchDog').encode())

    elif 'stopCV' == command_input:
        fpv.FindColor(0)
        fpv.WatchDog(0)
        FPV.FindLineMode = 0
        functionMode = 0
        time.sleep(0.3)
        move.motorStop()
        switch.switch(1,0)
        switch.switch(2,0)
        switch.switch(3,0)

    elif 'police' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'POLICE LIGHT')
        RL.police()

    elif 'policeOff' == command_input:
        functionMode = 0
        RL.pause()

    elif 'automatic' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'Automatic')
        if modeSelect == 'PT':
            scGear.moveAngle(2, -60  * Dv)
            fuc.automatic()
        else:
            fuc.pause() 

    elif 'automaticOff' == command_input:
        functionMode = 0
        fuc.pause()
        time.sleep(0.5)
        move.motorStop()
        time.sleep(0.5)

    elif 'trackLine' == command_input:
        fuc.trackLine()
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'TrackLine')

    elif 'trackLineOff' == command_input:
        functionMode = 0
        fuc.pause()
        move.motorStop()



def switchCtrl(command_input):
    if 'Switch_1_on' in command_input:
        switch.switch(1,1)

    elif 'Switch_1_off' in command_input:
        switch.switch(1,0)

    elif 'Switch_2_on' in command_input:
        switch.switch(2,1)

    elif 'Switch_2_off' in command_input:
        switch.switch(2,0)

    elif 'Switch_3_on' in command_input:
        switch.switch(3,1)

    elif 'Switch_3_off' in command_input:
        switch.switch(3,0) 


def robotCtrl(command_input):
    global direction_command, turn_command
    if 'forward' == command_input:
        direction_command = 'forward'
        move.move(speed_set, 'forward', 'no', rad)
    
    elif 'backward' == command_input:
        direction_command = 'backward'
        move.move(speed_set, 'backward', 'no', rad)

    elif 'DS' in command_input:
        direction_command = 'no'
        move.motorStop()

    elif 'left' == command_input:
        turn_command = 'left'
        scGear.moveAngle(0, 30  * Dv)
        time.sleep(0.15)
        move.move(speed_set, 'forward', 'no', rad)
        switch.switch(2,1)
        time.sleep(0.15)

    elif 'right' == command_input:
        turn_command = 'right'
        scGear.moveAngle(0,-30  * Dv)
        time.sleep(0.15)
        move.move(speed_set, 'forward', 'no', rad)
        switch.switch(1,1)
        time.sleep(0.15)

    elif 'TS' in command_input:
        turn_command = 'no'
        scGear.moveAngle(0, 0)
        move.motorStop()
        switch.switch(2,0)
        switch.switch(1,0)

    elif 'lookleft' == command_input:
        scGear.singleServo(1, 1, 3)

    elif 'lookright' == command_input:
        scGear.singleServo(1, -1, 3)

    elif 'LRstop' in command_input:
        scGear.stopWiggle()

    elif 'armup' == command_input:
        scGear.singleServo(2,  1, 3)

    elif 'armdown' == command_input:
        scGear.singleServo(2, -1, 3)

    elif 'armstop' in command_input:
        scGear.stopWiggle()

    elif 'handup' == command_input:
        scGear.singleServo(3, 1, 3)

    elif 'handdown' == command_input:
        scGear.singleServo(3, -1, 3)

    elif 'HAstop' in command_input:
        scGear.stopWiggle()

    elif 'grab' == command_input:
        scGear.singleServo(4, -1, 3)

    elif 'loose' == command_input:
        scGear.singleServo(4, 1, 3)

    elif 'stop' == command_input:
        scGear.stopWiggle()

    elif 'home' == command_input:
        scGear.moveServoInit([0])
        scGear.moveServoInit([1])
        scGear.moveServoInit([2])
        scGear.moveServoInit([3])
        scGear.moveServoInit([4])


def configPWM(command_input):
    global init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4

    if 'SiLeft' in command_input:
        numServo = int(command_input[7:])
        if numServo == 0:
            init_pwm0 += 2
            scGear.setPWM(0,init_pwm0)
        elif numServo == 1:
            init_pwm1 += 2
            scGear.setPWM(1,init_pwm1)
        elif numServo == 2:
            init_pwm2 -= 2
            scGear.setPWM(2,init_pwm2)
        elif numServo == 3:
            init_pwm3 -= 2
            scGear.setPWM(3,init_pwm3)
        elif numServo == 4:
            init_pwm4 -= 2
            scGear.setPWM(4,init_pwm4)

    if 'SiRight' in command_input:
        numServo = int(command_input[8:])
        if numServo == 0:
            init_pwm0 -= 2
            scGear.setPWM(0,init_pwm0)
        elif numServo == 1:
            init_pwm1 -= 2
            scGear.setPWM(1,init_pwm1)
        elif numServo == 2:
            init_pwm2 += 2
            scGear.setPWM(2,init_pwm2)
        elif numServo == 3:
            init_pwm3 += 2
            scGear.setPWM(3,init_pwm3)
        elif numServo == 4:
            init_pwm4 += 2
            scGear.setPWM(4,init_pwm4)

    if 'PWMMS' in command_input:
        numServo = int(command_input[6:])
        if numServo == 0:
            init_pwm0 = 90
        elif numServo == 1:
            init_pwm1 = 90
        elif numServo == 2:
            init_pwm2 = 90
        elif numServo == 3:
            init_pwm3 = 90
        elif numServo == 4:
            init_pwm4 = 90
        scGear.moveAngle(numServo, 0)

    if 'PWMINIT' == command_input:
        servoPosInit()
    elif 'PWMD' in command_input:
        init_pwm0 = 90 
        init_pwm1 = 90 
        init_pwm2 = 90 
        init_pwm3 = 90 
        init_pwm4 = 90
        for i in range(5):
            scGear.moveAngle(i, 0)



def wifi_check():
    global mark_test
    try:
        time.sleep(3)
        s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("1.1.1.1",80))
        ipaddr_check=s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        if OLED_connection:
            screen.screen_show(2, 'IP:'+ipaddr_check)
            screen.screen_show(3, 'AP MODE OFF')
        mark_test = 1  
    except:
        if mark_test == 1:
            mark_test = 0
            move.destroy()      # motor stop.
            scGear.moveInit()   # servo  back initial position.

        ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
        ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()                                  #Thread starts
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 10%')
        RL.setColor(0,16,50)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 30%')
        RL.setColor(0,16,100)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 50%')
        RL.setColor(0,16,150)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 70%')
        RL.setColor(0,16,200)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 90%')
        RL.setColor(0,16,255)
        time.sleep(1)
        if OLED_connection:
            screen.screen_show(2, 'AP Starting 100%')
        RL.setColor(35,255,35)
        if OLED_connection:
            screen.screen_show(2, 'IP:192.168.12.1')
            screen.screen_show(3, 'AP MODE ON')


def recv_msg(tcpCliSock):
    global speed_set, modeSelect
    move.setup()

    while True: 
        response = {
            'status' : 'ok',
            'title' : '',
            'data' : None
        }


        data = tcpCliSock.recv(BUFSIZ).decode()
        print(data)

        if not data:
            continue


        if isinstance(data,str):
            robotCtrl(data)

            switchCtrl(data)

            functionSelect(data, response)

            configPWM(data)

            if 'get_info' == data:
                response['title'] = 'get_info'
                response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

            if 'wsB' in data:
                try:
                    set_B=data.split()
                    speed_set = int(set_B[1])
                except:
                    pass

            elif 'AR' == data:
                modeSelect = 'AR'
                screen.screen_show(4, 'ARM MODE ON')
                try:
                    fpv.changeMode('ARM MODE ON')
                except:
                    pass

            elif 'PT' == data:
                modeSelect = 'PT'
                screen.screen_show(4, 'PT MODE ON')
                try:
                    fpv.changeMode('PT MODE ON')
                except:
                    pass

            #CVFL
            elif 'CVFL' == data:
                FPV.FindLineMode = 1
                tcpCliSock.send(('CVFL_on').encode())


            elif 'CVFLColorSet' in data:
                color = int(data.split()[1])
                FPV.lineColorSet = color

            elif 'CVFLL1' in data:
                try:
                    set_lip1=data.split()
                    lip1_set = int(set_lip1[1])
                    FPV.linePos_1 = lip1_set
                except:
                    pass

            elif 'CVFLL2' in data:
                try:
                    set_lip2=data.split()
                    lip2_set = int(set_lip1[1])
                    FPV.linePos_2 = lip2_set
                except:
                    pass

            elif 'CVFLSP' in data:
                try:
                    set_err=data.split()
                    err_set = int(set_lip1[1])
                    FPV.findLineError = err_set
                except:
                    pass

            elif 'defEC' in data:#Z
                fpv.defaultExpCom()

            elif 'findColorSet' in data:
                try:
                    command_dict = ast.literal_eval(data)
                    if 'data' in command_dict and len(command_dict['data']) == 3:
                        r, g, b = command_dict['data']
                        fpv.colorFindSet(r, g, b)
                        print(f"color: r={r}, g={g}, b={b}")
                except (SyntaxError, ValueError):
                    print("The received string format is incorrect and cannot be parsed.")
                

        if not functionMode:
            if OLED_connection:
                screen.screen_show(5,'Functions OFF')
        else:
            pass
        response = json.dumps(response)
        tcpCliSock.sendall(response.encode())

def test_Network_Connection():
    while True:
        try:
            s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("1.1.1.1",80))
            s.close()
        except:
            move.destroy()
        
        time.sleep(0.5)

if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()                                  

    
    try:
        RL=robotLight.RobotWS2812()
        RL.start()
        RL.breath(70,70,255)
    except:
        print('Use "sudo pip3 install rpi_ws281x" to install WS_281x package\n')
        pass

    HOST = ''
    PORT = 10223                              #Define port serial 
    BUFSIZ = 1024                             #Define buffer size
    ADDR = (HOST, PORT)

   
    wifi_check()
    try:                  #Start server,waiting for client
        tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        tcpSerSock.bind(ADDR)
        tcpSerSock.listen(5)                   
        print("Waiting for client connection")
        tcpCliSock, addr = tcpSerSock.accept()
        print("Connected to the client :" + str(addr))
        fps_threading=threading.Thread(target=FPV_thread)         #Define a thread for FPV and OpenCV
        fps_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
        fps_threading.start()   
        recv_msg(tcpCliSock)  
    except Exception as e:
        print(e)
        RL.setColor(0,0,0)

    try:
        RL.setColor(0,0,0)
    except:
        pass

