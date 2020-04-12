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
        self.user_id = twitter_key.user_id
        self.consumer_key = twitter_key.consumer_key
        self.consumer_secret = twitter_key.consumer_secret
        self.access_token_key = twitter_key.access_token_key
        self.access_token_secret = twitter_key.access_token_secret
 
    def add_arguments(self, parser):
        parser.add_argument('hoge')

    ##################################################################
    ## メイン処理
    def handle(self, *args, **options):
        
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token_key, self.access_token_secret)
        api = tweepy.API(auth ,wait_on_rate_limit = True)

        friends_ids = tweepy.Cursor(api.friends_ids, user_id = self.user_id, cursor = -1).items()
        friends_ids_list = []
        for friends_id in friends_ids:
            friends_ids_list.append(friends_id)
        
        followers_ids = tweepy.Cursor(api.followers_ids, user_id = self.user_id, cursor = -1).items()
        followers_ids_list = []
        for followers_id in followers_ids:
            followers_ids_list.append(followers_id)

        # フォローされてない友達を抽出
        unfollow_ids_set = set(friends_ids_list) ^ (set(friends_ids_list) & set(followers_ids_list))
        unfollow_ids_list = list(unfollow_ids_set)

        # 昔フォローした人を最初にする
        unfollow_ids_list.reverse()
        print(unfollow_ids_list)

        cnt = 0
        print(cnt)
        for f in unfollow_ids_list:
            twitter = self.getTwitterSession()

            # params = {'user_id': f}
            # url = "https://api.twitter.com/1.1/users/show.json"
            # req = twitter.get(url, params=params)
            # print("UNFOLLOWING:" + str(json.loads(req.text)['screen_name']))

            #while cnt < 10:
            params = {'user_id': f}
            url = "https://api.twitter.com/1.1/friendships/destroy.json"
            req = twitter.post(url, params=params)
            print(req.reason)
            if req.status_code == 200:
                cnt = cnt + 1
                time.sleep(1)
            else:
                break
            

    # セッション確立
    def getTwitterSession(self):
        return OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)