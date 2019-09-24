#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File    :   seleniumtest.py
@Time    :   2019-04-03
@Author  :   KAI
@Version :   1.01
@License :   (C) Copyright 2012-2019, Kaimobile
@Contact :   kyan@tju.edu.cn
@Desc    :   None
"""

'''
# Use Guide:
# 1. Install the driver for the browser firstly
# 2. Change the browser type in function "openWeb()"
# 3. Notice the default attributes in class "seleniumLogin"
# 4. Instantiated the object and run "mainProcess()"
# 5. Run "closeWeb()" finally
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import Select
from PIL import Image
import unittest
import time


class seleniumLogin(object):
    '''Simulate logining Baidu Account and get Cookies

    You need to install the driver for the browser first!

    Attributes:
        verifyCodeImgName: the file name of the verifycode image saved 
            on the disk
        usernameStr1: The string of account 1 userName
        passwordStr1: The string of account 1 password
        driver: the object of browser
        initURL: A string of the initial URL
    '''
    verifyCodeImgName = "verifyCodeImg.png"
    usernameStr1 = ""
    passwordStr1 = ""
    usernameStr2 = ""
    passwordStr2 = ""
    driver = None
    initURL = ''

    def __init__(self):
        self.openWeb()
        pass
    def openWeb(self):
        '''Open the browser and prepare

        Open the browser, input the target URL.
        Minimize the window and get the real URL.

        '''
        self.driver = webdriver.Edge()
        self.driver.get("https://passport.baidu.com")
        self.driver.maximize_window()
        self.initURL = self.driver.current_url   
        pass
    def changeLoginType(self):
        '''Change the login style

        Because there two login methods. One is scanning QR Code. The other
        is type userName and password. This function is to switch the login
        method to the traditional typing way.

        '''
        print("正在更改登陆方式...")
        elem = self.driver.find_element_by_id("TANGRAM__PSP_3__footerULoginBtn")
        if elem.is_displayed():
            #ActionChains(self.driver).click(elem).perform()
            elem.click()
        pass
    def inputAccount(self, usernameStr, passwordStr):
        '''Input the userName and password to the Input_Form

        Input the username and password.
        Then select the Pass_Remember Box.

        Args:
            usernameStr: The String of username
            passwordStr: The String of password

        '''
        print("正在输入用户名和密码...")
        username = self.driver.find_element_by_id("TANGRAM__PSP_3__userName")
        username.clear()
        username.send_keys(usernameStr)
        password = self.driver.find_element_by_id("TANGRAM__PSP_3__password")
        password.clear()
        password.send_keys(passwordStr)
        memberPass = self.driver.find_element_by_id("TANGRAM__PSP_3__memberPass")
        if not memberPass.is_selected():
            memberPass.click()
        print("用户名密码输入完成！")
        pass
    def getVerifyCode(self):
        '''Process Verify Code

        Judge if verify code is needed. If verify code is needed, the verify code
        will display by your photo viewer.

        Returns:
            True: Verify Code is needed.
            False: Verify Code is not needed.
        
        '''
        print("正在判断是否需要输入验证码...")
        verifyCode = self.driver.find_element_by_id("TANGRAM__PSP_3__verifyCode")
        if verifyCode.is_displayed():
            print("需要输入，正在打开验证码图片，关闭图片后可以输入！")
            verifyCodeImg = self.driver.find_element_by_id("TANGRAM__PSP_3__verifyCodeImg")
            self.driver.save_screenshot(self.verifyCodeImgName)
            left = verifyCodeImg.location['x']
            width = verifyCodeImg.size['width']
            height = verifyCodeImg.size['height']
            top = verifyCodeImg.location['y']
            picture = Image.open(self.verifyCodeImgName)
            picture = picture.crop((left, top, left+width, top+height))
            picture.save(self.verifyCodeImgName)
            picture.show()
            return True
        else:
            print("无需输入验证码！")
            return False
    def clickSubmit(self):
        '''Click Submit Button

        Submit and judge if login is successful.

        Returns: 
            True: Login successful
            False: Login unsuccessful

        '''
        time.sleep(2)
        print("正在登陆...")
        submit = self.driver.find_element_by_id("TANGRAM__PSP_3__submit")
        submit.click()
        #ActionChains(driver).click(submit).perform()
        try:
            for i in range(5):
                time.sleep(1)
                if self.loginJudge():
                    #verifyCodeText = verifyCode.get_attribute('value')
                    # print("Now-->",verifyCodeText,"<--")
                    print("请稍后，剩余等待时间", 4-i,"秒")
                else:
                    print("登陆成功！")
                    return True
        except:
            print("登陆出错，请重试")
            return False
        else:
            print("登陆出错，请重试")
            return False
        '''if cs is 1:
            errorElem = self.driver.find_element_by_id("TANGRAM__PSP_3__error")
            errorText = errorElem.get_attribute("value")
            print(errorText)
            return False
        else:
            print("网络错误，请重试！")
            return False'''
    def inputVerifyCode(self, verifyCodeStr):
        '''Input the verify code string

        Input the verify code string to the VerifyCode_Form

        Args:
            verifyCodeStr: The string of verify code

        '''
        verifyCode = self.driver.find_element_by_id("TANGRAM__PSP_3__verifyCode")
        verifyCode.clear()
        verifyCode.send_keys(verifyCodeStr)
        #verifyCode.send_keys(Keys.ENTER)
        #verifyCode.send_keys(Keys.ENTER)
        pass
    def getCookies(self):
        '''Get the cookies on "index.baidu.com"

        Open the website "index.baidu.com", get the cookies and 
        transform the cookies into a Dict, like {"name":"value",}

        Returns:
            cookiesDict: The Dict contains cookies, like {"name":"value",}

        '''
        self.driver.get("https://index.baidu.com")
        cookies = self.driver.get_cookies()
        cookiesDict = {}
        for cookie in cookies:
            cookiesDict[cookie['name']] = cookie['value']
        return cookiesDict
    def loginState(self):
        '''Judge if login is needed

        Judge if login is needed by searching the element Username_Input_Form
        in about 5 seconds. If it can't find the element, it means that login 
        is not needed.
        
        Returns: 
            True: Login is needed
            False: Login is not needed

        '''
        print("正在判断是否需要登陆...")
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.ID,"TANGRAM__PSP_3__qrcode"))
            )
        except:
            print("需要登陆！")
            return True
        else:
            print("无需登陆！")
            return False
    def loginJudge(self):
        '''Judge if login is still working

        Judge if login is still working by searching the element
        Username_Input_Form immediately. If it can't find the 
        element, it means that the working status is changed.

        Returns:
            True: Login process is still on
            False: Login process has changed

        '''
        try:
            element = WebDriverWait(self.driver, 0).until(
                EC.invisibility_of_element_located((By.ID,"TANGRAM__PSP_3__userName"))
            )
        except:
            return True
        else:
            return False

    def mainProcess(self):
        '''A whole process for simulating

        A whole process for simulating and get the cookies.

        Returns:
            cookies: The cookies Dict. If it returns a NULL Dict, it 
                means something wrong happened.

        '''
        if self.loginState():
            self.changeLoginType()
            self.inputAccount(self.usernameStr1, self.passwordStr1)
            cs = 0
            try:
                for i in range(10):
                    if self.getVerifyCode():
                        a = input("请输入验证码：")
                        self.inputVerifyCode(a)
                    if self.clickSubmit():
                        cs = 1
                        break
            except:
                print("Something wrong with the program, please try again! \
                    Or you can login the Baidu Account in the broswer directly. \
                    Then try to run the function again.")
                return {}
            else:
                if cs is 1:
                    print("Return the cookies successfully!")
                    return self.getCookies()
                else:
                    print("Something wrong with the program, please try again! \
                    Or you can login the Baidu Account in the broswer directly. \
                    Then try to run the function again.")
                    return {}
        else:
            return self.getCookies()
        self.driver.close()
    def closeWeb(self):
        '''Close the browser'''
        #self.driver.maximize_window()
        self.driver.close()
        

#a = seleniumLogin()
#print(a.mainProcess())
            




 
#finally:
#    driver.quit()
#a = EC.invisibility_of_element_located((By.ID,"TANGRAM__PSP_3__footerULoginBtn"))
#print(EC.url_changes(initURL))

#ActionChains(driver).click(username).perform()

#print(username.is_displayed())
#time.sleep(2)



#print(memberPass.is_selected())


'''

    '''
    #print(cookiesDict)


#elem.send_keys(Keys.LEFT)
#elem = driver.find_element_by_id("su")
#elem.send_keys(Keys.ENTER)
#print(elem)
#driver.close()