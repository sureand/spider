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
import shutil
importlib.reload(sys)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys   
from selenium.webdriver.common.action_chains import ActionChains
import logging

logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), filemode = 'a+', 
        format = '%(asctime)s - %(levelname)s: %(message)s')

current_keyword = ''
curent_urllist = []
current_keyword_index = 0

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
download_path = os.getcwd() + "/download/"
prefs = {"download.default_directory": download_path}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)

def get_url(word):
    url_str = urllib.parse.quote_plus(word)
    url = "https://cn.freeimages.com/search/{}".format(url_str)
    url = url.replace('\n', '')
    return url
    
def request_encoding(url):
    try:
      driver.get(url)
      driver.implicitly_wait(1)
    except:
          pass
    return driver.page_source
    
def get_html(url):
    html = request_encoding(url)
    return BeautifulSoup(html, 'lxml')
 
def create_directory(path):
    if not os.path.exists(path):  
        os.makedirs(path)
        
def save_pic(url):
    try:
        driver.get(url)
        driver.implicitly_wait(1)
    except:
        logging.error('save file error!')
          

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
    try:
        driver.get(url)  
        driver.find_element_by_name("username").send_keys(这里填写你的账号)    
        driver.find_element_by_name("username").send_keys(Keys.TAB)
        driver.find_element_by_name("password").send_keys(这里填写你的密码)
        driver.find_element_by_id("signin_button").click()
        time.sleep(3)
    except:
           pass

def parse_photo(url_list):
    pos = 0
    for url in url_list:
        driver.get(url)
        driver.implicitly_wait(2)
        try:
            li = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div[2]/div[2]/div/ul/li[1]/a')
            logging.info('download: ' + url)
            save_pic(li.get_attribute('href'))
            pos += 1
        except:
            logging.error(keyword)
            logging.error('can not founded element!')
            logging.error('download_failed: ' + url)
            write_all_urls(current_keyword_index, pos)
            time.sleep(1)

def save_cookies():
    dict_cookies = driver.get_cookies()
    json_cookies = json.dumps(dict_cookies)
    with open('cookies.json', 'w') as f:
      f.write(json_cookies)
      
def load_cookies():
    with open('cookies.json', 'r', encoding='utf-8') as f:
      list_cookies = json.loads(f.read())
      for cookie in list_cookies:
          t = time.time()
          cookie['expiry'] = int(t)
          driver.add_cookie(cookie)

#解释所有页面
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
        
def move_files(dest, source):
    dest = os.getcwd() + '/' + dest
    create_directory(dest)
    for file_ in os.listdir(source):
        shutil.copy(source + '/' +  file_, dest + '/' + file_ )
    for file_ in os.listdir(source):
        os.remove(source + '/' +  file_)

def write_all_urls(keyword_index, download_pos):
#出错的时候用来记录是哪个关键字的第几条, 下载列表的第几条
    try:
     with open('save_list.txt', 'w', encoding='utf-8') as f:
        f.writelines('keyword_index:' + str(keyword_index))
        for url in curent_urllist:
            f.writelines(url)
        f.writelines('download_pos:' + str(pos))
    except:
        print('wrote url_list  error!')

def restore_download():
    url_list = parse_txt('save_list.txt')
    download_urls = []
    keyword_index = -1
    if url_list:
       pos = url_list[-1]
       n = pos.find(':')
       index = pos[n+1: len(pos)]
       for i in range(int(index), len(url_list)):
           download_urls.append(url_list[i])
       parse_photo(download_urls)
       pos = url_list[0]
       n = pos.find(':')
       keyword_index = int(pos[n+1: len(pos)])
    return keyword_index
    
if __name__ == '__main__':
    login('https://cn.freeimages.com/signin?next=/')
    keyword_index = restore_download() #恢复出错前的下载
    keyword_list = parse_txt('download_list.txt')
    if keyword_index >= len(keyword_list):
       sys.exit()
    for i in (keyword_index + 1, len(keyword_list) + 1):
        pages = get_all_pages(get_url(keyword_list[i]))
        for page in pages:
            get_html(page)
            hrefs = driver.find_elements_by_css_selector(".thumbnail-rowgrid li a")
            url_list = []
            for href in hrefs:
                url_list.append(href.get_attribute('href'))
            curent_urllist = url_list
            current_keyword = keyword_list[i].replace("\n", "")
            parse_photo(url_list)
            time.sleep(120)
            move_files('save/' + current_keyword, download_path)
            current_keyword_index = i
            
    logging.info('finished!')	
    driver.close()