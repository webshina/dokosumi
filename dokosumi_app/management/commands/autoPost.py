from django.core.management.base import BaseCommand
from dokosumi_app.tools import TwitterModule
import random
import os
import pandas as pd
 
class Command(BaseCommand):
 
    def add_arguments(self, parser):
        parser.add_argument('hoge')
 
    def handle(self, *args, **options):

        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table('dokosumi_app/data/score_by_station.tsv')

        sample = score_df.sample().iloc[0]

        # コメント作成
        twitter_post_comment = '~あなたの知らない街紹介~\n'
        twitter_post_comment += '『' + sample.station_name + '』\n\n'
        twitter_post_comment += '交通利便性 : ' + str(int(sample.access)) + ' 点\n'
        twitter_post_comment += '家賃の安さ : ' + str(int(sample.landPrice)) + ' 点\n'
        twitter_post_comment += '治安の良さ : ' + str(int(sample.security)) + ' 点\n'
        twitter_post_comment += '緑地の多さ : ' + str(int(sample.park)) + ' 点\n'
        twitter_post_comment += '浸水危険度の低さ : ' + str(int(sample.flood)) + ' 点\n'
        twitter_post_comment += 'https://dokosumi.stuply.com/town_detail/' + sample.station_name + '\n'
        print(twitter_post_comment)

        # 画像取得
        twitter_post_img = 'dokosumi_app/data/town_img/' + sample.station_name + '.png'

        twitterModule = TwitterModule()
        twitterModule.officialPost(twitter_post_comment, twitter_post_img)