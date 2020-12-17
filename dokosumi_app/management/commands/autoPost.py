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
        # sample = score_df.sample().iloc[0]
        sample = score_df.loc[score_df['station_name'] == '武蔵浦和']
        print(sample.station_name)

        # コメント作成
        twitter_post_comment = '#' + sample.station_name + '\n\n'

        # 街のコメントを作成
        comment = str(sample.comment)
        # 街のコメントが80文字を超える場合は省略
        if len(comment) > 80:
            comment = comment[0:80] + '…' 
        # Nullの場合はコメントをテンプレート設定
        if comment == 'nan':
            comment = 'コメント募集中！この街へのコメントとともにリツイートお願いします。'

        twitter_post_comment += '' + comment + '\n\n'
        twitter_post_comment += 'アクセスの良さ : ' + str(int(sample.access)) + ' 点\n'
        twitter_post_comment += '家賃の安さ : ' + str(int(sample.landPrice)) + ' 点\n'
        twitter_post_comment += '買い物のしやすさ : ' + str(int(sample.supermarket)) + ' 点\n'
        twitter_post_comment += '治安の良さ : … '
        twitter_post_comment += 'https://dokosumiyoshi.tokyo/town_detail/' + urllib.parse.quote(sample.station_name) + '\n'
        print(twitter_post_comment)

        # 画像取得
        twitter_post_img = 'dokosumi_app/static/img/town_img/' + sample.station_name + '.jpg'

        # 投稿モジュールに渡す
        twitterModule = TwitterModule()
        twitterModule.officialPost(twitter_post_comment, twitter_post_img)
    