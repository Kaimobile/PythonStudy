#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File    :   baidutest.py
@Time    :   2019-08-19
@Author  :   KAI
@Version :   2.2
@License :   (C) Copyright 2012-2019, Kaimobile
@Contact :   kyan@tju.edu.cn
@Desc    :   None
"""

import random
import datetime
import requests
import json
import pandas as pd 


class baiduLogin(object):
    '''Get data from BaiduIndex and return the list.

    Input: 
        The start and end date String like "YYYYmmdd".
        The index type "pc", "wireless", "all". (optional)
    Default: "all"
        The keyword.
        The Area Code. (optional)

    '''

    keyWord = 'baidu' # Only one word
    dataType = 'all' # "pc", "wireless", "all"
    area = 0 # Area code. 0 is default
    startDateStdStr = ''
    endDateStdStr = '' # "YYYYmmdd" is the standard form in the code

    dataTypeStd = 'all' # "pc", "wise", "all"
    startDate = None
    endDate = None

    indexList = []

    urlSearch = "http://index.baidu.com/api/SearchApi/index"
    urlFeedSearch = "http://index.baidu.com/api/FeedSearchApi/getFeedIndex"
    urlPtbk = "http://index.baidu.com/Interface/ptbk"

    Referer = "http://index.baidu.com/v2/main/index.html"
    headers = {
        "Host": "index.baidu.com",
        "User-Agent": '',
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Connection": "keep-alive",
    }
    agentList = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    ]
    cookies = {}

    def __init__(self, start:str, end:str, cookies:dict):
        '''
        Args:
            start: The start date like "yyyymmdd"
            end: The end date like "yyyymmdd"
            cookies: The cookies dict.
        '''
        self.keyWord = "baidu"
        self.dataType = "all"
        self.preDataType()
        self.area = 0
        self.startDateStdStr = start
        self.endDateStdStr = end
        self.preDateRange()
        self.cookies = cookies
        self.preRequest()
        pass 
    def setParameter(self, keyWord:"baidu", dataType:"all", area:0):
        '''
        Args:
            keyWord: The keyword.
            dataType: The index type "pc", "wireless", "all".
            area: The Area Code of city.
        '''
        self.keyWord = keyWord
        self.dataType = dataType
        self.preDataType()
        self.area = area
        pass
    def preDateRange(self):
        '''
        Prepare the stardard datetime object
        '''
        self.startDate = datetime.datetime.strptime(self.startDateStdStr, r"%Y%m%d")
        self.endDate = datetime.datetime.strptime(self.endDateStdStr, r"%Y%m%d")
        pass
    def preRequest(self):
        '''
        Preparation for the request headers
        '''
        self.headers["User-Agent"] = random.choice(self.agentList)
        self.headers["Referer"] = self.Referer
        pass
    def preDataType(self):
        '''
        Prepare the standard datatype for services.
        '''
        if self.dataType == "pc":
            self.dataTypeStd = "pc"
        elif self.dataType == "wireless":
            self.dataTypeStd = "wise"
        else:
            self.dataTypeStd = "all"
        pass
    def getPtbk(self, uid):
        '''Request for the ptbk

        Send uniqid to the website for the ptbk.

        Args:
            uid: The uniqid of the raw data

        Returns:
            ptbk of the uid.
        '''
        uidparam = dict([("uniqid",uid)])
        rA = requests.get(self.urlPtbk, headers=self.headers, params=uidparam, cookies=self.cookies)
        rA.encoding = 'unicode'
        rADict = json.loads(rA.text)
        #self.saveFile("uniqid", rADict["data"])
        return rADict["data"]
    def mainProcess(self):
        '''A whole process for get the data_list

        Get the raw data and decode the data.
        Then recheck the start and end of the date.
        Finally return the List.

        Returns:
            The data DateFrame of the index.
            If the keyword doesn't exist, return 0.
        '''
        param = {
            "area": self.area,
            "word": self.keyWord,
            "startDate": self.startDateStdStr,
            "endDate": self.endDateStdStr,
        }
        rA = requests.get(self.urlSearch, headers=self.headers, params=param, cookies=self.cookies)
        #print(rA.text)
        #self.saveFile("json", rA.text)
        indexDict = json.loads(rA.text)
        indexDictA = indexDict["data"]
        statusCode = str(indexDict["status"])
        if statusCode != "0":
            return 0
        indexDictB = indexDictA["userIndexes"]
        indexDictC = indexDictB[0]
        indexDictD = indexDictC[self.dataTypeStd]
        indexDictE = indexDictD["data"]
        indexUniqid = indexDictA["uniqid"]
        ptbk = self.getPtbk(indexUniqid)
        self.startDateStdStr = indexDictD["startDate"]
        self.endDateStdStr = indexDictD["endDate"]
        self.startDate = datetime.datetime.strptime(indexDictD["startDate"], r"%Y-%m-%d")
        self.endDate = datetime.datetime.strptime(indexDictD["endDate"], r"%Y-%m-%d")
        m = list(ptbk)
        d = dict(zip(m[:len(m)//2:], m[len(m)//2::]))
        a = ''.join(map(lambda x: d[x], indexDictE))
        self.indexList = []
        if a == '':
            return 0
        else:
            #self.saveFile("indexList", a)
            indexListTmp = a.split(",")
            for i in indexListTmp:
                if i == "":
                    self.indexList.append(0)
                else:
                    self.indexList.append(int(i))
            #datePeroid = (self.endDate - self.startDate).days + 1
            #dates = pd.date_range(self.startDateStdStr, periods=datePeroid)
            #self.indexTable = pd.DataFrame(self.indexList, index=dates, columns=[self.keyWord,])
            #self.indexTable = pd.DataFrame(index=dates, data={self.keyWord:self.indexList})
            #print(a)
            return self.indexList
    def changeKeyWord(self, newKeyWord:str):
        '''Change the keyWord.

        Args:
            newKeyWord: The new keyWord.

        '''
        self.keyWord = newKeyWord
        pass
    def changeAgent(self):
        '''
        Change the User-Agent
        '''
        self.headers["User-Agent"] = random.choice(self.agentList)
        pass
    def changeDataType(self, newDataType:str):
        '''
        Change the Datatype.
        '''
        self.dataType = newDataType
        self.preDataType()
        pass
    def changeArea(self, newAreaCode:int):
        '''
        Change the area code.
        '''
        self.area = newAreaCode
        pass
    def changeCookies(self, newCookies:list):
        '''
        Change the cookies.
        '''
        self.cookies = newCookies
        pass
    def saveFile(self, fileN, fileStr):
        f = open(fileN+".txt", "w", encoding="utf-8")
        f.write(fileStr)
        f.close()
        pass
    def openFile(self, fileN):
        f = open(fileN+".txt", "r", encoding="utf-8")
        fileStr = f.read()
        f.close()
        return fileStr
