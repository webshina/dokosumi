from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
from stuply_app.models import Pict
import tweepy
import twitter
from requests_oauthlib import OAuth1Session
import json
from stuply_app.configs import twitter_key
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
from dateutil import parser
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

        #Pandasに格納し、「フォロワーが１０人以上１万人未満」のユーザーのみ抽出
        df = pd.DataFrame(lines)
        df = df.drop_duplicates()
        df = df[(df['user_followers_count'] > 10) & (df['user_followers_count'] < 10000)]
        df = df['user_screen_name']
        print("Tweet取得ユーザー:" + df[:])

        #DMを送信したユーザーリストを取得
        url = os.path.dirname(__file__) + '/DMSendUsers.txt'
        f = open(url, "r", encoding="utf-8")

        lines = []

        for line in f:
            lines.append(line.rstrip('\n'))

        f.close()
        
        df2 = pd.DataFrame(lines, columns=["user_screen_name"])
        print("DM送信対象外ユーザー：" + df2)

        #DMを送信したユーザーを削除
        df = df[~df[:].isin(df2['user_screen_name'])]
        print("DM送信ユーザー：" + df[:])

        # login with twitter
        session = requests.Session()
        redirect_from = "https://stuply.com/login/twitter/"
        res = session.get(redirect_from)

        soup = BeautifulSoup(res.text.encode(res.encoding), 'lxml')

        #TEMP
        # twitter_oauth_url = "https://twitter.com/sessions"
        # login_res = session.post(twitter_oauth_url, data=dataset)
        # soup = BeautifulSoup(res.text.encode(res.encoding), 'lxml')
        url = os.path.dirname(__file__) + '/source.html'
        f = open(url, "w", encoding="utf-8")
        f.write(str(soup))
        # #END

        oauth_token = soup.find(attrs={'id':'oauth_token'}).get('value')
        authenticity_token = soup.find(attrs={'name':'authenticity_token'}).get('value')
        redirect_after_login = soup.find(attrs={'name':'redirect_after_login'}).get('value')

        twitter_id = "stuply1"
        twitter_password = "mzkPnd13"
        dataset = {
                    'authenticity_token': authenticity_token,
                    'redirect_after_login': redirect_after_login,
                    'oauth_token': oauth_token,
                    'session[username_or_email]': twitter_id,
                    'session[password]': twitter_password
                }

        twitter_oauth_url = "https://twitter.com/oauth/authorize"
        login_res = session.post(twitter_oauth_url, data=dataset)
        login_soup = BeautifulSoup(login_res.text.encode(login_res.encoding), 'lxml')

        #TEMP
        # twitter_oauth_url = "https://twitter.com/sessions"
        # login_res = session.post(twitter_oauth_url, data=dataset)
        # soup = BeautifulSoup(res.text.encode(res.encoding), 'lxml')
        # url = os.path.dirname(__file__) + '/source.html'
        # f = open(url, "w", encoding="utf-8")
        # f.write(str(login_soup))
        # #END

        redirect_to = login_soup.select('.maintain-context')[0]['href']
        session.get(redirect_to)

        #送信する写真を取得
        pict = get_object_or_404(Pict, pk=self.pk)
        pict_img_base64 = base64.b64encode(open(os.path.join(settings.MEDIA_ROOT ,pict.pict_img.name), 'rb').read())
        pict_img_base64 = 'data:image/png;base64,' + str(pict_img_base64)
        pict_img_base64 = pict_img_base64.replace("b\'","")
        pict_img_base64 = pict_img_base64.replace("\\n\'","")
        comment = pict.comment

        # 13回までしか連続でDMを送れない
        # 一度にDM送信を1回までに制限
        for i in range(1):
            #「写真投稿画面」にアクセス
            res = session.get('https://stuply.com/upload_pict/')
            twitterScreenName = df.iloc[i]
            csrf = session.cookies['csrftoken']

            #写真を投稿してユーザーにDM送信
            payload = {'pict_img_base64': pict_img_base64, 'comment': comment, 'twitterScreenName': twitterScreenName, "csrfmiddlewaretoken" : csrf}
            res = session.post('https://stuply.com/upload_pict/', data=payload, headers=dict(Referer='https://stuply.com/upload_pict/'))
            print("RESULT: " + str(res))
            print("SEND TO: " + str(twitterScreenName))

            #DMを送信したユーザーを記録
            url = os.path.dirname(__file__) + '/DMSendUsers.txt'
            f = open(url, "a", encoding="utf-8")
            f.write(str(twitterScreenName) + '\n')
            f.close

            #sleep(900)