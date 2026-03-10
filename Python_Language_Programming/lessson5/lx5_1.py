from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import xlwt

class top_baidu(object):
    baidu_browser=webdriver.Chrome()
    First_page='https://top.baidu.com'
    wait_time=6

    def __init__(self):
        self.baidu_browser.get(self.First_page)
        time.sleep(self.wait_time)

    def get_data(self):
        hot_search=self.baidu_browser.find_element(By.CLASS_NAME,value='list_1EDla')
        top_list=hot_search.find_elements(By.CLASS_NAME,value='name_2Px2N')
        result_list=[]
        for item in top_list:
            if len(item.text)>0:
                result_list.append(item.text)

        return result_list

    def save_to_excel(self, data):
        workbook = xlwt.Workbook(encoding = 'utf-8')
        sheet = workbook.add_sheet('Baidu Hot List')
        sheet.write(0, 0, 'Title')

        # 写入数据
        for row_num, title in enumerate(data, start=1):
            sheet.write(row_num, 0, title)

        workbook.save('hot_list.xls')

if __name__ == "__main__":
    top_baidu = top_baidu()
    data = top_baidu.get_data()
    top_baidu.save_to_excel(data)