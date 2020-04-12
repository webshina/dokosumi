from django.conf import settings
import tweepy
import twitter
from social_django.models import UserSocialAuth
from requests_oauthlib import OAuth1Session
import json
from .configs import keys as twitter_key
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


class TwitterModule:
    def __init__(self):
        self.consumer_key = twitter_key.consumer_key
        self.consumer_secret = twitter_key.consumer_secret
        self.access_token_key = twitter_key.access_token_key
        self.access_token_secret = twitter_key.access_token_secret

    # 公式アカウントで投稿
    def officialPost(self, twitter_post_comment, pict_img):
        
        # 画像をアップロードし、media_idを取得
        upload_api = "https://upload.twitter.com/1.1/media/upload.json"
        post_api = "https://api.twitter.com/1.1/statuses/update.json"
        
        oAuth = OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)

        pict_img = os.path.join(pict_img)
        print(pict_img)
        img = {"media" : open(pict_img, 'rb')}
        print(img)
        req_media = oAuth.post(upload_api, files = img)
        print(req_media.text)
        media_id = json.loads(req_media.text)['media_id']

        params = {"status": twitter_post_comment, "lang": "ja", "media_ids": [media_id]}

        # 画像と文章を投稿
        req_post = oAuth.post(post_api, params)
        print(req_post)


class MailModule:
    def __init__(self):
        self.from_address = 'stuply.19921004@gmail.com'
        self.password = 'mzkPnd13'
        self.bcc_address = ''

    def create_message(self, from_address, to_address, bcc_address, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Bcc'] = bcc_address
        msg['Date'] = formatdate()
        return msg

    def send(self, to_address, subject, body):
        msg = self.create_message(self.from_address, to_address, self.bcc_address, subject, body)

        #context = ssl.create_default_context()
        smtpobj = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        smtpobj.login(self.from_address, self.password)
        smtpobj.sendmail(self.from_address, to_address, msg.as_string())
        smtpobj.close()