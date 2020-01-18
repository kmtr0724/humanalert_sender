#!/usr/bin/python
import socket
import RPi.GPIO as GPIO
import time
import datetime

# -*- coding:utf-8 -*-

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)
port = 8000

def sendData(host,port,data):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2)
        client.connect((host, port)) 
        client.send(data) 
        response = client.recv(1024) 
        client.close()
        return response
    except socket.error as e:
        #print('failed to connect, try reconnect\n' + format(e))
        return False

def waitforBroadcast(port):
    s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(("",port))

    while True:
        msg, address = s.recvfrom(1024)
        if msg == "I'm sensor host":
            break
    s.close()
    return address[0]

def printConsole(str):
    dt_now = datetime.datetime.now()
    print format(dt_now.strftime('%Y-%m-%d %H:%M:%S')) + " " + format(str)

health_cnt=0
error_num=6
detected_flag=0
while True:
    if error_num > 5:
        printConsole("Host timeout wait for broadcast")
        host = waitforBroadcast(port)
        printConsole("Broadcast recieve addr=" + format(host))
        error_num = 0
        detected_flag=0
        health_cnt=0
    if detected_flag==0 and GPIO.input(18)==1:
        sendData(host,port,"alert")
        printConsole("Detected Send Alert")
        detected_flag=1
    if detected_flag>=1:
        detected_flag+=1
    if detected_flag > 100:
        detected_flag=0
    if health_cnt > 50:
        ret=sendData(host,port,"ping")
        health_cnt=0
        if ret==False or ret!="pong":
            error_num=error_num+1
    health_cnt+=1
    time.sleep(0.1)



