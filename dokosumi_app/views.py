from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
import uuid
from PIL import Image
import io
import base64
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from django.db import transaction
import urllib
import random
import pandas as pd
import time
import os
import pathlib
import math
import numpy as np
import copy
from .models import ResultRank

# TEST
def test(request):
    if request.method == "POST":
        return redirect('test')
    else:
        return render(request, 'dokosumi_app/test.html')

# TOP
def top(request):
    if request.method == "POST":
        return redirect('top')
    else:
        picts = Pict.objects.filter(user_sendTo="").order_by('?')[:10]
        context = {
            'picts':picts,
        }
        print("TOP")
        return render(request, 'stuply_app/top.html', context)

# search_rank
def search_rank(request):
    if request.method == "POST":

        # ランキングを作る元keywordを取得
        keywords = ['dist_to_office', 'access', 'landPrice', 'park', 'flood', 'security']

        # ユーザーの価値観ポイント取得
        values = []
        for i in range(len(keywords)):
            values.append(request.POST.get(keywords[i], False))
        value_np = np.array(values, dtype=float)
        print(value_np)

        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table(dirname + '\data\score_by_station.tsv')
        
        #駅名を取得
        station_name = request.POST.get('station_name', False)
        print('station_name:' + station_name)

        # 職場の最寄り駅からの距離を計算
        score_df['dist_to_office'] = 0.0
        if station_name != '':
            if station_name not in score_df['station_name'].values:
                message = '『' + station_name + '』駅は存在しません。関東圏の駅のみが検索可能です。'
                context = {
                    'message' : message
                }
                return render(request, 'dokosumi_app/error.html', context)


            lat = score_df.loc[score_df['station_name'] == station_name, 'lat']
            lon = score_df.loc[score_df['station_name'] == station_name, 'lon']
            
            # 職場の最寄り駅と各駅の距離を計算
            score_df['dist_to_office'] = np.sqrt(pow(float(lat) - score_df['lat'], 2) + pow(float(lon) - score_df['lon'], 2))
            
            # 効用関数を適用
            ## 近い方がSCOREが高くなる
            score_np = pow(score_df['dist_to_office'].values, 0.4) * -1
            # 最大1最小0で正規化
            score_np = (score_np - score_np.min()).astype(float) / (score_np.max() - score_np.min()).astype(float)

            # DataFrameに再格納
            score_df['dist_to_office'] = score_np * 100

        # Numpyに変換
        score_np = score_df[keywords].values
        print(score_np)

        # 内積計算
        score_np = np.dot(score_np, value_np)
        print(score_np)

        # 最大1最小0で正規化
        a = (score_np - score_np.min()).astype(float)
        b = (score_np.max() - score_np.min()).astype(float)
        score_np = np.divide(a, b, out=np.zeros_like(a), where=b!=0)
        print(score_np)
        
        # DataFrameにSCORE格納
        score_df['score'] = score_np * 100
        score_df = score_df.sort_values('score', ascending=False).head(20)
        print(score_df)

        # resultRanksモデルのlistを作成
        resultRanks = []
        rank = 0
        for row_s in score_df.itertuples():
            rank += 1
            resultRank = ResultRank(\
                rank=rank, \
                station_name=row_s.station_name, \
                dist_to_office=round(float(row_s.dist_to_office)), \
                access=round(float(row_s.access)), \
                landPrice=round(float(row_s.landPrice)), \
                park=round(float(row_s.park)), \
                flood=round(float(row_s.flood)), \
                security=round(float(row_s.security)), \
                score=round(float(row_s.score)), \
            )
            resultRanks.append(resultRank)
        
        context = {
            'resultRanks' : resultRanks
        }
        return render(request, 'dokosumi_app/result_rank.html', context)

    else:
        context = {
        }
        return render(request, 'dokosumi_app/search_rank.html', context)

# 街の詳細
def town_detail(request, station_name):
    if request.method == "POST":
        return redirect('town_detail')
    else:
        # 駅名のTSVファイルを取得
        score_tsv_file = pathlib.Path('data\score_by_station.tsv')
        score_df = pd.read_table(score_tsv_file)

        town_score = score_df.loc[score_df['station_name'] == station_name]
        town_score = town_score.iloc[0]
        print(town_score)

        town_score = ResultRank(\
                rank=0, \
                station_name=town_score.station_name, \
                lat=float(town_score.lat), \
                lon=float(town_score.lon), \
                access=round(float(town_score.access)), \
                landPrice=round(float(town_score.landPrice)), \
                park=round(float(town_score.park)), \
                flood=round(float(town_score.flood)), \
                security=round(float(town_score.security)), \
                score=0.0, \
            )

        context = {
            'town_score':town_score,
        }
        return render(request, 'dokosumi_app/town_detail.html', context)