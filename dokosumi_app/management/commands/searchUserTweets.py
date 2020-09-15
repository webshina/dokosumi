from django.core.management.base import BaseCommand
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
from dateutil import parser

class Command(BaseCommand):

    def __init__(self):
        self.consumer_key = twitter_key.consumer_key
        self.consumer_secret = twitter_key.consumer_secret
        self.access_token_key = twitter_key.access_token_key
        self.access_token_secret = twitter_key.access_token_secret
 
    def add_arguments(self, parser):
        parser.add_argument('keyword', type=str, help='Tweetを検索するキーワードを入力')

    ##################################################################
    ## メイン処理
    def handle(self, *args, **options):
        # 書き込み先ファイルをクリア
        url = os.path.dirname(__file__) + '/userTweets.json'
        f = open(url, "w", encoding="utf-8")
        f.write('')
        f.close()
        
        timelines = []
        # ツイートID
        max_id = ''
        # 検索ワード
        keyword = options['keyword']
        # ツイート取得対象日
        dt_now = datetime.datetime.now()
        start_dt = dt_now.strftime('%Y%m%d')

        start_dt = datetime.datetime.strptime(start_dt, '%Y%m%d')
        for i in range(10):
            dt = (start_dt - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            # print(dt)
            since = str(dt) + '_00:00:00_JST'
            until = str(dt) + '_23:59:59_JST'

            while True:
                # APIの残り利用回数を取得
                limit, remaining, reset_minute = self.rate_limit_status()
                print('-' * 30)
                print('limit :{}'.format(limit))
                print('remaining :{}'.format(remaining))
                print('reset :{} minutes'.format(reset_minute))

                # APIの残り利用回数が0回の場合に回復するまで待機する
                if remaining == 0:
                    time.sleep(60 * (int(reset_minute) + 1))

                time.sleep(1)

                # ツイート検索
                timelines, max_id = self.getTwitterTimeline(keyword, since, until, max_id)

                # ツイートが取得できない場合
                if timelines == []:
                    time.sleep(5)
                    break

                # 日付ごとにjsonで書き込み
                # 1ツイートごとのjsonで書き込み後に改行を付与する
                url = os.path.dirname(__file__) + '/userTweets.json'
                f = open(url, "a", encoding="utf-8")
                for timeline in timelines:
                    json.dump(timeline
                            ,f
                            ,ensure_ascii=False
                            ,sort_keys=True
                            # ,indent=4
                            ,separators=(',', ': ')
                    )
                    f.write('\n')
                f.close()

                print(max_id)

                time.sleep(5)

    # セッション確立
    def getTwitterSession(self):
        return OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)

    # キーワード検索で得られたツイートを取得する
    # max_idを使用して次の100件を取得
    def getTwitterTimeline(self, keyword, since='', until='', max_id=''):
        timelines = []
        id = ''
        twitter = self.getTwitterSession()

        url = "https://api.twitter.com/1.1/search/tweets.json"
        params = {'q': keyword, 'count': 100, 'result_type': 'mixed'}

        if max_id != '':
            params['max_id'] = max_id
        if since != '':
            params['since'] = since
        if until != '':
            params['until'] = until

        print(params)

        req = twitter.get(url, params=params)

        if req.status_code == 200:
            search_timeline = json.loads(req.text)
            # APIからの返却内容を表示する
            # print(search_timeline)

            for tweet in search_timeline['statuses']:
                print('-' * 30)
                id = str(tweet['id'])
                print(id)
                print(str(parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo'))))

                # 次の100件を取得したときにmax_idとイコールのものはすでに取得済みなので捨てる
                if max_id == str(tweet['id']):
                    print('continue')
                    continue

                timeline = {'id': tweet['id']
                    #, 'created_at': str(parser.parse(tweet['created_at']).astimezone(timezone('Asia/Tokyo')))
                    #, 'text': tweet['text']
                    , 'user_id': tweet['user']['id']
                    #, 'user_created_at': str(parser.parse(tweet['user']['created_at']).astimezone(timezone('Asia/Tokyo')))
                    #, 'user_name': tweet['user']['name']
                    , 'user_screen_name': tweet['user']['screen_name']
                    #, 'user_description': tweet['user']['description']
                    #, 'user_location': tweet['user']['location']
                    #, 'user_statuses_count': tweet['user']['statuses_count']
                    #, 'user_followers_count': tweet['user']['followers_count']
                    , 'user_friends_count': tweet['user']['friends_count']
                    #, 'user_listed_count': tweet['user']['listed_count']
                    #, 'user_favourites_count': tweet['user']['favourites_count']
                }

                # urlを取得
                if 'media' in tweet['entities']:
                    medias = tweet['entities']['media']
                    for media in medias:
                        timeline['url'] = media['url']
                        break
                elif 'urls' in tweet['entities']:
                    urls = tweet['entities']['urls']
                    for url in urls:
                        timeline['url'] = url['url']
                        break
                else:
                    timeline['url'] = ''

                timelines.append(timeline)

        print('-' * 30)
        print(timelines)
        twitter.close()

        return timelines, id

    # API利用回数に引っかかった場合に待機させる
    def rate_limit_status(self):
        twitter = self.getTwitterSession()
        limit = 1
        remaining = 1
        reset_minute = 0

        url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
        req = twitter.get(url)
        if req.status_code == 200:
            limit_api = json.loads(req.text)

            limit = limit_api['resources']['search']['/search/tweets']['limit']
            remaining = limit_api['resources']['search']['/search/tweets']['remaining']
            reset = limit_api['resources']['search']['/search/tweets']['reset']
            reset_minute = math.ceil((reset - time.mktime(datetime.datetime.now().timetuple())) / 60)

        twitter.close()

        return limit, remaining, reset_minute