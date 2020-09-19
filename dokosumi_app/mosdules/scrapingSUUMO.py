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

class ScrapingSUUMO:

    def __init__(self):
        pass

    def getRentByStation():

        options = Options()
        # ヘッドレスモードを有効にする
        options.add_argument('--headless')
        # ChromeのWebDriverオブジェクトを作成する。
        browser = webdriver.Chrome(executable_path=r'C:\Program Files\chromedriver_win32\chromedriver.exe' ,options=options)

        prefs = ['tokyo','kanagawa','saitama','chiba']
        # prefs = ['chiba']
        station_rents = []

        for pref in prefs:

            #「路線・沿線から家賃相場・賃料相場情報を探す」へアクセス
            url = 'https://suumo.jp/chintai/soba/'+pref+'/ensen/'
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
            soup = soup.find("div", attrs={"class":"ui-section-body ui-section-body--mt20"})
            soup = soup.find_all("a")
            
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
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.graphpanel_matrix'))
                )
                time.sleep(1)

                #ページソースを取得
                soup = BeautifulSoup(browser.page_source, "html.parser")
                
                #駅名・家賃取得
                soup = soup.find_all("tr")

                rent_min = 999999999.0
                for tr in soup:

                    #駅名取得
                    try:
                        station = tr.find("td").string
                    except AttributeError:
                        print('Not Found')
                        continue
                    
                    #家賃取得
                    try:
                        rent = tr.find("span", attrs={"class":"graphpanel_matrix-td_graphinfo-strong"}).string
                    except AttributeError:
                        print('Not Found')
                        rent = 0.0

                    station_rent = [station, rent]

                    #家賃の最小値を記録
                    if float(rent) < float(rent_min) and rent != 0.0:
                        rent_min = rent

                    station_rents.append(station_rent)
                
                #家賃がNULLの場合はその路線の最小値を設定
                for station_rent in station_rents:
                    if station_rent[1] == 0.0:
                        station_rent[1] = rent_min
                        
        print(station_rents)
        browser.quit()
             
        #CSVに出力
        with open('./station_rents.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(station_rents)