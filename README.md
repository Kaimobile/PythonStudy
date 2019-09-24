# PythonStudy
![](https://img.shields.io/badge/license-GPL--3.0-brightgreen.svg)

Code about Python
## Python crawler
**lvmama.py**
- Codes about crawl a website with **POST** method. Use **bs4**, **regExp** and **DataFrame**.

**kugouComment.py**
- Codes about crawl music comments. In this file, **GET** method, **JSON** content process and **DataFrame** are used.

**seleniumtest.py**
- Simulate the user's login actions in the browser to get the cookies by **selenium** Package.

**baidutest.py**
- Baidu Index Crawler. Maybe the theory of decode the baidu index data is necessary.
## Neural Network
**nntest1.py**
- A basic **Neural Network** model. The test data is MNIST.
- You can see the theory in Youdao Cloud Note.
## AHP Algorism
**ahp.py**
- Give the ralationship Matrix, compute the Weight Matrix and the Character number(default: Lambda) and Character List.
## NLP
**ProcessCom.py**

This is the project of the BIG DATA course in TJU. Maybe it is my first time to try Object-Oriented Programming. It contains 5 classes, which are for crawler, data preparation, word2vec and matrix computing.

Weibo Class:
- Delay **random** time in crawler #157

WordPre Class:
- Open and close files. #378
- Open excel by **xlrd** and read the sheet and cell you want. #352
- Use **jieba** package for a segment object. #418
- Use **jieba.posseg as psg** for the property of each segment word. #437

Word2 Class:
- Use **from gensim.models import word2vec** for the words' Vector, save and open the model. #535 

Compute Class:
- Initialize the array by **np.zeros** and **np.random.rand**. #670
- The row of the Numpy Matrix **a.shape[0]**. #803
- **np.eye** generate the matrix, which diagonal is n, others are 0. #819
- Load and save numpy matrix by **np.loadtxt** and **np.savetxt**. #823
- Use **np.vstack** for adding the vertical cells. #859
- Remind to clear the exist Object or Dict. #885
- **a.argmax(axis=0)** returns the index of the max num. #1089
- **np.matmul** for multiply two matrix. #1224

## Quantifying

**hs300peA.py**

This is a really easy Strategy for investment. It is designed for Financial Engineering Course. Codes are easy to read. Math method contains exponent, coefficient of variation and mean.

- **np.std** and **np.mean** to compute std. deviation and average. #219
- **list.append** is a method to add an element, not concat. #238
- List expression like **[5\*(n+1) for n in range(10)]**. #579
- **x,y=np.meshgrid(x,y)** is a method for 3D plot. The new x and y are both matrix and they have the same size. The same position in x and y means the x-axis and y-axis. #644

Introduction:

The structure of the code is quite easy. The strategy uses P/E to proxy value and Coefficient of Variation to proxy trend. There are about 4 parts in this strategy:

1. Add daily data. Daily data contains Price, P/E. Then compute some parameters.
2. Buy model. Buy fixed quantity stock daily and buy stock when trend appears.
3. Sell model. Sell when fall trend appears.
4. Compound interest. Calculate currency interest when a day ends.

Buy & Sell Model:
- Fixed money investment is effective.
- How to recognize the trend:
  - Choose a window of Index Price, default is 30 trade day.
  - The Price should change at least 5%. Or it is not significant.
  - Calculate the Coefficient of Variation in the window. Only CoV which is higher than top 50% is significant.
- When a raise trend appears, spend 20% left money in stock.  