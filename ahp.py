'''
Dec 20， 2018
@author:        Kai Yan
@license:       GNU GPLv3
@contact:       kyan@tju.edu.cn
'''

import numpy as np
import math

class ahp:

    #The relationship Matrix
    matA = None
    #The number of items
    n = 0
    #R.I. parameter for check the availability. It depends on the shape of matrix
    ri = 0.9
    #The Weight matrix of items. shape = 1*n
    matW = None
    #Character Number of MatA
    matLambda = 0

    def __init__(self,initMAT):
        self.matA = initMAT
        self.n = self.matA.shape[0]
        self.matW = np.zeros(shape = (self.n))

    def getmatWtypeA(self):
        '''
        Get the Weight Matrix by method "Square Root".

        parameters

        NULL
        '''
        for i in range(self.n):
            s = 1.0
            for j in range(self.n):
                s = s * self.matA[i][j]
            s = pow(s,1/self.n)
            self.matW[i] = s
        p = self.matW.sum()
        for i in range(self.n):
            self.matW[i] = self.matW[i]/p
        print(self.matW)
        pass

    def getmatWtypeB(self):
        tempMat = np.zeros(shape = (self.n,self.n))
        sumList = self.matA.sum(axis = 0)
        for i in range(self.n):
            for j in range(self.n):
                tempMat[j][i] = self.matA[j][i] / sumList[i]
        #print(tempMat)
        self.matW = tempMat.sum(axis = 1)
        p = self.matW.sum()
        for i in range(self.n):
            self.matW[i] = self.matW[i]/p
        print(self.matW)
        pass

    def returnLambda(self,x1,x0):
        x = x1/x0
        return x.sum()/x1.size

    def getmatWtypeC(self):
        x0 = np.random.rand(self.n)
        x1 = np.matmul(self.matA,x0)
        oldL = 0
        newL = self.returnLambda(x1,x0)
        cnt = 1000
        while abs(newL-oldL) > 0.000000000001 and cnt > 0:
            cnt = cnt - 1
            x0 = np.true_divide( x1,np.max(x1))
            x1 = np.matmul(self.matA,x0)
            oldL = newL
            newL = self.returnLambda(x1,x0)
        self.matLambda = newL
        self.matW = x1 / x1.sum()
        print("Loop Times: ", 1000-cnt)
        print(self.matW)
        print(self.matLambda)

    def getmatLambda(self):
        a = np.matmul(self.matA,self.matW)
        b = a / self.matW
        self.matLambda = b.sum()/self.n
        print(self.matLambda)
        pass
    
    def matTest(self):
        ci = (self.matLambda - self.n)/(self.n - 1)
        cr = ci/self.ri
        print(cr)



if __name__ == "__main__":
    arr = (((1,     1/3,    3,      2       ),
            (3,     1,      5,      3       ),
            (1/3,   1/5,    1,      1/2     ),
            (1/2,   1/3,    2,      1       )))
    a = np.array(arr)
    b = ahp(a)
    b.getmatWtypeA()
    b.getmatLambda()
    b.getmatWtypeB()
    b.getmatLambda()
    b.getmatWtypeC()
    b.matTest()
    pass