from selenium import webdriver
'''
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
'''
driver = webdriver.Chrome()
driver.get("http://image.baidu.com/")
driver.implicitly_wait(1)


//*[@id="content"]/div/div[2]/div[1]/div/div[4]/ul

#content > div > div.display-table.listing-body > div.table-cell.main > div > div.detail-btns.clearfix > div.detail-btns-action > div > ul

//*[@id="content"]/div/div[2]/div[1]/div/div[2]/div[2]/div/ul

