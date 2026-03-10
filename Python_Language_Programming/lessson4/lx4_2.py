from selenium import webdriver
from selenium.webdriver.common.by import By
import time
class tj_web(object):
    tj_browser=webdriver.Chrome()
    First_page='https://www.tongji.edu.cn'
    wait_time=3
    def __init__(self):
        pass

    def auto_click(self,click_list):
        self.tj_browser.get(self.First_page)
        time.sleep(self.wait_time)
        click_bt1 = self.tj_browser.find_element(by=By.XPATH,value='/html/body/div[3]/div/ul/li[3]/a/span')
        click_bt1.click()
        screenshot_path = f"{click_list[0]}.png"
        self.tj_browser.save_screenshot(screenshot_path)
        html_source = self.tj_browser.page_source
        html_file_path = f"{click_list[0]}.txt"
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(html_source)

        time.sleep(self.wait_time)
        self.tj_browser.get(self.First_page)
        click_bt2 = self.tj_browser.find_element(by=By.XPATH, value='/html/body/div[3]/div/ul/li[4]/a/span')
        click_bt2.click()
        screenshot_path1 = f"{click_list[1]}.png"
        self.tj_browser.save_screenshot(screenshot_path1)
        html_source1 = self.tj_browser.page_source
        html_file_path1 = f"{click_list[1]}.txt"
        with open(html_file_path1, 'w', encoding='utf-8') as file:
            file.write(html_source1)

        time.sleep(self.wait_time)
        self.tj_browser.get(self.First_page)
        click_bt3 = self.tj_browser.find_element(by=By.XPATH, value='/html/body/div[3]/div[1]/ul/li[6]/a/span')
        click_bt3.click()
        screenshot_path2 = f"{click_list[2]}.png"
        self.tj_browser.save_screenshot(screenshot_path2)
        html_source2 = self.tj_browser.page_source
        html_file_path2 = f"{click_list[2]}.txt"
        with open(html_file_path2, 'w', encoding='utf-8') as file:
            file.write(html_source2)

        pass

if __name__=='__main__':
    tj_test=tj_web()
    tj_test.auto_click(['组织机构', '师资队伍', '科学研究'])

