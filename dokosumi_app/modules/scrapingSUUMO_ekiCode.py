import requests
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import urljoin
import lxml.html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re

options = Options()
# ヘッドレスモードを有効にする
# options.add_argument('--headless')
# ChromeのWebDriverオブジェクトを作成する。
browser = webdriver.Chrome(executable_path=r'C:\Program Files\chromedriver_win32\chromedriver.exe' ,options=options)

prefs = ['tokyo','kanagawa','saitama','chiba']
# prefs = ['chiba']

#駅名と駅コードを格納するリストを作成
station_name_code_list = []

for pref in prefs:
    print(pref + "から取得")

    #「路線・沿線から家賃相場・賃料相場情報を探す」へアクセス
    url = 'https://suumo.jp/chintai/'+pref+'/ensen/'
    browser.get(url)
    print("「路線・沿線から家賃相場・賃料相場情報を探す」にアクセスしました")
    #ページが表示されるまで待機
    e = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.searchtable-title'))
    )
    time.sleep(1)

    #ページソースを取得
    soup = BeautifulSoup(browser.page_source, "html.parser")
    
    #路線リスト取得
    url = '^/chintai/' + pref + '/en_'
    soup = soup.find_all("a", attrs={"href":re.compile(url)})
    # soup = soup.find_all('a', href=re.compile(url))
    
    routes = []
    for a in soup:
        route = a.get('href')
        routes.append(route)
    
    #「各路線の家賃相場情報」へアクセス
    for url in routes:
        print("URL:"+url)

        browser.get('https://suumo.jp/'+str(url))
        print("「各路線の家賃相場情報」にアクセスしました")
        #ページが表示されるまで待機
        e = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.searchitem-list'))
        )
        time.sleep(1)

        #ページソースを取得
        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        #駅コード・駅名取得
        soup = soup.find_all("input", attrs={"name":"ek"})
        for item in soup:

            #駅コード取得
            try:
                ekiCode = item.get('value')
                #末尾から5文字を切り取り
                ekiCode = ekiCode[-5:]
            except AttributeError:
                print('Not Found')
                ekiCode = 'ERROR'
                continue

            print(ekiCode)

            #駅名取得
            item = item.parent
            item = item.find('label').find('span')
            try:
                station_name = item.string
            except AttributeError:
                print('Not Found')
                station_name = 'ERROR'
                continue

            print(station_name)

            # 駅名と駅コードを格納
            station_name_code_list.append([station_name, ekiCode])
            print(station_name_code_list)

browser.quit()
        
#CSVに出力
#プログラムの実行ディレクトリを取得
dirname = os.path.dirname(os.path.abspath(__file__))
with open(dirname + '/station_name_code_list.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(station_name_code_list)
