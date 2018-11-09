'''
@author:        Kai Yan
@license:       GNU GPLv2
@contact:       kyan@tju.edu.cn
'''

import requests
import json
import re
import pandas as pd
import bs4
import time
import random

def saveFile(filename, content):
    f = open(filename, 'w', encoding = 'utf-8')
    f.write(str(content))
    f.close()

def openFile(filename):
    f = open(filename, 'r', encoding = 'utf-8')
    fget = f.read()
    f.close()
    return fget

def delay():
    '''
    Delay less than 1 second and print it
    '''
    #Get a random number from 0 to 1
    t = random.random()
    #Print the time you will delay
    print("Delay Time: ",t)
    time.sleep(t)

def getTotalCommentCount(tripID):
    '''
    Return the total comment COUNT of the trip, which ID is tripID
    The COUNT is from the main INDEX
    tripID:             ID of the trip or attraction
    '''
    url = r'http://ticket.lvmama.com/scenic-' + str(tripID)
    t = requests.get(url).text
    #Use BeautifulSoup to Analysis the HTML
    soup = bs4.BeautifulSoup(t,'lxml')
    #the COUNT is in a <span> label; and the <span> label is in a <a> label, which has {id: allCmt}
    count = soup.find_all('a', attrs={'id': 'allCmt'})[0].find_all('span')
    #Use RE to delete everything except number
    commentCount = re.sub(r'[^\d+]','',count[0].string)
    return commentCount

def getInfo(page=1,totalCmt=3026,tripID=81):
    '''
    Return the String of the XHR received
    Page:               get the content of which page
    totalCmt:           total comment Count
    tripID:             ID of the trip or attration
    '''
    #Request URL
    url = r"http://ticket.lvmama.com/vst_front/comment/newPaginationOfComments"
    #Referer of header
    tripWeb = r'http://ticket.lvmama.com/scenic-'+str(tripID)
    #Content-Length of header
    contentLength = 108 + len(str(page)) + len(str(totalCmt)) + len(str(tripID))

    header = {
        'Host':             r'ticket.lvmama.com',
        #'User-Agent':       r'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'User-Agent':       r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Accept':           r'text/html, */*; q=0.01',
        'Accept-Language':  r'en-US,en;q=0.5',
        'Accept-Encoding':  r'gzip, deflate',
        'Referer':          tripWeb,
        'Content-Type':     r'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': r'XMLHttpRequest',
        'Content-Length':   str(contentLength),
        'DNT':              '1',
        'Connection':       r'keep-alive'
    }

    params = {
        'type':             'all',
        'currentPage':      page,
        'totalCount':       totalCmt,
        'placeId':          tripID,
        'productId':         '',
        'placeIdType':      'PLACE',
        'isPicture':        '',
        'isBest':           '',
        'isPOI':            'Y',
        'isELong':          'N'
    }
    #POST and receive r
    r = requests.post(url, headers = header, data = params)
    #saveFile('exp.txt',r.text)       #Debug
    #return the string of r
    return r.text


def dataProcess(t):
    '''
    Return a DataFrame, which has clear data
    t:                  the String of content
    '''
    #t = openFile('exp.txt')            #Debug
    #find all data you need from the string by regExp or bs4. These are ROUGH processes
    date = re.findall(r'<em>\d\d\d\d-\d\d-\d\d',t)
    newDate = []
    #user = re.findall(r'>.{0,3}\*\*\*\*.{0,3}<',t)
    #newUser = []
    useful = re.findall(r'有用<em>\d+</em>',t)
    newUseful = []
    scoreA = re.findall(r'景区服务.+\n+.+<i>\d',t)
    newScoreA = []
    scoreB = re.findall(r'游玩体验.+\n+.+<i>\d',t)
    newScoreB = []
    scoreC = re.findall(r'预订便捷.+\n+.+<i>\d',t)
    newScoreC = []
    scoreD = re.findall(r'性价比.+\n+.+<i>\d',t)
    newScoreD = []
    soup = bs4.BeautifulSoup(t,'lxml')
    comment = soup.find_all('div', attrs={'class': re.compile('ufeed-content')})
    p = ""
    newComment = []

    #Maybe there are some BUGs and some list couldn't be up to 10. So the times of loop is the minima of all lists
    totalListLen = min([len(date),len(useful),len(scoreA),len(scoreB),len(scoreC),len(scoreD),len(comment)])

    #find all data by regExp or replace function. These are EXACT processes
    for i in range(totalListLen):
        newDate.append(date[i].replace('<em>',''))
        #newUser.append(re.sub('>|<','',user[i]))
        newUseful.append(useful[i].replace('有用<em>','').replace('</em>',''))
        newScoreA.append(re.sub(r'[^\d+]','',scoreA[i]))
        newScoreB.append(re.sub(r'[^\d+]','',scoreB[i]))
        newScoreC.append(re.sub(r'[^\d+]','',scoreC[i]))
        newScoreD.append(re.sub(r'[^\d+]','',scoreD[i]))
        #Delete <div> Label
        p = str(comment[i]).replace('<div class="ufeed-content"> <!-- 展开时加showmore -->','').replace('</div>','')
        #Delete <span> Label
        p = re.sub(r'<span.+</span>','',p)
        #Delete head <a> Label
        p = re.sub(r'<a.+xmy">','',p)
        #Delete end </a> Label
        p = p.replace(r"</a>",'')
        #Delete \s and \n
        p = re.sub(r'\s|\n','',p)
        #Delete "【点评有奖第6季】"
        p = re.sub(r'【.+】','',p)
        newComment.append(p)

    #Make a new DataFrame and Return
    labelFrame = {
        #'UserId':       newUser,
        'Date':         newDate,
        'UsefulCount':  newUseful,
        'ServeScore':   newScoreA,
        'PlayScore':    newScoreB,
        'BookScore':    newScoreC,
        'PriceScore':   newScoreD,
        'Comment':      newComment
    }
    return pd.DataFrame(labelFrame)

def getOneTrip(tripID):
    totalCmt = getTotalCommentCount(tripID)
    #Calculate the whole pages
    totalPage = int(totalCmt) // 10 + 1
    #Make a null DataFrame
    finalFrame = pd.DataFrame()
    try:
        for i in range(totalPage):
            webInfo = getInfo(page=i+1,totalCmt=totalCmt,tripID=tripID)
            finalFrame = pd.concat([finalFrame,dataProcess(webInfo)])
            delay()
            print("Page: ",i+1," Of ",totalPage)
    finally:
        finalFrame.to_excel('lvmama'+str(tripID)+'.xlsx')

def main():
    #81 --> 周庄古镇
    tripList = [101243]     #101243 ->_-> CiQiKou of Chongqing 
    for tripID in tripList:
        getOneTrip(tripID)
    
main()