#!/usr/bin/env/python
# File name   : WebServer.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/03/26
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
import asyncio
import websockets
import json
import app
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


functionMode = 1
speed_set = 50
rad = 0.5


scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()
modeSelect = 'PT'

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

direction_command = 'no'
turn_command = 'no'

def servoPosInit():
    scGear.initConfig(0,init_pwm0,1)
    scGear.initConfig(1,init_pwm1,1)
    scGear.initConfig(2,init_pwm2,1)
    scGear.initConfig(3,init_pwm3,1)
    scGear.initConfig(4,init_pwm4,1)


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

def ap_thread():
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
            response['title'] = 'scanResult'
            response['data'] = radar_send
            time.sleep(0.3)
            functionMode = 0

    elif 'findColor' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'FindColor')
        if modeSelect == 'PT':
            flask_app.modeselect('findColor')

    elif 'motionGet' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'MotionGet')
        flask_app.modeselect('watchDog')

    elif 'stopCV' == command_input:
        flask_app.modeselect('none')
        functionMode = 0
        switch.switch(1,0)
        switch.switch(2,0)
        switch.switch(3,0)
        move.motorStop()
    

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
        fuc.pause()
        time.sleep(0.5)
        move.motorStop()
        time.sleep(0.5)
        functionMode = 0

    elif 'trackLine' == command_input:
        fuc.trackLine()
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'TrackLine')

    elif 'trackLineOff' == command_input:
        fuc.pause()
        move.motorStop()
        functionMode = 0

    elif 'police' == command_input:
        if OLED_connection:
            functionMode = 1
            screen.screen_show(5,'POLICE LIGHT')
        RL.police()
        pass

    elif 'policeOff' == command_input:
        RL.breath(75,85,90)
        functionMode = 0
        pass


def switchCtrl(command_input, response):
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


def robotCtrl(command_input, response):
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
        scGear.singleServo(1,-1, 3)

    elif 'LRstop' in command_input:
        scGear.stopWiggle()


    elif 'armup' == command_input:
        scGear.singleServo(2, 1, 3)

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

def configPWM(command_input, response):
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
    try:
        s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("1.1.1.1",80))
        ipaddr_check=s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        if OLED_connection:
            screen.screen_show(2, 'IP:'+ipaddr_check)
            screen.screen_show(3, 'AP MODE OFF')
    except:
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

async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)

async def recv_msg(websocket):
    global speed_set, modeSelect
    move.setup()

    while True: 
        response = {
            'status' : 'ok',
            'title' : '',
            'data' : None
        }

        data = ''
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')

        if not data:
            continue

        if isinstance(data,str):
            robotCtrl(data, response)

            switchCtrl(data, response)

            functionSelect(data, response)

            configPWM(data, response)

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
                flask_app.modeselect('findlineCV')

            elif 'CVFLColorSet' in data:
                color = int(data.split()[1])
                flask_app.camera.colorSet(color)

            elif 'CVFLL1' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_1(pos)

            elif 'CVFLL2' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_2(pos)

            elif 'CVFLSP' in data:
                err = int(data.split()[1])
                flask_app.camera.errorSet(err)

            elif 'defEC' in data:#Z
                fpv.defaultExpCom()

        elif(isinstance(data,dict)):
            if data['title'] == "findColorSet":
                color = data['data']
                flask_app.colorFindSet(color[0],color[1],color[2])

        if not functionMode:
            if OLED_connection:
                screen.screen_show(5,'Functions OFF')
        else:
            pass
        print(data)
        response = json.dumps(response)
        await websocket.send(response)

async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)

if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()

    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()
    try:
        RL=robotLight.RobotWS2812()
        RL.start()
        RL.breath(70,70,255)
    except:
        print('Use "sudo pip3 install rpi_ws281x" to install WS_281x package\n')
        pass

    while  1:
        wifi_check()
        try:                  #Start server,waiting for client
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')

            break
        except Exception as e:
            print(e)
            RL.setColor(0,0,0)

        try:
            RL.setColor(0,80,255)
        except:
            pass
    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
        RL.setColor(0,0,0)
        move.destroy()
