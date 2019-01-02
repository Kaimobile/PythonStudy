# PythonStudy
![](https://img.shields.io/badge/license-GPL--3.0-brightgreen.svg)

Code about Python

## Python crawler

**lvmama.py**

- Codes about crawl a website with **POST** method. Use **bs4**, **regExp** and **DataFrame**.

**kugouComment.py**

- Codes about crawl music comments. In this file, **GET** method, **JSON** content process and **DataFrame** are used.

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


