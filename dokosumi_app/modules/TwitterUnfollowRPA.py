import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import io
import requests
import hashlib
import pandas as pd
import base64
import numpy as np
import re
import tweepy

# フォローされてるユーザーを取得
user_id = '1244119517275361280'
consumer_key='lWkYU1CBv01mqfGCEUz4VIA8X'
consumer_secret='bKAdtznSEKBYDPceONiaxfVYfv2Taj3NtHRjlMEdK85vfpKY1n'
access_token_key='1244119517275361280-uvZKcW3ec33T189JH7olfTpO0hlQXt'
access_token_secret='4V3S1X8DhdLGSkWlvnCVlEl8a4A47yCPOQkHaB7qQDkNp'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth ,wait_on_rate_limit = True)

friends_ids = tweepy.Cursor(api.friends_ids, user_id = user_id, cursor = -1).items()
friends_ids_list = []
for friends_id in friends_ids:
    friends_ids_list.append(friends_id)

# ユーザー名/メールアドレス
# username = input("username：")
username = "dokosumiyoshi"

# パスワード
# password = input("password：")
password = 'mzkPnd13'

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path="C:\Program Files\chromedriver_win32\chromedriver.exe", options=options)
driver.get("https://twitter.com/")

time.sleep(3)
elems = driver.find_elements_by_tag_name("a")
for elem in elems:
    attr = elem.get_attribute("data-testid") # *2:適切な属性名を指定してください。
    if (attr == "loginButton"):
        elem.click()
        break


time.sleep(3)
elems = driver.find_elements_by_name("session[username_or_email]")
for elem in elems:
    attr = elem.get_attribute("type") # *2:適切な属性名を指定してください。
    if (attr == "text"):
        username_box = elem

elems = driver.find_elements_by_name("session[password]")
for elem in elems:
    attr = elem.get_attribute("type") # *2:適切な属性名を指定してください。
    if (attr == "password"):
        password_box = elem

# ユーザ名とパスワードをインプットする
username_box.send_keys(username)
password_box.send_keys(password)

#ログインボタンをクリック
elems = driver.find_elements_by_tag_name("div")
for elem in elems:
    attr = elem.get_attribute("data-testid") # *2:適切な属性名を指定してください。
    if (attr == "LoginForm_Login_Button"):
        elem.click()
        break
        time.sleep(1)


cnt = 200
while cnt>0:

    driver.get("https://twitter.com/" + username + "/following")
    time.sleep(1)

    #ユーザーをアンフォロー
    elems = driver.find_elements_by_tag_name("div")
    for elem in elems:
        attr = elem.get_attribute("data-testid") # *2:適切な属性名を指定してください。
        if (attr == "UserCell"):

            # フォロー解除ボタンをクリック
            print(elem)
            elems2 = elem.find_elements_by_tag_name("div")
            for elem2 in elems2:

                attr = elem2.get_attribute("data-testid") # *2:適切な属性名を指定してください。
                if ("-unfollow" in str(attr)):
                    elem2.click()
                    time.sleep(1)
                    
                    # フォロー解除確認ボタンをクリック
                    elems3 = driver.find_elements_by_tag_name("div")
                    for elem3 in elems3:
                        attr = elem3.get_attribute("data-testid") # *2:適切な属性名を指定してください。
                        if (attr == "confirmationSheetConfirm"):
                            elem3.click()
                            time.sleep(1)
                            print("フォロー解除完了")
                            break
                    break
            
            continue

    cnt = cnt - 1