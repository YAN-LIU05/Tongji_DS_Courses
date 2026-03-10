from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class tj_bbs(object):
    bbs_browser=webdriver.Chrome()
    login_page='http://cyr985.net3v.club/bbs/login.asp'
    post_page='http://cyr985.net3v.club/bbs/topic.asp?id=4891&boardid=6&TB=1'
    wait_time=3
    def __init__(self):
        pass
    def auto_login(self,username,password):
        self.bbs_browser.get(self.login_page)
        time.sleep(self.wait_time)
        #name_bt=self.bbs_browser.find_element(by=By.NAME,value='name')
        name_bt = self.bbs_browser.find_element(by=By.XPATH, value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[1]/div[1]/input')
        name_bt.send_keys(username)
        #pwd_bt=self.bbs_browser.find_element(by=By.NAME,value='Password')
        pwd_bt = self.bbs_browser.find_element(by=By.XPATH, value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[2]/div[1]/input')
        pwd_bt.send_keys(password)
        #login_bt=self.bbs_browser.find_element(by=By.CLASS_NAME,value='login')
        login_bt=self.bbs_browser.find_element(by=By.XPATH, value='/html/body/div[5]/table/tbody/tr/td/div[2]/form/div[5]/input')
        login_bt.click()
        time.sleep(self.wait_time)
        pass

    def auto_post(self,bbs_content):
        self.bbs_browser.get(self.post_page)
        time.sleep(self.wait_time)
        click_bt1 = self.bbs_browser.find_element(by=By.XPATH,value='//*[@id="Board"]/div[5]/a')
        click_bt1.click()
        click_bt2 = self.bbs_browser.find_element(by=By.XPATH,value='/html/body/div[5]/table[1]/tbody/tr/td[2]/a')
        click_bt2.click()
        content_bt=self.bbs_browser.find_element(by=By.XPATH,value='//*[@id="edit"]')
        content_bt.send_keys(bbs_content)
        click_bt3 = self.bbs_browser.find_element(by=By.XPATH, value='//*[@id="sayb"]')
        click_bt3.click()
        pass

if __name__=='__main__':
    tj_test=tj_bbs()
    tj_test.auto_login('YAN','lzz20050511')
    tj_test.auto_post('hello')

