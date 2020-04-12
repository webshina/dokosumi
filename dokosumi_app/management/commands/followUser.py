from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import tweepy
import twitter
from requests_oauthlib import OAuth1Session
import json
from dokosumi_app.configs import keys as twitter_key
from PIL import Image
import io
import base64
from io import BytesIO
import urllib
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
import datetime
import time
import math
from pytz import timezone
import pandas as pd
import json
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
from time import sleep
from django.conf import settings
from django.template.context_processors import csrf

class Command(BaseCommand):

    def __init__(self):
        self.consumer_key = twitter_key.consumer_key
        self.consumer_secret = twitter_key.consumer_secret
        self.access_token_key = twitter_key.access_token_key
        self.access_token_secret = twitter_key.access_token_secret
        self.pk = 832
 
    def add_arguments(self, parser):
        parser.add_argument('hoge')

    ##################################################################
    ## メイン処理
    def handle(self, *args, **options):

        #ユーザーリストファイルを取得
        url = os.path.dirname(__file__) + '/userTweets.json'
        f = open(url, 'r', encoding="utf-8")

        lines = []

        for line in f:
            data = json.loads(line)
            lines.append(data)

        f.close()

        #Pandasに格納し、「フォロワーが100人以上」のユーザーのみ抽出
        df = pd.DataFrame(lines)
        df = df.drop_duplicates()
        df = df[(df['user_friends_count'] > 100)]
        df = df['user_screen_name']
        print("Tweet取得ユーザー:" + df[:])

        #フォローしたユーザーリストを取得
        url = os.path.dirname(__file__) + '/followedUsers.txt'
        f = open(url, "r", encoding="utf-8")

        lines = []

        for line in f:
            lines.append(line.rstrip('\n'))

        f.close()
        
        df2 = pd.DataFrame(lines, columns=["user_screen_name"])
        print("follow対象外ユーザー：" + df2)

        #DMを送信したユーザーを削除
        df = df[~df[:].isin(df2['user_screen_name'])]
        print("followユーザー：" + df[:])

        # follow実行
        for i in range(1):
            
            oAuth = OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)
        
            api = twitter.Api(consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        access_token_key=self.access_token_key,
                        access_token_secret=self.access_token_secret
                        )
            
            # headers = {'content-type': 'application/json'}
            # url = 'https://api.twitter.com/1.1/users/lookup.json'

            # screen_name = df.iloc[i]
            
            # try:
            #     user = api.GetUser(screen_name=screen_name)
            # except twitter.error.TwitterError as err:
            #     err = 'ユーザー:' + screen_name + 'が見つかりませんでした。'
            #     return err
            
            # payload = {
            #     'screen_name' : str(screen_name)
            # }
            # #payload = json.dumps(payload)

            # res = oAuth.get(url,
            #                 headers=headers,
            #                 params=payload)
            # res = json.loads(res.text)[0]
            # print("RESPONSE: " + str(res['following']))]
            
            #フォロー実行
            headers = {'content-type': 'application/json'}
            url = 'https://api.twitter.com/1.1/friendships/create.json'

            screen_name = df.iloc[i]

            payload = {
                'screen_name' : str(screen_name)
            }

            res = oAuth.post(url,
                            headers=headers,
                            params=payload)
            print("RESPONSE: " + str(res.reason))

            #followしたユーザーを記録
            print(str(screen_name))
            url = os.path.dirname(__file__) + '/followedUsers.txt'
            f = open(url, "a", encoding="utf-8")
            f.write(str(screen_name) + '\n')
            f.close