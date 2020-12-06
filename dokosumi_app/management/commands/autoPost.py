from django.core.management.base import BaseCommand
from dokosumi_app.tools import TwitterModule
import random
import os
import pandas as pd
import urllib.parse

class Command(BaseCommand):
 
    def add_arguments(self, parser):
        parser.add_argument('hoge')
 
    def handle(self, *args, **options):

        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table('dokosumi_app/data/score_by_station.tsv')

        # 住みたい街ランキングのTSVファイルを取得
        dirname = os.path.dirname(__file__)
        sumitaimachi_rank_df = pd.read_table('dokosumi_app/data/sumitaimachi_rank.tsv')

        # 住みたい街ランキング100位圏内の街を抽出
        score_df = score_df[score_df['station_name'].isin(sumitaimachi_rank_df['station_name'])]

        # ランダムに一つ抽出
        sample = score_df.sample().iloc[0]

        # コメント作成
        twitter_post_comment = '~あなたの街の鑑定結果~\n'
        twitter_post_comment += '#' + sample.station_name + '\n\n'
        twitter_post_comment += sample.comment + '\n\n'
        twitter_post_comment += 'アクセスの良さ : ' + str(int(sample.access)) + ' 点\n'
        twitter_post_comment += '家賃の安さ : ' + str(int(sample.landPrice)) + ' 点\n'
        twitter_post_comment += '買い物のしやすさ : ' + str(int(sample.supermarket)) + ' 点\n'
        twitter_post_comment += '治安の良さ : ' + str(int(sample.security)) + ' 点\n'
        twitter_post_comment += '浸水危険度の低さ : ' + str(int(sample.flood)) + ' 点\n\n'
        twitter_post_comment += '#どこ住吉\n'
        twitter_post_comment += 'https://dokosumiyoshi.tokyo/town_detail/' + urllib.parse.quote(sample.station_name) + '\n'
        print(twitter_post_comment)

        # 画像取得
        twitter_post_img = 'dokosumi_app/static/img/town_img/' + sample.station_name + '.jpg'

        # 投稿モジュールに渡す
        twitterModule = TwitterModule()
        twitterModule.officialPost(twitter_post_comment, twitter_post_img)
    