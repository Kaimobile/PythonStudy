#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File    :   hs300peA.py
@Time    :   2019-01-14
@Author  :   MetalOxide
@Version :   1.1
@License :   (C) Copyright 2012-2019, Kaimobile
@Contact :   kyan@tju.edu.cn
@Desc    :   None
"""
import numpy as np 
import xlrd
import time
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 

class DataPre(object):
    """Prepare data for next strategy

    Put the fileName in the object, and you can get the 
    Data you need by visiting the attributes.

    Attributes:
    fileName: the File Name of the Data file
    dateList: The List of Date
    peList: The List of P/E
    priceList: The List of HS300 Index Price
    oldPriceList: The List of Old SZ000001 Index
    num: Count of data
    """
    
    def __init__(self,fileName: str):
        """
        Initialize the fileName
        """
        self.fileName = fileName
        self.dateList = []
        self.peList = []
        self.priceList = []
        self.oldPriceList = []
        self.num = 0
        pass
    
    def getExcelData(self, sheetType="xls", sheetIndex=0):
        """
        Open the Excel with fileName

        Args:
            sheetType: The excel type. You can give "xlsx" or "xls".
                The default of the parameter is "xls".
            sheetIndex: The index of the sheet in the Excel file.
                The default is 0.
        """
        shx = xlrd.open_workbook(self.fileName+"."+sheetType)
        sh = shx.sheet_by_index(sheetIndex)
        rowNum = sh.nrows
        for i in range(rowNum):
            self.dateList.append(str(sh.cell_value(i,0)))
            self.peList.append(float(sh.cell_value(i,1)))
            self.priceList.append(float(sh.cell_value(i,2)))
        self.num = min(len(self.dateList), len(self.peList), 
            len(self.priceList))
        
        sh = shx.sheet_by_index(sheetIndex+1)
        rowNum = sh.nrows
        for i in range(rowNum):
            self.oldPriceList.append(float(sh.cell_value(i,1)))
        pass

class StrategyA(object):
    """StrategyA

    A Strategy based on exponent and 2-8 rule

    Attributes:
        dateList: List of processed date
        peList: Ascend Order List of P/E
        priceList: List of price
        cvList: List of coefficient of variation
        oriList: List of the Orientation of Stock, each
            number means one period of CV. -1 means fall,
            1 means raise.
        assetList: List of total Asset.
        moneyList: List of total Currency.
        stockList: List of total Stock.
        currencyList: List of non-risk money.
        num: Number of the used data

        sumPe: the Sum of total P/E
        avgPe: The Average of total P/E
        hopePe: The lowest P/E you will buy all stocks
        edgePe: the P/E Number at 'ratio' position
        cPrice: current Stock Price
        cPe: current P/E

        edgeCV: The CV Number at 'ratio' position
        cCV: The current CV
        cOri: The current Orientation.

        ratioPE: The threshold of P/E,
            default: 0.8
        ratioCV: The threshold of CV,
            default: 0.95
        window: The number of calculating CV,
            default: 20
        cvStep: The step of buy or sell total asset.
            default: 10
        totalStock: The Stock num you have bought,
            default: 10
        totalMoney: The total money now,
            default: 10000
        eachMoney: how much you want to buy each week,
            default: 10

        expA: the factor of the eachMoney in buy module, 
            default edgePe = 20P/E
        expB: the factor of the totalMoney in buy module,
            default avgPe = 15P/E

        maxAsset: The maximum Asset appears
        maxRatio: Max retracement
        sRatio: Sharpe Ratio
    """

    def __init__(self, tMoney=10000, tStock=10, eMoney=10, ratioPE=0.8, 
                ratioCV=0.95, window=20, cvStep=10):
        self.dateList = []
        self.peList = []
        self.priceList = []
        self.cvList = []
        self.oriList = []
        self.assetList = []
        self.moneyList = []
        self.stockList = []
        self.currencyList = []
        self.num = 0

        self.sumPe = 0
        self.avgPe = 15.0
        self.hopePe = 10.0
        self.edgePe = 20.0
        self.cPrice = 0
        self.cPe = 0

        self.edgeCV = 1
        self.cCV = 0
        self.cOri = 1
        
        self.ratioPE = ratioPE
        self.ratioCV = ratioCV
        self.window = window
        self.cvStep = cvStep
        self.totalMoney = tMoney
        self.totalStock = tStock
        self.eachMoney = eMoney
        self.expA = math.log(2) / (self.edgePe - self.avgPe)
        self.expB = math.log(2) / (self.avgPe - self.hopePe)
        self.expC = math.log(2) / (self.edgePe - self.hopePe)
        
        self.maxAsset = 0.000001
        self.maxRatio = 0.0
        self.sRatio = 0.0
        pass

    def __del__(self):
        self.dateList = []
        self.peList = []
        self.priceList = []
        self.cvList = []
        self.oriList = []
        pass

    def fList(self, point, types):
        """Find the value in the list.

        Find the num of the position you give and return.
        
        Args:
            point: The position you want
            types: The num type you need.
                types: 0 --> P/E
                types: 1 --> CV
        
        Returns:
            The value at the position you give.
        """
        if types == 0:
            return self.peList[int(point * len(self.peList))]
        else:
            return self.cvList[int(point * len(self.cvList))]
        pass

    def refreshExp(self):
        """

        Change the exponent parameter.

        """
        if (self.edgePe - self.avgPe) > 0:
            self.expA = math.log(2) / (self.edgePe - self.avgPe)
        if (self.avgPe - self.hopePe) > 0:
            self.expB = math.log(2) / (self.avgPe - self.hopePe)
        if (self.edgePe - self.hopePe) > 0:
            self.expC = math.log(2) / (self.edgePe - self.hopePe)    
        pass

    def refreshCV(self):
        """Refresh the Coefficient of Variation

        CV = Standard Division / Mean

        """
        if self.num > self.window:
            i1 = self.num - self.window
            i2 = self.num
            stdNum = np.std(self.priceList[i1:i2])
            avg = np.mean(self.priceList[i1:i2])
            self.cCV = stdNum / avg
            self.cvList.append(self.cCV)
            self.cvList.sort()
            self.edgeCV = self.fList(self.ratioCV,1)
            self.refreshOri(i1, i2)
        pass

    def loadOldCV(self, priceList):
        """Load Old CV

        """
        for i in range(len(priceList)):
            if i > self.window:
                i1 = i - self.window
                i2 = i
                std = np.std(priceList[i1:i2])
                avg = np.mean(priceList[i1:i2])
                self.cvList.append(std/avg)
        self.cvList.sort()
        #plt.plot(self.cvList)
        #plt.show()
        pass

    def refreshOri(self, L, R):
        """Refresh the Orientation of Stock

        Each value represent one period of CV.
        -1 means fall and 1 means raise.

        Args:
            L: Small side of the range.
            R: Large side of the range.
        """
        numL = self.priceList[L-1]
        numR = self.priceList[R-1]
        if numR > numL*1.05:
            self.cOri = 1
        elif numR*0.95 < numL:
            self.cOri = -1
        else:
            self.cOri = 0
        self.oriList.append(self.cOri)
        pass

    def addOneDay(self, date, pe, price):
        """Add One day.

        Add a new Market Day and change attributes.
        
        Attention: This function doesn't add the 
            'eachMoney' to 'totalMoney'!

        Args:
            date: date of the day, a string
            pe: P/E
            price: HS300 Index

        """
        self.dateList.append(date)
        self.priceList.append(price)
        self.num = self.num + 1
        self.peList.append(pe)
        self.peList.sort()

        self.cPrice = price
        self.cPe = pe
        #if self.hopePe > pe:
        #    self.hopePe = pe
        self.edgePe = self.fList(self.ratioPE,0)
        self.sumPe = self.sumPe + pe
        self.avgPe = self.sumPe / self.num
        #self.avgPe = self.fPE(0.5)
        self.refreshExp()
        self.refreshCV()

        tasset = self.totalStock * price + self.totalMoney
        if tasset > self.maxAsset:
            self.maxAsset = tasset
        else:
            tRatio = 1 - tasset / self.maxAsset
            if tRatio > self.maxRatio:
                self.maxRatio = tRatio
        pass

    def buyStockPeriodExp(self):
        """Buy stock period Exponent Plan

        Buy stock period with a exponent model.
        The model begins at P/E=avgPe(default: 15.0) and end at P/E=edgePe.
        When P/E is less than avgPe(default: 15.0), you spend all
        "eachMoney". When P/E reachs the edgePe, stop buying.
        The surplus money is saved to "totalMoney".

        """
        # 'ratio' is the percentage you buy each time
        if self.cPe > self.edgePe:
            self.totalMoney = self.totalMoney + self.eachMoney
            return
        elif self.cPe <= self.avgPe:
            ratio = 1.0
        else:
            ratio = 2 - pow(math.e, (self.cPe - self.avgPe) * self.expA)
        buy = ratio * self.eachMoney
        save = self.eachMoney - buy
        self.totalMoney = self.totalMoney + save
        self.totalStock = self.totalStock + (buy / self.cPrice)
        pass

    def buyStockPeriodExp2(self):
        """Buy stock period Exponent Plan

        Buy stock period with a exponent model.
        The model begins at P/E=avgPe(default: 15.0) and end at P/E=edgePe.
        When P/E is less than avgPe(default: 15.0), you spend all
        "eachMoney". When P/E reachs the edgePe, stop buying.
        The surplus money is saved to "totalMoney".

        """
        # 'ratio' is the percentage you buy each time
        if self.cPe > self.edgePe:
            self.totalMoney = self.totalMoney + self.eachMoney
            return
        elif self.cPe <= self.hopePe:
            ratio = 1.0
        else:
            ratio = 2 - pow(math.e, (self.cPe - self.hopePe) * self.expC)
        tbuy = ratio * self.eachMoney * 2
        if self.eachMoney >= tbuy:
            buy = tbuy
            save = self.eachMoney - buy
        else:
            if (self.totalMoney + self.eachMoney) >= tbuy:
                buy = tbuy
                self.totalMoney = self.totalMoney - (buy - self.eachMoney)
            else:
                buy = self.totalMoney + self.eachMoney
                self.totalMoney = 0
            save = 0
        self.totalMoney = self.totalMoney + save
        self.totalStock = self.totalStock + (buy / self.cPrice)
        pass

    def buyStockPeriodFixed(self):
        """Buy stock period Fixed Plan.

        Spend all 'eachMoney' each period.

        """
        buyStock = self.eachMoney / self.cPrice
        self.totalStock = self.totalStock + buyStock
        pass

    def buyStockPeriodPoint2(self, point=0.5):
        """Buy stock period Below Exist Point Plan.

        Spend all 'eachMoney' when current P/E is below point.
        Spend None when P/E is above point.

        Args:
            point: The index of the highest P/E you can accept.
                default: 0.5.
        """
        if self.cPe > self.fList(point,0):
            self.totalMoney = self.totalMoney + self.eachMoney
        else:
            tbuy = self.eachMoney / point
            if self.totalMoney >= tbuy:
                buy = tbuy
                self.totalMoney = self.totalMoney - (tbuy - self.eachMoney)
            else:
                buy = self.totalMoney + self.eachMoney
                self.totalMoney = 0
            self.totalStock = self.totalStock + (buy / self.cPrice)
        pass
    
    def buyStockPeriodPoint(self, point=0.5):
        """Buy stock period Below Exist Point Plan.

        Spend all 'eachMoney' when current P/E is below point.
        Spend None when P/E is above point.

        Args:
            point: The index of the highest P/E you can accept.
                default: 0.5.
        """
        if self.cPe > self.fList(point,0):
            self.totalMoney = self.totalMoney + self.eachMoney
        else:
            self.buyStockPeriodFixed()
        pass

    def buyStockPeriodNone(self):
        """Buy no stock.

        Save 'eachMoney' to 'totalMoney'.

        """
        self.totalMoney = self.totalMoney + self.eachMoney
        pass

    def buyStockTotalExp(self):
        """Buy stock totally Exponent Plan.

        Buy stock by a exponent moedel.
        The model begins at P/E=hopePe(default: 10.0) and end at P/E=avgPe.
        When P/E reachs the hopePe(default: 10.0), you spend all
        "totalMoney". When P/E reachs the avgPe, stop buying.

        """
        # 'ratio' is the stock percentage you should keep 
        if self.cPe <= self.hopePe:
            ratio = 1.0
        else:
            ratio = 2 - pow(math.e, (self.cPe - self.hopePe) * self.expB)
        tSAsset = self.totalStock * self.cPrice
        tMAsset = self.totalMoney
        tAsset = tSAsset + tMAsset
        if tAsset * ratio > tSAsset:
            buy = tAsset * ratio - tSAsset
            self.totalMoney = self.totalMoney - buy
            buyStock = buy / self.cPrice
            self.totalStock = self.totalStock + buyStock
        pass
        
    def buyStockTotalCV(self):
        """Buy total stock with CV Plan

        Buy stocks when HS300 is raising quickly
        """
        if self.cCV > self.edgeCV and self.cOri > 0:
            buy = self.totalMoney / self.cvStep
            buyStock = buy / self.cPrice
            self.totalMoney = self.totalMoney - buy
            self.totalStock = self.totalStock + buyStock
        pass

    def sellStockCV(self):
        """Sell stock with CV Plan.

        Sell stocks when HS300 is falling quickly
        """
        if self.cCV > self.edgeCV and self.cOri < 0:
            sellStock = self.totalStock / self.cvStep
            sell = sellStock * self.cPrice
            self.totalMoney = self.totalMoney + sell
            self.totalStock = self.totalStock - sellStock
        pass

    def sellStockLog(self):
        """Sell stock with Log Plan.

        Sell stocks with a logarithm model.
        The model begins at P/E=edgePe and no end.
        The ratio is the percentage of recommend money.
        Ratio = ln(cPE / edgePE)
        """
        if self.cPe > self.edgePe:
            # ratio: Percentage of money
            tratio = math.log(self.cPe / self.edgePe)
            if tratio >= 1:
                ratio = 1.0
            else:
                ratio = tratio
        else:
            ratio = 0
        
        #Judge sell how much stocks
        ttAsset = self.totalStock * self.cPrice + self.totalMoney
        if (ttAsset * ratio) > self.totalMoney:
            sell = ttAsset * ratio - self.totalMoney
        else:
            sell = 0
        #print(sell)
        self.totalMoney = self.totalMoney + sell
        self.totalStock = self.totalStock - (sell / self.cPrice)
        pass

    def dailyMoney(self, ratio=0.209):
        """
        The currency interset everyday

        Args:
            ratio: The interest ratio of currency funds
        """
        dayInt = ratio / 365
        self.totalMoney = self.totalMoney * (1 + dayInt)
        self.moneyList.append(self.totalMoney)
        self.stockList.append(self.totalStock)
        self.assetList.append(self.totalMoney + self.totalStock * self.cPrice)
        if self.num == 1:
            self.currencyList.append(self.assetList[0])
        else:
            p = (self.currencyList[self.num-2] + self.eachMoney) * (1 + dayInt)
            self.currencyList.append(p)
        pass

    def strategyA(self, date, pe, price):
        """
        decide buy or sell how much

        Args:
            date: date of the day, a string
            pe: P/E
            price: HS300 Index
        """
        self.addOneDay(date, pe, price)
        #self.buyStockPeriodExp2()
        #self.buyStockPeriodNone()
        self.buyStockPeriodFixed()
        #self.buyStockPeriodPoint2(0.50)
        #self.buyStockTotalExp()
        #self.buyStockTotalCV()
        #self.sellStockLog()
        #self.sellStockCV()
        self.dailyMoney()
        pass
        
    def strategyB(self, date , pe, price):
        """
        strategyB, only save money
        """
        self.addOneDay(date, pe, price)
        self.totalMoney = self.eachMoney + self.totalMoney
        self.dailyMoney()
        pass
    
    def strategyC(self, date, pe, price):
        """
        only buy stocks
        """
        self.addOneDay(date, pe, price)
        self.buyStockPeriodFixed()
        #self.buyStockPeriodPoint2(0.2)
        #self.buyStockPeriodExp2()
        self.dailyMoney()

    def sharpeRatio(self):
        aList = []
        bList = []
        length = min(len(self.assetList), len(self.currencyList))
        for i in range(1,length):
            an = (self.assetList[i] - self.assetList[i-1]) / \
                self.assetList[i-1]
            aList.append(an)
            bn = (self.currencyList[i] - self.currencyList[i-1]) / \
                self.currencyList[i-1]
            bList.append(bn)
        #print(np.mean(aList), np.mean(bList), np.std(aList), np.std(bList))
        a = np.mean(aList) - np.mean(bList)
        b = np.std(aList) - np.std(bList)
        self.sRatio = (a / b) * np.sqrt(self.num)
        
        pass

def test():
    a = DataPre("HS300TTMPEData1")
    a.getExcelData()
    # w1 for window 5-50
    w1 = [5*(n+1) for n in range(10)]
    # w2 for window 20-35
    w2 = [20+n for n in range(20)]
    # r1 for ratioCV 0.80-0.99
    r1 = [0.80+0.02*n for n in range(10)]
    # r2 for ratioCV 0.90-0.98
    r2 = [0.90+0.005*n for n in range(20)]
    # c1 for cvStep 2-20
    c1 = [2+n for n in range(20)]
    # c2 for cvStep 1-5
    c2 = [1+0.5*n for n in range(10)]
    # r3 for ratioPE 0.70-0.99
    r3 = [0.1+0.05*n for n in range(18)]

    for j in r3:
        b = StrategyA(1, 0, ratioPE=j,ratioCV=0.80, window=10, cvStep=5)
        b.loadOldCV(a.oldPriceList)
        for i in range(a.num):
            b.strategyC(a.dateList[i], a.peList[i], a.priceList[i])
        b.sharpeRatio()
        print(j,b.totalStock * b.cPrice + b.totalMoney, b.maxRatio, b.sRatio)
    pass

def testPoint():
    a = DataPre("HS300TTMPEData1")
    a.getExcelData()
    # p1 for Point 10-70
    p1 = [0.10+0.05*n for n in range(19)]

    for j in p1:
        b = StrategyA(1, 0, ratioPE=0.80,ratioCV=0.80, window=10, cvStep=5)
        b.loadOldCV(a.oldPriceList)
        for i in range(a.num):
            b.addOneDay(a.dateList[i], a.peList[i], a.priceList[i])
            b.buyStockPeriodPoint2( j )
            #b.buyStockTotalCV()
            #b.sellStockCV()
            b.dailyMoney()
        b.sharpeRatio()
        print(j,b.totalStock * b.cPrice + b.totalMoney, b.maxRatio, b.sRatio)
    pass

def testPlt():
    a = DataPre("HS300TTMPEData1")
    a.getExcelData()
    # w1 for window 5-50
    w = np.arange(20,50,2)
    wLen = len(w)
    # r1 for ratioCV 0.80-0.99
    r = np.arange(0.2,0.6,0.03)
    rLen = len(r)
    z = np.zeros(shape=(wLen,rLen))

    for k in range(wLen):
        for j in range(rLen):
            b = StrategyA(10000, 10, ratioPE=0.8,ratioCV=r[j], window=w[k], cvStep=5)
            b.loadOldCV(a.oldPriceList)
            for i in range(a.num):
                b.strategyA(a.dateList[i], a.peList[i], a.priceList[i])
            b.sharpeRatio()
            z[k][j] = b.totalStock * b.cPrice + b.totalMoney
            print(z[k][j])
            print("Computing", j+1 , "of",rLen ,"|", k+1 ,"of" ,wLen)
    fig = plt.figure() 
    ax = Axes3D(fig) 
    r,w=np.meshgrid(r,w) 
    ax.plot_surface(r,w, z, rstride=1, cstride=1, cmap='rainbow') 
    ax.set_xlabel("Ratio CV")
    ax.set_ylabel("Window")
    ax.set_zlabel("Total Asset")
    ax.set_title("Sensitivity test of Ratio CV & Window")
    #ax.scatter3D(r,w, z, cmap='Blues') 
    plt.show()

    pass

def main():
    a = DataPre("HS300TTMPEData1")
    a.getExcelData()
    b = StrategyA(20000, 0 , ratioCV=0.50, window=30, cvStep=5, ratioPE=0.80)
    b.loadOldCV(a.oldPriceList)
    c = []
    d = []
    #test()
    #testPoint()
    #testPlt()
    #b.totalMoney=0;b.totalStock=0
    for i in range(a.num):
        #b.strategyA(a.dateList[i], a.peList[i], a.priceList[i])
        b.strategyB(a.dateList[i], a.peList[i], a.priceList[i])
        #b.strategyC(a.dateList[i], a.peList[i], a.priceList[i])
        #print(b.cPrice)
        #print(b.totalStock * b.cPrice + b.totalMoney)
        c.append(b.totalStock * b.cPrice + b.totalMoney)
        d.append(b.maxRatio)
    b.sharpeRatio()
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ax1.set_title("Control Model")
    plt.xlabel("Trading Day")
    plt.ylabel("Total Asset/CNY")
    ax1.plot(b.assetList)
    plt.show()
    print(b.totalStock * b.cPrice + b.totalMoney, b.maxRatio, b.sRatio)
    #print(c)
    pass
if __name__ == "__main__":
    main()
    pass