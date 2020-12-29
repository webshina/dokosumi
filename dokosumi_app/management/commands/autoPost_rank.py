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

        # 投稿リストファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table('dokosumi_app/data/post_comment_list.tsv')

        # ランダムに一つ抽出
        sample = score_df.sample().iloc[0]

        # コメント作成
        print(twitter_post_comment)

        # 投稿モジュールに渡す
        twitterModule = TwitterModule()
        twitterModule.officialPost(twitter_post_comment, '')
    