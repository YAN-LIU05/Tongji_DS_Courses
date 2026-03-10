from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyttsx3

class tj_web(object):
    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def __init__(self):
        self.tj_browser = webdriver.Chrome()
        self.First_page = 'https://news.tongji.edu.cn/info/1003/88134.htm'  # 修正了 URL
        self.tj_browser.get(self.First_page)
        time.sleep(3)

    def auto_replace(self):
        time.sleep(5)  # 等待页面元素加载
        WebDriverWait(self.tj_browser, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'h3'))
        )
        # 使用 JavaScript 替换 h3 元素中的文本
        self.tj_browser.execute_script("""
        var h3Elements = document.getElementsByTagName("h3");
        for (var i = 0; i < h3Elements.length; i++) {
            h3Elements[i].textContent = h3Elements[i].textContent.replace('覃海洋', '刘彦');
        }
        """)
        time.sleep(2)

        # 获取替换后的 h3 文本并朗读
        h3_elements = self.tj_browser.find_elements(By.TAG_NAME, 'h3')
        if h3_elements:
            first_h3_text = h3_elements[1].text
            self.speak(first_h3_text)

if __name__ == "__main__":
    web = tj_web()
    web.auto_replace()