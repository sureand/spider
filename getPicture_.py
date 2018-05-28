# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib
import os
import time
import random
import json
import importlib 
import sys
importlib.reload(sys)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys   
from selenium.webdriver.common.action_chains import ActionChains
'''
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
'''
driver = webdriver.Chrome()

def get_url(word):
    url_str = urllib.parse.quote_plus(word)
    url = "https://cn.freeimages.com/search/{}".format(url_str)
    return url
    
def request_encoding(url):
    driver.get(url)
    driver.implicitly_wait(1)
    return driver.page_source
    
def get_html(url):
    html = request_encoding(url)
    return BeautifulSoup(html, 'lxml')

def random_code():
    return random.randint(50000, 59999)
 
def create_directory(path):
    if not os.path.exists(path):  
        os.makedirs(path)  
        os.chdir(path)
        
def save_pic(url):
    driver.get(url)
    driver.implicitly_wait(1)

def parse_txt(path):
    assert(path)
    text_line = []
    file = open(path, 'r', encoding='utf-8') 
    line = file.readline()
    while line:
      text_line.append(line)
      line = file.readline()
    file.close()  
    return text_line
       
def parse_config():
    config = []
    with open('config.json', 'r') as f:
        content = json.load(f)
    return content
    
def login(url):
    driver.get(url)  
    driver.find_element_by_name("username").send_keys("851497767@qq.com")    
    driver.find_element_by_name("username").send_keys(Keys.TAB)
    driver.find_element_by_name("password").send_keys("lishu1123")
    driver.find_element_by_id("signin_button").click()
    time.sleep(3)
    driver.find_element_by_name("password").send_keys(Keys.ENTER)  
    
def parse_photo(url_list):
    for url in url_list:
        driver.get(url)
        driver.implicitly_wait(2)
        li = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div[2]/div[2]/div/ul/li[1]/a')
        if != li:
           continue
        save_pic(li.get_attribute('href'))

def save_cookies():
    dictCookies = driver.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    with open('cookies.json', 'w') as f:
      f.write(jsonCookies)
      
def load_cookies():
    with open('cookies.json', 'r', encoding='utf-8') as f:
      cookies_list = json.loads(f.read())
      for cookie in cookies_list:
          t = time.time()
          cookie['expiry'] = int(t)
          driver.add_cookie(cookie)

def get_all_pages(url):
    pages_list = []
    get_html(url)
    pages_list.append(url)
    max = '0'
    try:
      ul = driver.find_element_by_xpath('.//*[@id="content"]/div/div[3]/div[2]/div/ul[2]')
      ul = ul.find_elements_by_xpath('li')
      for li in ul:
         try:
           a = li.find_element_by_xpath('a')
           href = a.get_attribute('href')
           n = href.rfind('/')
           if href[n+1: len(href)].isdigit():
              if int(href[n+1: len(href)]) > int(max):
                 max = href[n+1: len(href)]
         except:
           pass

      if len(ul):
        length = int(max)
        for i in range(2, length+1):
            pages = url+ '/' + str(i)
            pages_list.append(pages)
    except:
      pass
    return pages_list
            
if __name__ == '__main__':
    login('https://cn.freeimages.com/signin?next=/')
    keyword_list = parse_txt('download_list.txt')
    for keyword in keyword_list:
        pages = get_all_pages(get_url(keyword))
        for page in pages:
            get_html(page)
            hrefs = driver.find_elements_by_css_selector(".thumbnail-rowgrid li a")
            url_list = []
            for href in hrefs:
                url_list.append(href.get_attribute('href'))
            parse_photo(url_list)
    driver.close()