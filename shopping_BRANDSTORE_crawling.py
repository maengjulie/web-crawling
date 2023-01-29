'''
0. Import packages
'''
from bs4 import BeautifulSoup
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
import time
from datetime import timedelta


type = '브랜드스토어'
driver_path = "C:\chromedriver_win32\chromedriver.exe"  # path to Chrome Driver

start_time = time.time()


'''if type == '브랜드스토어':
    xpath_idx = 4
elif type == '소호몰':
    xpath_idx = 5'''

print("**** Accessing Listed Stores ****")
driver = selenium.webdriver.Chrome(driver_path)
driver.get("https://search.shopping.naver.com/allmall")
driver.find_elements_by_xpath("//a[contains(@class, 'mallTab_link_mall__2SLt6')]")[4].send_keys(Keys.ENTER)
time.sleep(3)
previous_height = driver.execute_script('return document.body.scrollHeight')
while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(3)
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == previous_height:
        break
    previous_height = new_height

soup = BeautifulSoup(driver.page_source, "html.parser")
divs = soup.find_all('li', class_='mallListItem_item_mall__3yVIl')
urls = []
for i in divs:
    # print(i.find('a')['href'].strip())
    url = i.find('a')['href'].strip()
    urls.append(url)
driver.close()
print("Complete")

print("**** Retrieving URLs ****")
brand_urls = []
driver = selenium.webdriver.Chrome(driver_path)
for url in urls:
    driver.get(url)
    brand_urls.append(driver.current_url)
driver.close()
print("Complete")


print("**** Extracting Brand Names ****")
brand_names = []
for idx, x in enumerate(brand_urls):
    if idx == 0:
        brand_name = x.split("com/", 1)[1]
    else:
        brand_name = x.split("com/", 1)[1].split('?')[0]
    #print(brand_name)
    brand_names.append(brand_name)
print(len(brand_names))
print("Complete")


print("**** Extracting Company Info ****")
data = []
for brand in brand_names:
    target_url = 'https://brand.naver.com/' + brand + '/profile?cp=2'
    result = requests.get(target_url)
    a = result.text
    soup = BeautifulSoup(a, 'html.parser')
    divs = soup.find_all('div', class_='_2PXb_kpdRh')
    divs2 = soup.find_all('div', class_='_2E256BP8nc')
    element_list = []
    for div in divs:
        element_list.append(div.text)
    if len(element_list) >= 2:
        del element_list[2]
        new = element_list[2][:-2]
        element_list[2] = new
    element_keys = []
    for d in divs2:
        element_keys.append(d.text)
    individual_data = dict(zip(element_keys, element_list))
    #print(individual_data)
    data.append(individual_data)

df = pd.DataFrame(data)
df.index = np.arange(1, len(df) + 1)
df.index.name = 'No.'

df.to_excel('네이버_브랜드스토어_판매자정보_크롤링.xlsx'.format(type), encoding='euc-kr')

print("Complete")
elapsed_time = time.time() - start_time
print("Elapsed time: %s" % (str(timedelta(seconds=elapsed_time))))
