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
        return redirect('top')

# search_rank
def search_rank(request):
        context = {}
        return render(request, 'dokosumi_app/search_rank.html', context)


# 住みよい街ランキング表示
def result_rank(request):

    # エンコードされたGETパラメータを取得
    queryString = urllib.parse.unquote(request.META['QUERY_STRING'])
    params = urllib.parse.parse_qs(queryString)

    # 駅名のTSVファイルを取得
    dirname = os.path.dirname(__file__)
    score_df = pd.read_table(dirname + '/data/score_by_station.tsv')
    
    #駅名を取得
    station_name = params.get('station_name',[''])[0]
    print('station_name:' + station_name)
    # 駅名の存在チェック
    if station_name != '' and station_name not in score_df['station_name'].values:
        message = '『' + station_name + '』駅は存在しません。東京・千葉・神奈川・埼玉の駅のみが検索可能です。'
        context = {
            'message' : message
        }
        return render(request, 'dokosumi_app/error.html', context)
    
    #パートナーの駅名を取得
    partners_station_name = params.get('partners_station_name',[''])[0]
    print('partners_station_name:' + partners_station_name)
    # 駅名の存在チェック
    if partners_station_name != '' and partners_station_name not in score_df['station_name'].values:
        message = '『' + partners_station_name + '』駅は存在しません。東京・千葉・神奈川・埼玉の駅のみが検索可能です。'
        context = {
            'message' : message
        }
        return render(request, 'dokosumi_app/error.html', context)

    # ランキングを作る元keywordを取得
    keywords = ['dist_to_office', 'dist_to_partners_office', 'access', 'landPrice', 'park', 'flood', 'security']

    # ユーザーの価値観ポイント取得
    values = []
    for i in range(len(keywords)):
        values.append(params[keywords[i]][0])
    value_np = np.array(values, dtype=float)
    print(value_np)

    # 職場からの距離を計算
    score_df['dist_to_office'] = calc_dist_score(station_name)

    # パートナーの職場からの距離を計算
    score_df['dist_to_partners_office'] = calc_dist_score(partners_station_name)

    # 物件数が少なく、住むのに向いていないであろう街を除外
    score_df = score_df.loc[score_df['livable'] != 0.0]

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

    # ユーザーの価値観ポイント取得
    user_values = {\
        "dist_to_office":{"description":"職場からの距離", "param":round(float(params["dist_to_office"][0]))}, \
        "dist_to_partners_office":{"description":"パートナーの職場からの距離", "param":round(float(params["dist_to_partners_office"][0]))}, \
        "access":{"description":"交通利便性", "param":round(float(params["access"][0]))}, \
        "landPrice":{"description":"家賃の安さ", "param":round(float(params["landPrice"][0]))}, \
        "park":{"description":"公園の多さ", "param":round(float(params["park"][0]))}, \
        "flood":{"description":"浸水危険度の低さ", "param":round(float(params["flood"][0]))}, \
        "security":{"description":"治安の良さ", "param":round(float(params["security"][0]))}, \
    }

    # 各街のステータスリストを作成
    resultRanks = []
    rank = 0
    for row_s in score_df.itertuples():
        rank += 1

        # 街のステータスを作成
        town_values_all = { \
                "dist_to_office":{"description":"職場からの距離", "param":round(float(row_s.dist_to_office))}, \
                "dist_to_partners_office":{"description":"パートナーの職場からの距離", "param":round(float(row_s.dist_to_partners_office))}, \
                "access":{"description":"交通利便性", "param":round(float(row_s.access))}, \
                "landPrice":{"description":"家賃の安さ", "param":round(float(row_s.landPrice))}, \
                "park":{"description":"公園の多さ", "param":round(float(row_s.park))}, \
                "flood":{"description":"浸水危険度の低さ", "param":round(float(row_s.flood))}, \
                "security":{"description":"治安の良さ", "param":round(float(row_s.security))}, \
        } 

        # ユーザーの価値観が0以上のパラメータのみ採用
        town_values = {}
        for key in town_values_all.keys():
            if user_values.get(key).get("param") > 0:
               town_values[key] = town_values_all[key]

        resultRank = { \
            "rank":{"description":"順位", "param":rank}, \
            "station_name":{"description":"駅名", "param":row_s.station_name}, \
            "lat":{"description":"緯度", "param":row_s.lat}, \
            "lon":{"description":"経度", "param":row_s.lon}, \
            "score":{"description":"総合スコア", "param":round(float(row_s.score))}, \
            "values":town_values, \
        }

        resultRanks.append(resultRank)
    
    context = {
        'values' : user_values,
        'resultRanks' : resultRanks,
    }
    return render(request, 'dokosumi_app/result_rank.html', context)


# 距離の計算
def calc_dist_score(station_name):

    # 駅名のTSVファイルを取得
    dirname = os.path.dirname(__file__)
    score_df = pd.read_table(dirname + '/data/score_by_station.tsv')

    # 職場の最寄り駅からの距離を計算
    score_df['dist_to_office'] = 0.0
    if station_name != '':

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

    return score_df['dist_to_office']


# 街の詳細
def town_detail(request, station_name):
    if request.method == "POST":
        return redirect('town_detail')
    else:
        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table(dirname + '/data/score_by_station.tsv')

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