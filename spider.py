from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time
import pandas as pd

def get_driver():
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  #开启无头模式
    
    #更改chromedriver.exe路径
    driver = webdriver.Chrome(executable_path = 'D:\chromedriver.exe',options = options)
    driver.maximize_window()
    driver.get('https://www.izaiwen.cn/')
    return driver

def get_input(driver):
    more_detail = driver.find_element_by_css_selector("body > div.container.list-box > form > div > div:nth-child(7) > span")
    driver.execute_script("arguments[0].click();",more_detail)

def get_info(driver,keyword):
    out_Data = []
        
    driver.find_element_by_name("keyword").clear()
    driver.find_element_by_name("keyword").send_keys(keyword)
    search = driver.find_element_by_class_name("layui-btn-normal")
    driver.execute_script("arguments[0].click();",search)
    driver.implicitly_wait(30)
    time.sleep(5)
    
    try:
        page = driver.find_element_by_class_name("layui-laypage-last").get_attribute("data-page")
    except:
        page = driver.find_element_by_class_name("layui-laypage-default").find_elements_by_tag_name('a')[-2].text
    print("检索关键词{}共得到{}页，3秒后开始爬取".format(keyword,str(page)))
    time.sleep(3)

    try:
        page = int(page)+1
    except:
        page = 1

    for i in range(0,page):
        print("正在爬取关键词{}下第{}页".format(keyword,str(i+1)))
        projects_list = driver.find_element_by_class_name("list-container-box").find_elements_by_css_selector("[class='item-box layui-card ']") 
        for project in projects_list:
            project_dict = {}
            project_dict['keyword'] = keyword
            project_dict['title'] = project.find_element_by_class_name("title").text
            
            project_dict['项目批准号'] = project.find_element_by_xpath(".//a/div/div/div[1]/div[contains(text(),'项目批准')]").text.split("：")[-1]
            project_dict['省份'] = project.find_element_by_xpath(".//a/div/div/div[1]/div[contains(text(),'省份')]").text.split("：")[-1]
            project_dict['负责人'] = project.find_element_by_xpath(".//a/div/div/div[1]/div[contains(text(),'负责')]").text.split("：")[-1]
            project_dict['依托单位'] = project.find_element_by_xpath(".//a/div/div/div[1]/div[contains(text(),'依托单位')]").text.split("：")[-1]
            
            project_dict['资助金额'] = project.find_element_by_xpath(".//a/div/div/div[2]/div[contains(text(),'金额')]").text.split("：")[-1]
            project_dict['批准年份'] = project.find_element_by_xpath(".//a/div/div/div[2]/div[contains(text(),'年份')]").text.split("：")[-1]
            project_dict['学科分类'] = project.find_element_by_xpath(".//a/div/div/div[2]/div[contains(text(),'学科')]").text.split("：")[-1]
            project_dict['资助类别'] = project.find_element_by_xpath(".//a/div/div/div[2]/div[contains(text(),'资助类别')]").text.split("：")[-1]
            
            project_dict['关键词'] = project.find_element_by_xpath(".//a/div/div/div[3]").text.split("：")[-1]
            project_dict['研究成果'] = project.find_element_by_xpath(".//a/div/div/div[4]").text.split("：")[-1]
            out_Data.append(project_dict)
        try:
            next_page = driver.find_element_by_class_name("layui-laypage-next")
            driver.execute_script("arguments[0].click();",next_page)
        
            
            driver.implicitly_wait(60)
            time.sleep(8)
        except:
            print("error")
    
    return (out_Data)

if __name__ == '__main__':
    
    #获取driver
    driver = get_driver()

    #输入登录信息，在登录页面输入账号密码，如果15s不够，可以自己改
    time.sleep(40)
    
    #点击展开选项
    get_input(driver)

    #关键词列表
    keywords=['垄断企业','价值共创']

    #获取网页信息
    data=[]
    for i,val in enumerate(keywords):
        if i == 0:
            data = get_info(driver,val)
        else:
            temp_data = get_info(driver,val)
            data.extend(temp_data)
    
    #导出结果
    df_out_data = pd.DataFrame.from_dict(data)
    df_out_data.to_excel("国自然数据2021年.xlsx")
