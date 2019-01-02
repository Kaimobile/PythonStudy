'''
Nov 27， 2018
@author:        Kai Yan
@license:       GNU GPLv3
@contact:       kyan@tju.edu.cn
'''
import gensim
import jieba
import jieba.posseg as psg
import xlrd
import re
from gensim.models import word2vec 
import logging
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
import requests
import time
import random
import math

class Weibo:

    datePartA = []
    datePartB = []
    dateTotal = []

    urlA = r"https://weibo.com/p/"
    urlB = r"https://weibo.com/p/aj/v6/mblog/mbloglist"

    #=================Structure of Page and CurrentPage=======================
    #                                            PageBar
    # Page:                 1       2       3       -
    # CurrentPage:  A       0       3       6       -
    #               B1      1       4       7       0
    #               B2      2       5       8       1
    #=========================================================================
    #Total pages you need
    page = 0
    #The ID of scenery 
    pId = 0
    #current page now(small page)
    cp = 0
    #Page now(big page)
    p = 1

    userAgentList = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    ]

    #https://weibo.com/p/100101B2094651D56EA2FA469A?feed_filter=timeline&feed_sort=timeline&current_page=9&since_id=&page=23#feedtop

    headersA = {
        "Host":                         "weibo.com",
        "User-Agent":                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Accept":                       "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language":              "zh-CN,zh;q=0.9",
        "Accept-Encoding":              "gzip, deflate, br",
        #Change in __init__()
        "Referer":                      "",
        "DNT":                          "1",
        "Connection":                   "keep-alive",
        "Upgrade-Insecure-Requests":    "1"
    }

    headersB = {
        "Host":                         "weibo.com",
        "User-Agent":                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Accept":                       "*/*",
        "Accept-Language":              "zh-CN,zh;q=0.9",
        "Accept-Encoding":              "gzip, deflate, br",
        #Change in getDatePartB()
        "Referer":                      "",
        "Content-Type":                 "application/x-www-form-urlencoded",
        "X-Requested-With":             "XMLHttpRequest",
        "DNT":                          "1",
        "Connection":                   "keep-alive"
    }

    paramsA = {
        #Change in getDatePartA()
        "__ref":                        "",
        #Change in getDatePartA()
        "_t":                           "",
        "ajaxpagelet":                  1,
        "ajaxpagelet_v6":               1,
        #Change in getDatePartA()
        "current_page":                 "",
        "feed_filter":              	"timeline",
        "feed_sort":                	"timeline",
        #Change in getDatePartA()
        "page":                         "",
        "pids":                         "Pl_Third_App__17",
        "since_id":                     "",
    }

    paramsB = {
        #Change in getDatePartB(), current Linux time
        "__rnd":                        "",
        "ajwvr":                        6,
        #Change in getDatePartB()
        "current_page":                 "",
        #Change in __init__()
        "domain":                       "",
        #Change in __init__()
        "domain_op":                    "",
        "feed_type":                    1,
        #Change in __init__()
        "id":                           "",
        #Change in getDatePartB()
        "page":                         "",
        #Change in getDatePartB()
        "pagebar":                      "",
        "pl_name":                      "Pl_Third_App__17",
        #Change in getDatePartB()
        "pre_page":                     "",
        #Change in __init__()
        "script_uri":                   "",
        "since_id":                     "",
        "tab":                          "home",
    }

    cookies = {}

    def __init__(self,allPage,pid,cookie):
        '''
        fName:      name of the scene       string
        allPage:    total pages you want    int
        pid:        the id of scenery       string
        cookie:     cookies dict            dict
        '''
        self.page = allPage
        self.pId = pid
        self.urlA = self.urlA + self.pId
        self.cookies = cookie
        #Change headersA Referer
        self.headersA["Referer"] = r"https://weibo.com/p/"+self.pId
        #Change paramsB
        self.paramsB["domain"] = self.pId[0:6]
        self.paramsB["domain_op"] = self.pId[0:6]
        self.paramsB["id"] = self.pId
        self.paramsB["script_uri"] = "/p/"+self.pId
        pass

    def changeUserAgent(self):
        '''
        Change UserAgent in headers A/B/C from the userAgentList
        '''
        t = int(random.random()*len(self.userAgentList))
        self.headersA["User-Agent"] = self.userAgentList[t]
        self.headersB["User-Agent"] = self.userAgentList[t]
        pass

    def delay(self,rate = 5):
        '''
        Delay less than 1 second and print it
        params             function             range           default
        rate         the rate to 1 second      1 - inf             5         
        '''
        t = random.random()*rate
        print("Delay Time: ",t)
        time.sleep(t)
        pass

    def getDatePartA(self):
        '''
        Use current p and cp to get datePartA, then extend the dateTotal
        '''
        #Change ref in params
        if self.p == 1:
            self.paramsA["__ref"] = self.headersA["Referer"]
        else:
            self.paramsA["__ref"] = "/p/"+self.pId+"?feed_filter=timeline&feed_sort=timeline&current_page="+str(self.cp-3)+"&since_id=&page="+str(self.p-1)+"#feedtop"
        #Change Linux time
        self.paramsA["_t"] = "FM_" + str(int(time.time()))
        #Change current time
        self.paramsA["current_page"] = self.cp
        #Change page
        self.paramsA["page"] = self.p
        #Requests
        rA = requests.get(self.urlA, headers = self.headersA, params = self.paramsA , cookies = self.cookies)
        tA = rA.text
        #Get List
        self.datePartA = re.findall(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}",tA)
        self.dateTotal.extend(self.datePartA)
        pass
    
    def getDatePartB(self):
        '''
        Use current p and cp to get datePartB, then extend the dateTotal
        '''
        self.headersB["Referer"] = r"https://weibo.com/p/"+self.pId+"?current_page="+str(3*self.p-3)+"&since_id=&page="+str(self.p)
        #Change current Linux time
        self.paramsB["__rnd"] = str(int(time.time()))
        #Change current page
        self.paramsB["current_page"] = str(self.cp)
        #Change page
        self.paramsB["page"] = str(self.p)
        #Change page bar
        self.paramsB["pagebar"] = str(self.cp - 2*self.p - 1)
        #Change pre page
        self.paramsB["pre_page"] = self.p
        #Requests
        rB = requests.get(self.urlB, headers = self.headersB, params = self.paramsB , cookies = self.cookies)
        tB = rB.text
        #Get List
        self.datePartB = re.findall(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}",tB)
        self.dateTotal.extend(self.datePartB)
        pass
    
    def getTotalPage(self,totalpage = 0):
        '''
        Get dateTotal of totalPage
        params             function             range           default
        totalpage      the page you want       1 - inf         self.page
        Warning:    Use Try-finally sentence, add save in finally part
        '''
        if totalpage == 0:
            totalpage = self.page
        for i in range(totalpage):
            self.p = i + 1
            self.getDatePartA()
            self.delay(2)
            self.cp = self.cp + 1
            self.getDatePartB()
            self.delay(2)
            self.cp = self.cp + 1
            self.delay(2)
            self.getDatePartB()
            self.cp = self.cp + 1
            print("You are getting Page: ",i+1)
        pass
    
    def saveTotalPageTxt(self, fileName = "test"):
        '''
        Save the dateTotal to text file
        params             function             range           default
        fileName        name of text             ---            "text"
        '''
        f = open(fileName+".txt","w",encoding = "utf-8")
        f.write(str(self.dateTotal))
        f.close()
        pass

    def openTotalPageTxt(self, fileName = "test"):
        '''
        Open the dateTotal from text file
        '''
        f = open(fileName+".txt","r",encoding = "utf-8")
        self.dateTotal = eval(f.read())
        f.close()
        pass

    def saveTotalPageCsv(self, fileName = "test"):
        '''
        Save the dateTotal to csv file
        params             function             range           default
        fileName          name of csv            ---            "text"
        '''
        name = ["Time"]
        tempData = pd.DataFrame(columns=name, data = self.dateTotal)
        tempData.to_csv(fileName+".csv",encoding = "utf-8")
        pass

class GetWeibo:

    cookies = {
        "_s_tentry":                "passport.weibo.com",
        "ALF":                      "1574959213",
        "Apache":                   "7638528373018.554.1543423194059",
        "cross_origin_proto":       "SSL",
        "login_sid_t":              "ff10f35e8098267f58babc38c14e946a",
        "SCF":                      "Ai-M73TVvQwOGtZwdz4hznT8jAkvrqCJVU_xX8rT8vI29vbro0UzQilPhNJ6x6AtMFCptDIzSbymVYt2wDlkzLU.",
        "SINAGLOBAL":               "7638528373018.554.1543423194059",
        "SSOLoginState":            "1543423213",
        "SUB":                      "_2A252-rS_DeRhGeNN6VMV-CvMzz6IHXVScaF3rDV8PUNbmtAKLWjDkW9NSd-_hAwdBXj6YdbUKAKuj4PtWLo3e0fp",
        "SUBP":                     "0033WrSXqPxfM725Ws9jqgMF55529P9D9WF1rosoawEHoQeXxpEv8pmc5JpX5K2hUgL.Fo-0eo2X1h-7Shz2dJLoI7DS9-xyd2vRIgxL",
        "SUHB":                     "0d4OkJmX7b2xI2",
        "TC-Page-G0":               "4e714161a27175839f5a8e7411c8b98c",
        "TC-V5-G0":                 "a472c6c9af48bc4b9df1f924ca5cce70",
        "Ugrow-G0":                 "169004153682ef91866609488943c77f",
        "ULV":                      "1543423194082:1:1:1:7638528373018.554.1543423194059:",
        "un":                       "18633315573",
        "wb_view_log":              "2560*14401",
        "wb_view_log_5321485042":   "2560*14401",
        "WBStorage":                "f44cc46b96043278|undefined",
        "wvr":                      "6"
    }

    pid = "100101B2094652D369A7FA499A"

    w = Weibo(25,pid,cookies)

    def getWeiboDate(self):
        try:
            self.w.getTotalPage()
        finally:
            print(len(self.w.dateTotal))
            self.w.saveTotalPageTxt(self.pid[-6:])
            self.w.saveTotalPageCsv(self.pid[-6:])
        pass

class WordPre:
    #The file Name
    fileName = ""
    #Total String of comment
    totalWord = ""
    #Splitted String by jieba
    jiebaWord = ""
    #Stop word list
    stopWordList = []
    #The stopword list you can add yourself
    addStopWordList = ['\n',' ','「']

        #AdJiebaWord  --> Advanced Jieba Words
        #adJiebaWord = ""
        #AdJiebaList  --> Advanced Jieba List
        #nWordList = []
        #aWordList = []
        #vWordList = []

    #AdJiebaDict  --> Advanced Jieba Dictionary
    '''
    key:        word
    values:     count of the word
    '''
    nWordDict = {}
    aWordDict = {}
    vWordDict = {}

    #AdJiebaSorted  --> Advanced Jieba Sorted Dictionary
    '''
    sorted tuple word descending list, from large to small. eg: [(a1,b1),(a2,b2)...]
    a1:         word
    b1:         count of the word
    '''
    nWordSorted = []
    aWordSorted = []
    vWordSorted = []

    def __init__(self,fileN):
        '''
        Different filaName tells different Class
        '''
        self.fileName = fileN
        pass
    
    #import xlrd
    def getTotalWordFromExcel(self,colsID ,rowsID = 1,sheetIndex = 0,sheetType = "xlsx"):
        '''
        You should at least input colsID, which is Real Col(at least 1) and it contains comments
        params                 function                                            range                    default
        colsID:         the Col which you need                                  ( 1 - inf )                   ---
        rowsID:         which row starts catching                               ( 1 - inf )                    1
        sheetIndex:     which sheet do you need, default is 0, the first one    ( 0 - inf )                    0
        sheetType:      type of Excel, "xlsx" or "xls"                          ( "xlsx", "xls" )            "xlsx"
        '''
        #Read the Excel Sheet
        shx = xlrd.open_workbook(self.fileName+"."+sheetType)
        tp = []
        try:
            #Find the sheet with sheetIndex
            sh = shx.sheet_by_index(sheetIndex)
        except:
            print("no that sheet index",sheetIndex,"Please try again")
        else:
            #Get the total ROW count
            nrows = sh.nrows
            #Add the content in each cell to the "totalWord"
            for i in range(rowsID,nrows):
                tp.append(str(sh.cell_value(i,colsID-1)))
        self.totalWord = ' '.join(tp)
        pass

    def saveTotalWord(self):
        '''
        Save the variable "totalWord" to a text file
        '''
        f = open(self.fileName + ".txt", 'w', encoding = 'utf-8')
        f.write(self.totalWord)
        f.close()
        print("Save " + self.fileName + ".txt successfully")
        pass
    
    def openTotalWord(self):
        '''
        Open a text file to the variable "totalWord"
        '''
        f = open(self.fileName+".txt", 'r', encoding = 'utf-8')
        self.totalWord = f.read()
        f.close()       
        pass

    def getStopWord(self , stopWord = "stopwords.txt" , addStopWord = addStopWordList):
        '''
        Config the stopWordList variable
        params                  function                           range                    default
        stopWord:           File name of the stopwords         python Str Type          "stopwords.txt"
        addStopWord:        A list of stop words               python List Type         addStopWordList
        '''
        f = open(stopWord,'r', encoding = 'utf-8')
        while 1:
            #Read one line, because there is only one word in each line
            line = f.readline()
            #Stop reading
            if not line:
                break
            #Replace the "\n" and add it to the "stopWordList"
            self.stopWordList.append(line.replace("\n",''))
        #Add the users' stopwords to the "stopWordList"
        self.stopWordList.extend(addStopWord)
        pass

    #import jieba
    def getJiebaWord(self , stopWord = "stopwords.txt", addStopWord = addStopWordList):
        '''
        Old form of getJiebaWord
        Notice: "totalWord" is needed
        '''
        #generate the stopWordList variable
        self.getStopWord(stopWord,addStopWord)
        
        #Get the Jieba String
        tempWord = self.totalWord
        tempWord.replace('\t','').replace('\n','').replace('.','')
        segWord = jieba.cut(tempWord, cut_all = False)
        for word in segWord:
            if word not in self.stopWordList:
                self.jiebaWord = self.jiebaWord + word + ' '
        print("You get JiebaWord "+self.fileName+" !")
        pass

    #import jieba.posseg as psg 
    def getAdJiebaF(self):
        '''
        Get Noun, Verb and Adjective List from "totalWord"
        Notice: "totalWord" is needed
        '''
        seq = psg.cut(self.totalWord)
        tempList = []
        self.nWordDict.clear()
        self.vWordDict.clear()
        self.aWordDict.clear()
        for k in seq:
            if k.flag[0] == 'n':
                #count the frequency of Noun Words
                self.nWordDict[k.word] = self.nWordDict.get(k.word,0) + 1
            #Get Advanced Jieba List
                #self.nWordList.append(k.word)
                #Get Advanced Jieba Word
                tempList.append(k.word)
            elif k.flag[0] == 'a':
                #count the frequency of Adjective Words
                self.aWordDict[k.word] = self.aWordDict.get(k.word,0) + 1
            #Get Advanced Jieba List
                #self.aWordList.append(k.word)
                #Get Advanced Jieba Word
                tempList.append(k.word)
            elif k.flag[0] == 'v':
                #count the frequency of Verb Words
                self.vWordDict[k.word] = self.vWordDict.get(k.word,0) + 1
            #Get Advanced Jieba List
                #self.vWordList.append(k.word)
                #Get Advanced Jieba Word
                tempList.append(k.word)
        #Sort these three Dict
        self.nWordSorted = sorted(self.nWordDict.items(), key = lambda x:x[1], reverse = True)
        self.aWordSorted = sorted(self.aWordDict.items(), key = lambda x:x[1], reverse = True)
        self.vWordSorted = sorted(self.vWordDict.items(), key = lambda x:x[1], reverse = True)
        #Create jiebaWord
        self.jiebaWord = ' '.join(tempList)
        print("You Sorted "+self.fileName+" !")
        pass

    def saveAdJiebaF(self):
        '''
        Save the variable nWordSorted, aWordSorted, vWordSorted
        '''
        f = open(self.fileName+"nWordSorted.txt" , "w" , encoding = 'utf-8')
        f.write(str(self.nWordSorted))
        f.close()
        f = open(self.fileName+"aWordSorted.txt" , "w" , encoding = 'utf-8')
        f.write(str(self.aWordSorted))
        f.close()
        f = open(self.fileName+"vWordSorted.txt" , "w" , encoding = 'utf-8')
        f.write(str(self.vWordSorted))
        f.close()
        pass
    
    def openAdJiebaF(self):
        '''
        Open the variable nWordSorted, aWordSorted, vWordSorted
        '''
        f = open(self.fileName+"nWordSorted.txt" , "r" , encoding = 'utf-8')
        self.nWordSorted = eval(f.read())
        f.close()
        f = open(self.fileName+"aWordSorted.txt" , "r" , encoding = 'utf-8')
        self.aWordSorted = eval(f.read())
        f.close()
        f = open(self.fileName+"vWordSorted.txt" , "r" , encoding = 'utf-8')
        self.vWordSorted = eval(f.read())
        f.close()
        pass

    def saveJiebaWord(self):
        '''
        Save the variable "jiebaWord" to a text file
        '''
        f = open(self.fileName+"Jieba.txt", 'w', encoding = 'utf-8')
        f.write(self.jiebaWord)
        f.close()
        pass

    def openJiebaWord(self):
        '''
        Open a text file to the variable "jiebaWord"
        '''
        f = open(self.fileName+"Jieba.txt", 'r', encoding = 'utf-8')
        self.jiebaWord = f.read()
        f.close()  
        pass

class Word2:
    fileName = ''
    word2VecModel = None

    def __init__(self, fn):
        self.fileName = fn

    #from gensim.models import word2vec 
    #import logging
    def word2Vector(self):
        '''
        Create Word2Vector Model
        Notice: "Jieba.txt" is needed
        '''
        #Config something display
        logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
        #Using Text8Corpus to process Corpus
        sentences = word2vec.Text8Corpus(self.fileName+"Jieba.txt")

        #window：表示当前词与预测词在一个句子中的最大距离是多少, default = 5
        #sentence：可以是一个list，建议使用BrownCorpus,Text8Corpus或·ineSentence构建
        #iter：迭代次数, default = 5
        #size：size of vector
        #https://blog.csdn.net/szlcw1/article/details/52751314
        self.word2VecModel = word2vec.Word2Vec(sentences, size=200)

    def saveModel(self):
        self.word2VecModel.save(self.fileName+".model")
    
    def openModel(self):
        self.word2VecModel = gensim.models.Word2Vec.load(self.fileName+".model")

class Compute:
    fileList = ["BaDaLing", 
                "BingMaYong",
                "BuDaLaGong",
                "DongFangMingZhu",
                "FengHuang",
                "GuGong",
                "GuLangYu",
                "HuaShan",
                "JiuZhaiGou",
                "LiJiang",
                "PingYao",
                "QingHaiHu",
                "TongLi",
                "WuZhen",
                "XiHu",
                "XiTang",
                "YiHeYuan",
                "ZhouZhuang"]
    testList = [
        "HuangShan",
        "LiJiang2",
        "MoGaoKu",
        "ZhangJiaJie",
        "ZhongShanLing"
    ]
    totalFileName = "TotalCom"
    fileListId = 0
    wordObj = None
    totalWordObj = None
    wordVec = None

    '''
    Compute W^v. 
    Choose top k from each type. Top m is 1.
    '''
    #Size of each n/adj/v, top 3*k word of totalWords
    k = 0
    #Summary of top 3*k n/adj/v
    totalWordList = []
    #Matrix of vector cosine
    wordMatrix = None
    #0-1 Matrix of vector cosine, top m words is 1, others is 0.
    m = 0
    wordNetMatrix = None

    '''
    Compute X.
    Count top k words(in totalWordList) in each scenery
    '''
    #Matrix of each scenery in the 3*k top words
    sceneWordMatrix = None

    '''
    Compute W^u.
    Top u is 1
    '''
    #Dict of TF n. adj. v. of current fileListId
    nTFDict = {}
    aTFDict = {}
    vTFDict = {}
    #Dict of IDF n/adj/v of all fileList
    nIDFDict = {}
    aIDFDict = {}
    vIDFDict = {}
    #List of TF-IDF n/adj/v of all fileList
    '''
    sorted tuple word descending list, from large to small. eg: [(a1,b1),(a2,b2)...]
    a1:         word
    b1:         TF-IDF
    '''
    nTFIDFList = []
    aTFIDFList = []
    vTFIDFList = []
    #Correlation Matrix
    corrMartix = None
    #Correlation 0-1 Matrix, top u words is 1, others is 0
    u = 0
    corrNetMartix = None

    '''
    Save U0(weekday) and U0(weekend)
    '''
    #U0 weekday
    timeWeekdayMatrix = None
    #U0 weekend
    timeWeekendMatrix = None

    '''
    Notice: 18-->Num of scene, 300-->3*100, 5-->Num of Test
    X:  18*300
    Xt: 5*300
    U:  18*24
    V:  300*24
    Du: 18*18 (cnt of corrNetMatrix)
    U0a:18*24 (weekday)
    U0b:18*24 (weekend)
    Wu: 18*18
    Wv: 300*300
    Gu: 18*18 (control weibo time, 0 for miss, 1 for normal)
    '''
    X = None
    U = None
    V = None
    Du = None
    Dv = None
    U0a = None
    U0b = None
    Wu = None
    Wv = None
    Gu = None

    def __init__(self , matSize = 5):
        #Init k,m,u to Default
        self.k = matSize
        self.m = int(self.k*0.5)
        self.u = 2
        #Init all Matrix
            #Matrix 3k*3k, W^v
        self.wordMatrix = np.zeros(shape = (matSize*3,matSize*3))
        self.wordNetMatrix = np.zeros(shape = (matSize*3,matSize*3))
            #Matrix i*3k (i is the number of scenery) 
        self.sceneWordMatrix = np.zeros(shape = matSize*3)
            #Matrix i*i, W^u
        self.corrMartix = np.zeros(shape = (len(self.fileList), len(self.fileList)))
        self.corrNetMartix = np.zeros(shape = (len(self.fileList), len(self.fileList)))
            #Matrix U0
        self.timeWeekdayMatrix = np.zeros(shape = (len(self.fileList),24))
        self.timeWeekendMatrix = np.zeros(shape = (len(self.fileList),24))
            #Matrix parameter
        self.X = np.zeros(shape = (len(self.fileList),matSize*3))
        self.U = np.random.rand(len(self.fileList),24)
        self.V = np.random.rand(3*matSize,24)
        self.Du = np.zeros(shape = (len(self.fileList), len(self.fileList)))
        self.Dv = np.zeros(shape = (matSize*3,matSize*3))
        self.Gu = np.zeros(shape = (len(self.fileList), len(self.fileList)))
        #Init wordObj, totalWordObj, wordVec
            #Init totalWordObj
        self.totalWordObj = WordPre(self.totalFileName)
        self.totalWordObj.openAdJiebaF()
            #Init wordVec
        self.wordVec = Word2(self.totalFileName)
        self.wordVec.openModel()
            #Init wordObj
        self.fileListId = 0
        self.wordObj = WordPre(self.fileList[self.fileListId])
        pass

    def test(self):
        #self.wordObj.getTotalWordFromExcel(1)
        for i in range(len(self.testList)):
            self.wordObj = WordPre(self.testList[i])
            self.wordObj.getTotalWordFromExcel(4)
            self.fileListId = i
            self.wordObj.saveTotalWord()
            self.wordObj.getAdJiebaF()
            self.wordObj.saveAdJiebaF()
        #self.wordObj.saveJiebaWord()
        #self.wordObj.openAdJiebaF()
        #self.wordVec.word2Vector()
        #self.wordVec.saveModel()
        #self.wordVec.openModel()
        #self.wordObj = WordPre("TotalCom")
        #self.wordObj.getTotalWordFromExcel(1,1)
        #self.wordObj.saveTotalWord()
        #self.wordObj.getAdJiebaF()
        #self.wordObj.saveAdJiebaF()
        #self.wordObj.openTotalWord()
        #self.wordObj.getAdJiebaF()
        #self.wordObj.saveJiebaWord()
        #self.wordObj.saveAdJiebaF()
        #self.wordObj.openJiebaWord()
        #self.wordObj.openAdJiebaF()
        #self.wordVec = Word2("TotalCom")
        #self.wordVec.word2Vector()
        #self.wordVec.saveModel()
        pass
    
    #from scipy.spatial.distance import pdist
    def getTotalWordList(self):
        '''
        Get the "totalWordList" from top k words in n. adj. and v.
        Notice: totalWordObj.nWordSorted
                totalWordObj.aWordSorted
                totalWordObj.vWordSorted       are needed
        '''
        #Add the top k noun words to the totalWordList
        for i in range(self.k):
            self.totalWordList.append(self.totalWordObj.nWordSorted[i][0])
        #Add the top k adj words to the totalWordList
        for i in range(self.k):
            self.totalWordList.append(self.totalWordObj.aWordSorted[i][0])
        #Add the top k verb words to the totalWordList
        for i in range(self.k):
            self.totalWordList.append(self.totalWordObj.vWordSorted[i][0])
        pass

    def vectorCosine(self):
        '''
        Compute the vector cosine of totalWordList
        Notice: totalWordObj.nWordSorted
                totalWordObj.aWordSorted
                totalWordObj.vWordSorted
                wordVec.word2VecModel       are needed
        '''
        #Get the totalWordList first
        self.getTotalWordList()
        #Compute each cell of the matrix
        for y in range(self.k*3):
            for x in range(self.k*3):
                #model[u"好"] can return the vector directly
                #Compute the vector cosine
                self.wordMatrix[y][x] = self.wordVec.word2VecModel.wv.similarity(self.totalWordList[y],self.totalWordList[x])
        pass
        
    def saveWordMatrix(self, saveId = -1):
        if saveId < 0:
            saveId = self.fileListId
        tempfileName = self.fileList[saveId]
        np.savetxt(tempfileName+"wordMatrix.txt",self.wordMatrix)
        pass

    def openWordMatrix(self, saveId = -1):
        if saveId < 0:
            saveId = self.fileListId
        tempfileName = self.fileList[saveId]
        self.wordNetMatrix = np.loadtxt(tempfileName+"wordMatrix.txt")
        pass    

    def wordNet(self,rm = -1):
        '''
        Change top m words in 3*k words to 1, others to 0
        Notice: totalWordObj.nWordSorted
                totalWordObj.aWordSorted
                totalWordObj.vWordSorted
                wordVec.word2VecModel       are needed
        '''
        #Judge if you give a "rm" number.
        #When you define a function, the formal paramter is static. 
        #If you set a default to it, it would init at first and wouldn't change.
        if rm < 0:
            rm = self.m
        #Get the wordMatrix
        self.vectorCosine()
        tempMat = self.wordMatrix
        #Find every Row
        for i in range(tempMat.shape[0]):
            #Find top rm words
            for j in range(rm):
                num = -1.0
                numid = 0
                #Try to find the largest cell in one Row by a loop
                for ii in range(tempMat.shape[1]):
                    if tempMat[i][ii] > num:
                        num = tempMat[i][ii]
                        numid = ii
                #Avoid find the same cell twice
                tempMat[i][numid] = 0
                #Set the wordNetMatrix 1
                self.wordNetMatrix[i][numid] = 1
        #Get Matrix Dv
        self.Dv = np.eye(3*self.k)*rm
        print("WordNet computed successfully")
        pass

    def saveWordNetMatrix(self, saveId = -1):
        if saveId < 0:
            saveId = self.fileListId
        tempfileName = self.fileList[saveId]
        np.savetxt(tempfileName+"wordNetMatrix.txt",self.wordNetMatrix,fmt="%d")
        #https://cloud.tencent.com/developer/article/1081196
        pass
    
    def openWordNetMatrix(self, saveId = -1):
        if saveId < 0:
            saveId = self.fileListId
        tempfileName = self.fileList[saveId]
        self.wordNetMatrix = np.loadtxt(tempfileName+"wordNetMatrix.txt",dtype=int)
        pass
        
    def getAllSceneWordMatrix(self):
        '''
        count 3*k words in each scenery
        Notice: wordObj1.totalWord
                wordObj2.totalWord
                ...
                totalWordList               are needed
        '''
        cs = 0
        for sceneName in self.fileList:
            tempWordObj = WordPre(sceneName)
            tempWordObj.openTotalWord()
            tempM = np.zeros(shape = self.k*3)
            i = 0
            for keyWord in self.totalWordList:
                tempM[i] = len(re.findall(keyWord,tempWordObj.totalWord))
                i = i + 1
            if cs == 0:
                self.sceneWordMatrix = tempM
                cs = 1
            else:
                self.sceneWordMatrix = np.vstack((self.sceneWordMatrix,tempM))
        print("Get the count of all 3*k feature words of all scenery")
        pass

    def saveAllSceneWordMatrix(self):
        np.savetxt(self.totalFileName+"sceneWordMatrix.txt",self.sceneWordMatrix,fmt="%d")
        pass

    def openAllSceneWordMatrix(self):
        self.sceneWordMatrix = np.loadtxt(self.totalFileName+"sceneWordMatrix.txt",dtype=int)
        pass

    def getTFDict(self,n = 300):
        '''
        Get TF Dict of current fileListId
        params                 function                      range                    default
          n       Top n TF. The range of the TF words       1 - inf                     300
        Notice: wordObj.nWordSorted     
                wordObj.aWordSorted
                wordObj.vWordSorted
                totalWordObj.nWordSorted
                totalWordObj.aWordSorted
                totalWordObj.vWordSorted
        '''
        self.wordObj.openAdJiebaF()
        self.totalWordObj.openAdJiebaF()
        #Clear the TF Dict
        self.aTFDict.clear()
        self.vTFDict.clear()
        self.nTFDict.clear()
        #Count of total adj/n/v word in each word
        aCount = 0
        nCount = 0
        vCount = 0
        for i in self.wordObj.nWordSorted:
            nCount = nCount + i[1]
        for i in self.wordObj.vWordSorted:
            vCount = vCount + i[1]
        for i in self.wordObj.aWordSorted:
            aCount = aCount + i[1]
        #Get top n to adj/n/v WordDict
        for i in range(n):
            self.nTFDict[self.wordObj.nWordSorted[i][0]] = self.wordObj.nWordSorted[i][1] / nCount
            self.vTFDict[self.wordObj.vWordSorted[i][0]] = self.wordObj.vWordSorted[i][1] / vCount
            self.aTFDict[self.wordObj.aWordSorted[i][0]] = self.wordObj.aWordSorted[i][1] / aCount
        pass

    def getIDFDict(self,n = 300):
        '''
        Get IDF Dict of current fileListId
        params                 function                      range                    default
          n       Top n IDF. The range of the IDF words     1 - inf                     300
        Notice: wordObj1.totalWord 
                wordObj2.totalWord
                ...
                wordObj.nWordSorted 
                wordObj.vWordSorted
                wordObj.aWordSorted         are needed
        '''
        self.wordObj.openAdJiebaF()
        #Combine all fileList totalWord to a list
        tList = []
        for i in range(len(self.fileList)):
            tObj = WordPre(self.fileList[i])
            tObj.openTotalWord()
            tList.append(tObj.totalWord)
        #Clear the Dict and Temp Dict
        tempNIDFDict = {}
        tempVIDFDict = {}
        tempAIDFDict = {}
        self.nIDFDict.clear()
        self.vIDFDict.clear()
        self.aIDFDict.clear()
        #Count if the top n word appear in every file
        for i in range(n):
            for j in range(len(tList)):
                if self.wordObj.nWordSorted[i][0] in tList[j]:
                    tempNIDFDict[self.wordObj.nWordSorted[i][0]] = tempNIDFDict.get(self.wordObj.nWordSorted[i][0],0) + 1
                if self.wordObj.vWordSorted[i][0] in tList[j]:
                    tempVIDFDict[self.wordObj.vWordSorted[i][0]] = tempVIDFDict.get(self.wordObj.vWordSorted[i][0],0) + 1
                if self.wordObj.aWordSorted[i][0] in tList[j]:
                    tempAIDFDict[self.wordObj.aWordSorted[i][0]] = tempAIDFDict.get(self.wordObj.aWordSorted[i][0],0) + 1
        #Compute accurate IDF
        for i in tempNIDFDict:
            self.nIDFDict[i] = math.log(len(tList) / tempNIDFDict.get(i,len(tList)),10)
        for i in tempVIDFDict: 
            self.vIDFDict[i] = math.log(len(tList) / tempVIDFDict.get(i,len(tList)),10) 
        for i in tempAIDFDict:
            self.aIDFDict[i] = math.log(len(tList) / tempAIDFDict.get(i,len(tList)),10) 
        pass

    def getAllTopTFIDFList(self,n = 300):
        '''
        Get all TF-IDF of fileList
        params                 function                      range                    default
          n      The range of search, bigger is better      1 - inf                     300
        Notice: wordObj1.totalWord
                wordObj1.nWordSorted
                wordObj1.vWordSorted
                wordObj1.aWordSorted
                ...
                totalWordObj.nWordSorted
                totalWordObj.vWordSorted
                totalWOrdObj.aWordSorted        are needed
        '''
        for j in range(len(self.fileList)):
            #Refresh the wordObj
            self.fileListId = j
            self.wordObj = WordPre(self.fileList[self.fileListId])
            self.wordObj.openAdJiebaF()
            self.wordObj.openTotalWord()
            #Get TF and IDF
            safeN = min(len(self.wordObj.nWordSorted),len(self.wordObj.vWordSorted),len(self.wordObj.aWordSorted))
            if n > safeN:
                n = safeN
            self.getTFDict(n)
            self.getIDFDict(n)
            tempn = {}
            tempa = {}
            tempv = {}
            for i in self.nIDFDict:
                tempn[i] = self.nIDFDict[i] * self.nTFDict[i]
            for i in self.aIDFDict:
                tempa[i] = self.aIDFDict[i] * self.aTFDict[i]
            for i in self.vIDFDict:
                tempv[i] = self.vIDFDict[i] * self.vTFDict[i]
            #Sort and Find top list
            tempnList = sorted(tempn.items(), key = lambda x:x[1], reverse = True)
            tempaList = sorted(tempa.items(), key = lambda x:x[1], reverse = True)
            tempvList = sorted(tempv.items(), key = lambda x:x[1], reverse = True)
            self.nTFIDFList.append(tempnList)
            self.aTFIDFList.append(tempaList)
            self.vTFIDFList.append(tempvList)
            print("Finish Computing TF-IDF ",j+1,"/",len(self.fileList)-1)
        pass
        
    def getCorrelation(self, a, b, charactNum=5, nRate=0.333333, vRate=0.333333, aRate=0.333333):
        '''
        Return the correlation of fileList[a] and fileList[b]
        params                 function                      range                          default
          a              one scenery you choose            0 - len(fileList)                   --
          b            another scenery you choose          0 - len(fileList)                   --
        charactNum      number of feature words     1 - min(All n/a/vTFIDFList[all cell])      5
         nRate              Rate of noun                   0 - inf                          0.333333
         vRate              Rate of Verb                   0 - inf                          0.333333
         aRate              Rate of Adj                    0 - inf                          0.333333
        Notice: nTFIDFList
                aTFIDFList
                vTFIDFList      are needed
        '''
        cm = np.zeros(shape = (charactNum,charactNum))
        tempSumN = 0
        tempSumV = 0
        tempSumA = 0
        #Generate word index List of chractNum. Judge if the words in the List are in the Word2VecModel
        nAList = []
        vAList = []
        aAList = []
        nAIndex = 0
        vAIndex = 0
        aAIndex = 0
        nBList = []
        vBList = []
        aBList = []
        nBIndex = 0
        vBIndex = 0
        aBIndex = 0
        for i in range(charactNum):
            while True:
                if self.nTFIDFList[a][nAIndex][0] in self.wordVec.word2VecModel:
                    nAList.append(nAIndex)
                    nAIndex = nAIndex + 1
                    break
                else:
                    nAIndex = nAIndex + 1
            while True:
                if self.vTFIDFList[a][vAIndex][0] in self.wordVec.word2VecModel:
                    vAList.append(vAIndex)
                    vAIndex = vAIndex + 1
                    break
                else:
                    vAIndex = vAIndex + 1
            while True:
                if self.aTFIDFList[a][aAIndex][0] in self.wordVec.word2VecModel:
                    aAList.append(aAIndex)
                    aAIndex = aAIndex + 1
                    break
                else:
                    aAIndex = aAIndex + 1
            while True:
                if self.nTFIDFList[b][nBIndex][0] in self.wordVec.word2VecModel:
                    nBList.append(nBIndex)
                    nBIndex = nBIndex + 1
                    break
                else:
                    nBIndex = nBIndex + 1
            while True:
                if self.vTFIDFList[b][vBIndex][0] in self.wordVec.word2VecModel:
                    vBList.append(vBIndex)
                    vBIndex = vBIndex + 1
                    break
                else:
                    vBIndex = vBIndex + 1
            while True:
                if self.aTFIDFList[b][aBIndex][0] in self.wordVec.word2VecModel:
                    aBList.append(aBIndex)
                    aBIndex = aBIndex + 1
                    break
                else:
                    aBIndex = aBIndex + 1
        #compute n.
        for y in range(charactNum):
            for x in range(charactNum):
                cm[y][x] = self.wordVec.word2VecModel.wv.similarity(self.nTFIDFList[a][nAList[y]][0],self.nTFIDFList[b][nBList[x]][0])
        colmax = cm.argmax(axis = 0)
        rowmax = cm.argmax(axis = 1)
        for i in range(charactNum):
            tempSumN = tempSumN + cm[i][colmax[i]] + cm[rowmax[i]][i]
        #Compute v.
        for y in range(charactNum):
            for x in range(charactNum):
                cm[y][x] = self.wordVec.word2VecModel.wv.similarity(self.vTFIDFList[a][vAList[y]][0],self.vTFIDFList[b][vBList[x]][0])
        colmax = cm.argmax(axis = 0)
        rowmax = cm.argmax(axis = 1)
        for i in range(charactNum):
            tempSumV = tempSumV + cm[i][colmax[i]] + cm[rowmax[i]][i]
        #Compute a.
        for y in range(charactNum):
            for x in range(charactNum):
                cm[y][x] = self.wordVec.word2VecModel.wv.similarity(self.aTFIDFList[a][aAList[y]][0],self.aTFIDFList[b][aBList[x]][0])
        colmax = cm.argmax(axis = 0)
        rowmax = cm.argmax(axis = 1)
        for i in range(charactNum):
            tempSumA = tempSumA + cm[i][colmax[i]] + cm[rowmax[i]][i]
        #Compute total correlateion
        return (tempSumN*nRate + tempSumV*vRate + tempSumA*aRate)/(2 * charactNum) 
    
    def getCorrMatrix(self, featureNum=5, nRates=0.333333, vRates=0.333333, aRates=0.333333):
        '''
        Get the whole Correlation Matrix
        params                 function                      range                          default
        featureNum      number of feature words     1 - min(All n/a/vTFIDFList[all cell])      5
         nRates              Rate of noun                   0 - inf                          0.333333
         vRates              Rate of Verb                   0 - inf                          0.333333
         aRates              Rate of Adj                    0 - inf                          0.333333
        Notice: nTFIDFList
                aTFIDFList
                vTFIDFList      are needed
        '''
        for i in range(len(self.fileList)):
            for j in range(len(self.fileList)):
                self.corrMartix[i][j] = self.getCorrelation(a = i, b = j, charactNum=featureNum, nRate=nRates, vRate=vRates, aRate=aRates)
            print("Finish Compute Matrix Line: ",i,"/",len(self.fileList)-1)
        #print(self.corrMartix)
    
    def getCorrNetMatrix(self, ru = -1 , featureNum=5, nRate=0.333333, vRate=0.333333, aRate=0.333333):
        '''
        Get the whole Correlation 0-1 Matrix and Du Matrix. Top u is 1
        params                 function                      range                          default
        featureNum      number of feature words     1 - min(All n/a/vTFIDFList[all cell])      5
         nRate              Rate of noun                   0 - inf                          0.333333
         vRate              Rate of Verb                   0 - inf                          0.333333
         aRate              Rate of Adj                    0 - inf                          0.333333
        Notice: nTFIDFList
                aTFIDFList
                vTFIDFList      are needed
        '''
        #add one, because the biggest must be itself
        if ru < 0:
            ru = self.u
        ru = ru + 1
        #Get a temp Matrix
        self.getCorrMatrix(featureNum,nRate,vRate,aRate)
        tempMat = self.corrMartix
        #Find every Row
        for i in range(tempMat.shape[0]):
            #Find top rm words
            for j in range(ru):
                num = -1.0
                numid = 0
                #Try to find the largest cell in one Row by a loop
                for ii in range(tempMat.shape[1]):
                    if tempMat[i][ii] > num:
                        num = tempMat[i][ii]
                        numid = ii
                #Avoid find the same cell twice
                tempMat[i][numid] = 0
                #Set the wordNetMatrix 1
                self.corrNetMartix[i][numid] = 1
        #Compute Du
        self.Du = np.eye(len(self.fileList))*ru
        print("CorrNetMatrix computed successfully")
        pass

    def openTimeMatrix(self , *missId):
        '''
        Open Weibo Time matrix and prepare Gu Matrix
        missId:  fileListId of miss weibo Time
        '''
        self.timeWeekdayMatrix = np.loadtxt(open(self.totalFileName+"timeWeekdayMatrix.csv","rb"),delimiter=",",skiprows=0)
        self.timeWeekendMatrix = np.loadtxt(open(self.totalFileName+"timeWeekendMatrix.csv","rb"),delimiter=",",skiprows=0)
        self.Gu = np.eye(len(self.fileList))
        for i in missId:
            self.Gu[i][i] = 0
        pass

    def getAllVariable(self):
        '''
        Get All variable you need to compute
        You should change m, u and error WeiboTime ID
        '''
        #Get the W^v, input m
        self.wordNet(60)
        #Get the X, need totalWordList
        self.getAllSceneWordMatrix()
        #Get the W^u, input u
        self.getAllTopTFIDFList(300)
        self.getCorrNetMatrix(2)
        #Get timeMatrix
        self.openTimeMatrix(8)
        #Prepare all variable
        self.X = self.sceneWordMatrix
        self.U0a = self.timeWeekdayMatrix
        self.U0b = self.timeWeekendMatrix
        self.Wu = self.corrNetMartix
        self.Wv = self.wordNetMatrix
        pass

    def saveAllVariable(self):
        np.savetxt(self.totalFileName+"X.txt",self.X,fmt="%d")
        np.savetxt(self.totalFileName+"U.txt",self.U)
        np.savetxt(self.totalFileName+"V.txt",self.V)
        np.savetxt(self.totalFileName+"Du.txt",self.Du,fmt="%d")
        np.savetxt(self.totalFileName+"Dv.txt",self.Dv,fmt="%d")
        np.savetxt(self.totalFileName+"U0a.txt",self.U0a,fmt="%d")
        np.savetxt(self.totalFileName+"U0b.txt",self.U0b,fmt="%d")
        np.savetxt(self.totalFileName+"Wu.txt",self.Wu,fmt="%d")
        np.savetxt(self.totalFileName+"Wv.txt",self.Wv,fmt="%d")
        np.savetxt(self.totalFileName+"Gu.txt",self.Gu,fmt="%d")
        pass
    
    def openAllVariable(self):
        self.getTotalWordList()
        self.X = np.loadtxt(self.totalFileName+"X.txt",dtype=int)
        self.U = np.loadtxt(self.totalFileName+"U.txt")
        self.V = np.loadtxt(self.totalFileName+"V.txt")
        self.Du = np.loadtxt(self.totalFileName+"Du.txt",dtype=int)
        self.Dv = np.loadtxt(self.totalFileName+"Dv.txt",dtype=int)
        self.U0a = np.loadtxt(self.totalFileName+"U0a.txt",dtype=int)
        self.U0b = np.loadtxt(self.totalFileName+"U0b.txt",dtype=int)
        self.Wu = np.loadtxt(self.totalFileName+"Wu.txt",dtype=int)
        self.Wv = np.loadtxt(self.totalFileName+"Wv.txt",dtype=int)
        self.Gu = np.loadtxt(self.totalFileName+"Gu.txt",dtype=int)
        pass

    def ComputeOnce(self,typeId = 0):
        '''
        Compute Once.
        typeId = 0 --> weekday
        typeId = 1 --> weekend
        '''
        if typeId == 0:
            U0 = self.U0a
        else:
            U0 = self.U0b
        a = np.matmul(self.X,self.V) + np.matmul(self.Gu,U0) + np.matmul(self.Wu,self.U)
        b = np.matmul(np.matmul(self.U,self.V.T),self.V) + np.matmul(self.Gu,self.U) + np.matmul(self.Du,self.U) + self.U
        self.U = self.U * np.power(a/b,0.5)
        a = np.matmul(self.X.T,self.U) + np.matmul(self.Wv,self.V)
        b = np.matmul(np.matmul(self.V,self.U.T),self.U) + np.matmul(self.Dv,self.V) + self.V
        self.V = self.V * np.power(a/b,0.5)
        pass

    def ComputeLoop(self, typeId = 0,loopTimes = 200):
        '''
        Compute few times
        loopTimes:  Times loop
        typeId = 0 --> weekday
        typeId = 1 --> weekend
        '''
        for i in range(loopTimes):
            self.ComputeOnce(typeId)
            print("This is ",i+1,"/",loopTimes)
        pass
        np.savetxt(self.totalFileName+str(typeId)+"U_Key.csv",self.U,delimiter=',',fmt='%0.2f')
        np.savetxt(self.totalFileName+str(typeId)+"V_Key.csv",self.V,delimiter=',',fmt='%0.2f')

    def testPart(self):
        '''
        Notice: testWordObj1.totalWord
                testWordObj2.totalWord
                ...
                totalWOrdList               are needed
        '''
        #Get Xt Matrix
        self.getTotalWordList()
        cs = 0
        for sceneName in self.testList:
            tempWordObj = WordPre(sceneName)
            tempWordObj.openTotalWord()
            tempM = np.zeros(shape = self.k*3)
            i = 0
            for keyWord in self.totalWordList:
                tempM[i] = len(re.findall(keyWord,tempWordObj.totalWord))
                i = i + 1
            if cs == 0:
                self.Xt = tempM
                cs = 1
            else:
                self.Xt = np.vstack((self.Xt,tempM))
        print("Get the count of all 3*k feature words of test scenery")
        #Get U and V for weekday
        self.openAllVariable()
        self.ComputeLoop(0)
        #Get Test Result of weekday
        testWeekday = np.matmul(self.Xt,self.V)
        np.savetxt("TestWeekday.csv",testWeekday,delimiter=',',fmt='%0.2f')
        print("Finish Test weekday")
        #Get U and V for weekend
        self.ComputeLoop(1)
        #Get Test Result of weekend
        testWeekend = np.matmul(self.Xt,self.V)
        np.savetxt("TestWeekend.csv",testWeekend,delimiter=',',fmt='%0.2f')
        print("Finish Test Weekend")
        pass

def main():
    #a = WordPre("testDataA")
    #a.getTotalWordFromExcel()
    #a.openTotalWord()
    #a.getAdJiebaF()
    #a.saveAdJiebaF()
    
    #b = Word2("testDataA")
    #b.word2Vector()
    #b.saveModel()
    #=========================================
    c = Compute(100)
    #c.getAllVariable()
    #c.saveAllVariable()
    #c.openAllVariable()
    #c.ComputeLoop()
    c.testPart()
    #==========================================
    #c.getTFDict(10)
    #c.getIDFDict(10)
    #c.test()
    #c.getAllTopTFIDFList(300)
    #c.getCorrMatrix()
    #c.wordVec.word2Vector()
    #c.wordVec.saveModel()
    
    #c.vectorCosine()
    #c.wordNet(60)
    #c.saveWordMatrix()
    #c.getTotalWordList()
    #c.getAllSceneWordMatrix()
    #d = GetWeibo()
    #d.getWeiboDate()

    pass
if __name__ == "__main__":
    main()