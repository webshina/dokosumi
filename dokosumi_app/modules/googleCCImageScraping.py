import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import requests
import hashlib
import pandas as pd
import base64
import numpy as np
import re

# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
score_df = pd.read_table('dokosumi_app/data/score_by_station.tsv')

stations = score_df['station_name']

image_save_folder_path = 'dokosumi_app/data/town_img/'

for station in stations:

    print(station + '駅の画像を収集…')

    # 既に写真が存在すればスキップ
    file_path = os.path.join(image_save_folder_path, station + '.jpg')
    if not os.path.exists(file_path):

        # クリックなど動作後に待つ時間(秒)
        sleep_between_interactions = 2

        # ダウンロードする枚数
        download_num = 1
        # 検索ワード
        query = station # + " 町並み"
        # 画像検索用のurl
        search_url = "https://www.google.com/search?q={q}&tbm=isch&tbs=il:cl&hl=ja&sa=X&ved=0CAAQ1vwEahcKEwjYkNiR1ontAhUAAAAAHQAAAAAQAg&biw=1263&bih=520"

        # サムネイル画像のURL取得
        options = Options()
        options.add_argument('--headless')
        wd = webdriver.Chrome(executable_path="C:\Program Files\chromedriver_win32\chromedriver.exe", options=options)
        wd.get(search_url.format(q=query))
        # サムネイル画像のリンクを取得(ここでコケる場合はセレクタを実際に確認して変更する)
        thumbnail_results = wd.find_elements_by_css_selector("img.rg_i")

        # サムネイルをクリックして、各画像URLを取得
        image_urls = set()
        for img in thumbnail_results[:download_num]:
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue
            # 一発でurlを取得できないので、候補を出してから絞り込む(やり方あれば教えて下さい)
            # 'n3VNCb'は変更されることあるので、クリックした画像のエレメントをみて適宜変更する
            url_candidates = wd.find_elements_by_class_name('n3VNCb')
            for candidate in url_candidates:
                url = candidate.get_attribute('src')
                image_urls.add(url)
        # 少し待たないと正常終了しなかったので3秒追加
        time.sleep(sleep_between_interactions+3)
        wd.quit()

        # 画像のダウンロード
        image_save_folder_path = 'dokosumi_app/data/town_img/'
        for url in image_urls:
            try:
                if url and 'http' in url:
                    image_content = requests.get(url).content
                elif url and 'image/jpeg;base64' in url:
                    # 頭のいらない部分を取り除いた上で、バイト列にエンコード
                    image_data_bytes = re.sub('^data:image/.+;base64,','',url).encode('utf-8')
                    # バイト列をbase64としてデコード
                    image_content = base64.b64decode(image_data_bytes)
                else:
                    print('URL invalid : ' + url)
            except Exception as e:
                print(f"ERROR - Could not download {url} - {e}")

            try:
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                file_path = os.path.join(image_save_folder_path, station + '.jpg')
                with open(file_path, 'wb') as f:
                    image.save(f, "JPEG", quality=90)
                print(f"SUCCESS - saved {url} - as {file_path}")
            except Exception as e:
                print(f"ERROR - Could not save {url} - {e}")
    
    else:
        print('既に収集済み')