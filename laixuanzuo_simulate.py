#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File    :   laixuanzuo_simulate.py
@Time    :   2019-10-05
@Author  :   KAI YAN
@Version :   1.10
@License :   (C) Copyright 2012-2019, Kaimobile
@Contact :   kyan@tju.edu.cn
@Desc    :   None
"""

import time
import numpy as np 
from PIL import ImageGrab
import win32api
import win32con
import win32gui
import datetime
import random

class screenMonitor(object):
    '''
    Monitor the screen and get the status of 
    Seat 1 and Seat 2.
    '''
    ########## Layout of the authorisation Absolute Position #############
    # (0,0)  
    #    ____________________________________________
    #    |                                           |
    #    |                                           |
    #    |       (548,1228)                          |
    #    |            ______________________         |
    #    |           |                      |        |        
    #    |           |          .(690,1244) |        |
    #    |           |        RGB(7,193,96) |        |
    #    |           |______________________|        |
    #    |                           (731,1268)      |
    #    |___________________________________________|
    #                                           (1280,1400)
    #
    ########## Layout of the Selection Absolute Position #################
    #  (0,785)
    #    _________________________________________________________
    #   |                                                         |
    #   |                                                         |
    #   |            .                          .                 |
    #   |        (402,865)                  (912,865)             |  
    #   |    Valid RGB(115,163,232)     Invalid RGB(172,172,172)  |
    #   |                                                         |
    #   |_________________________________________________________|
    #                                                       (1280,985)
    ########### Layout of the Windows Absolute Position ##################
    #  (400,15)
    ########### Layout of the Index Absolute Position ####################
    #  (215,1366)
    seat1Pos = (402, 80) # The absolute pos is (402, 865)
    seat2Pos = (912, 80) # The absolute pos is (912, 865)
    seatPos = [seat1Pos, seat2Pos]
    authorPos = (690, 1244)
    windowsPos = (400, 15)
    indexPos = (215, 1366)

    seatPicPos = (0, 1035, 1280, 1235) #(0, 785, 1280, 985)
    authorPicPos = (0, 0, 1280, 1400)

    colorBlank = (255, 255, 255)
    colorValid = (115, 163, 232)
    colorInvalid = (172, 172, 172)
    colorAuthor = (7, 193, 96)
    def __init__(self):
        super()
    def judgeAuthorStatus(self):
        '''
        Return if authorization is needed.

        Return:
            True: Green button is checked. Need to click.
            False: No green button.
        '''
        img = ImageGrab.grab(self.authorPicPos)
        imgMat = img.load()
        s = self.judgePoint(imgMat[self.authorPos], self.colorAuthor)
        return s
    def judegSeatStatus(self, seatID):
        '''
        Return the current seatID status

        Args:
            seatID: 1 or 2
        Return:
            0: Blank, maybe loading
            1: Valid, select next
            2: Invalid
        '''
        img = ImageGrab.grab(self.seatPicPos)
        imgMat = img.load()
        s1 = self.judgePoint(imgMat[self.seatPos[seatID]], self.colorValid)
        s2 = self.judgePoint(imgMat[self.seatPos[seatID]], self.colorInvalid)
        key = 2
        if s1:
            key = 1
        elif s2:
            key = 2
        else:
            key = 0
        return key

    def judgePoint(self, pointA, pointB, threshold=3):
        '''
        Judge pointA and pointB are the same point.

        Args:
            pointA: The pointA RGB like (1,1,1)
            pointB: The pointB RGB
            threshold: The max difference
        Return:
            True: The same point
            False: different point
        '''
        key = True
        for i in range(3):
            if abs(pointA[i]-pointB[i]) > threshold:
                key = False
        return key
class simulateSeat(object):
    '''
    1. Select the main windows
    2. Finish the authorisation and wait until open
    3. refresh the index, judge if finished
    4. judge the seat status, if unable, return 3
    5. select the two seat at the same time
    '''    
    seatMonitor = None

    windowsPos = None
    indexPos = None
    seatPos = []
    startTime = None # Hour, Minute
    def __init__(self, sHour, sMinute):
        super()
        self.seatMonitor = screenMonitor()
        # Set the seatPos
        seat1Pos = (self.seatMonitor.seat1Pos[0]+self.seatMonitor.seatPicPos[0],
        self.seatMonitor.seat1Pos[1]+self.seatMonitor.seatPicPos[1])
        seat2Pos = (self.seatMonitor.seat2Pos[0]+self.seatMonitor.seatPicPos[0],
        self.seatMonitor.seat2Pos[1]+self.seatMonitor.seatPicPos[1])
        self.seatPos.append(seat1Pos)
        self.seatPos.append(seat2Pos)
        # Set windowsPos and indexPos
        self.windowsPos = self.seatMonitor.windowsPos
        self.indexPos = self.seatMonitor.indexPos
        # Set the start time
        self.startTime = (sHour, sMinute)
        pass
    def mouseClick(self,pos):
        x = pos[0]
        y = pos[1]
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        pass
    def selectWindows(self):
        self.mouseClick(self.windowsPos)
        pass
    def prepareBefore(self, sTime):
        '''
        Click the index button and finish the authorisation.
        Delay until the book platform open.
        
        Args:
            sTime: Start Time.
        Return:
            Delay until up to the startTime.
        '''
        # Finish the authorisation
        self.mouseClick(self.indexPos)
        a = self.seatMonitor.judgeAuthorStatus()
        if a:
            self.mouseClick(self.seatMonitor.authorPos)
        # Wait until it is up to the start Time
        t = datetime.datetime.now()
        while t.hour!=sTime[0] or t.minute!=sTime[1]:
            time.sleep(0.05)
            t = datetime.datetime.now()
        pass
    def refreshWindows(self):
        '''
        Refresh the web only
        '''
        self.mouseClick(self.indexPos)
        s = False
        for i in range(30):
            if self.seatMonitor.judegSeatStatus(0) != 0:
                s = True
                break
            else:
                time.sleep(0.5)
        return s
    def selectSeat(self):
        '''
        Select the any seat.
        '''
        self.mouseClick(self.seatPos[0])
        print("The 1st time select Seat1.Time: {}".format(datetime.datetime.now()))
        time.sleep(0.1)
        self.mouseClick(self.seatPos[1])
        print("The 1st time select Seat2.Time: {}".format(datetime.datetime.now()))
        time.sleep(1)
        self.mouseClick(self.seatPos[0])
        print("The 2nd time select Seat1.Time: {}".format(datetime.datetime.now()))
        time.sleep(0.1)
        self.mouseClick(self.seatPos[1])
        print("The 2nd time select Seat2.Time: {}".format(datetime.datetime.now()))

    def mainProcess(self):
        print("The program starts at {}".format(datetime.datetime.now()))
        self.selectWindows()
        self.prepareBefore(self.startTime)
        time.sleep(random.random())
        self.selectSeat()
        for i in range(1):
            s1 = self.refreshWindows()
            if s1:
                self.selectSeat()
        
a = simulateSeat(6,0)
a.mainProcess()
input("Wait...")