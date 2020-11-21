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
    params_list_in_dict = urllib.parse.parse_qs(queryString)
    # エンコードされたGETパラメータはリストを含む辞書型なので、単純な辞書型に変更
    params = {}
    for key, value in params_list_in_dict.items():
        params[key] = value[0]

    # 駅名のTSVファイルを取得
    dirname = os.path.dirname(__file__)
    score_df = pd.read_table(dirname + '/data/score_by_station.tsv', dtype=str)
    
    #駅名を取得
    station_name = params.get('station_name','')
    print('station_name:' + station_name)
    # 駅名の存在チェック
    if station_name != '' and station_name not in score_df['station_name'].values:
        message = '『' + station_name + '』駅は存在しません。東京・千葉・神奈川・埼玉の駅のみが検索可能です。'
        context = {
            'message' : message
        }
        return render(request, 'dokosumi_app/error.html', context)
    
    #パートナーの駅名を取得
    partners_station_name = params.get('partners_station_name','')
    print('partners_station_name:' + partners_station_name)
    # 駅名の存在チェック
    if partners_station_name != '' and partners_station_name not in score_df['station_name'].values:
        message = '『' + partners_station_name + '』駅は存在しません。東京・千葉・神奈川・埼玉の駅のみが検索可能です。'
        context = {
            'message' : message
        }
        return render(request, 'dokosumi_app/error.html', context)

    # ランキングを作る元keyword(ユーザーの価値観ポイント)を取得
    params_only_numbers = params.copy()
    for key, value in params.items():
        if key == 'station_name' or key == 'partners_station_name':
            del params_only_numbers[key]
    
    value_np = np.array(list(params_only_numbers.values()), dtype=float)
    print(value_np)

    # 駅名のTSVファイルを取得
    dirname = os.path.dirname(__file__)
    time_df = pd.read_table(dirname + '/data/TimeToArriveByStation.tsv')

    # 通勤時間を計算
    score_df['dist_to_office'] = calc_dist_score(score_df, time_df, station_name)

    # パートナーの通勤時間を計算
    score_df['dist_to_partners_office'] = calc_dist_score(score_df, time_df, partners_station_name)

    # 物件数が少なく、住むのに向いていないであろう街を除外
    score_df = score_df.loc[score_df['livable'] != "0.0"]

    # Numpyに変換
    score_np = score_df[params_only_numbers.keys()].astype(float).values
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
        "dist_to_office":{"description":"通勤時間", "param":round(float(params.get("dist_to_office",0)))}, \
        "dist_to_partners_office":{"description":"パートナーの通勤時間", "param":round(float(params.get("dist_to_partners_office",0)))}, \
        "access":{"description":"アクセスの良さ", "param":round(float(params.get("access",0)))}, \
        "landPrice":{"description":"家賃の安さ", "param":round(float(params.get("landPrice",0)))}, \
        "park":{"description":"公園の多さ", "param":round(float(params.get("park",0)))}, \
        "flood":{"description":"浸水危険度の低さ", "param":round(float(params.get("flood",0)))}, \
        "security":{"description":"治安の良さ", "param":round(float(params.get("security",0)))}, \
        "supermarket":{"description":"買い物のしやすさ", "param":round(float(params.get("supermarket",0)))}, \
    }

    # 各街のステータスリストを作成
    resultRanks = []
    rank = 0
    for row_s in score_df.to_dict(orient='records'):
        rank += 1

        #職場の最寄り駅からの時間を取得
        if station_name != '':
            # station_name列が対象の駅名と一致する行を取得
            time_to_station = time_df[time_df['station_name'] == station_name]
            # station_name列が対象の駅名と一致する行を取得
            time_to_station = time_to_station[row_s.get('station_name',0)].astype(float).values[0]
            hh = int(time_to_station / 60)
            mm = int(time_to_station % 60)
            time_to_station = '(' + str(hh) + '時間' + str(mm) + '分' + ')'
        else:
            time_to_station = ''

        #パートナーの職場の最寄り駅からの時間を取得
        if partners_station_name != '':
            # station_name列が対象の駅名と一致する行を取得
            time_to_partners_station = time_df[time_df['station_name'] == partners_station_name]
            # station_name列が対象の駅名と一致する行を取得
            time_to_partners_station = time_to_partners_station[row_s.get('station_name',0)].astype(float).values[0]
            hh = int(time_to_partners_station / 60)
            mm = int(time_to_partners_station % 60)
            time_to_partners_station = '(' + str(hh) + '時間' + str(mm) + '分' + ')'
        else:
            time_to_partners_station = ''



        # 街のステータスを作成
        town_values_all = { \
                "dist_to_office":{"description":"通勤時間", "remarks":time_to_station, "param":round(float(row_s.get('dist_to_office',0)))}, \
                "dist_to_partners_office":{"description":"パートナーの通勤時間", "remarks":time_to_partners_station, "param":round(float(row_s.get('dist_to_partners_office',0)))}, \
                "access":{"description":"アクセスの良さ", "param":round(float(row_s.get('access',0)))}, \
                "landPrice":{"description":"家賃の安さ", "param":round(float(row_s.get('landPrice',0)))}, \
                "park":{"description":"公園の多さ", "param":round(float(row_s.get('park',0)))}, \
                "flood":{"description":"浸水危険度の低さ", "param":round(float(row_s.get('flood',0)))}, \
                "security":{"description":"治安の良さ", "param":round(float(row_s.get('security',0)))}, \
                "supermarket":{"description":"買い物のしやすさ", "param":round(float(row_s.get('supermarket',0)))}, \
        } 

        # ユーザーの価値観が0以上のパラメータのみ採用
        town_values = {}
        for key in town_values_all.keys():
            if user_values.get(key).get("param") > 0:
               town_values[key] = town_values_all[key]

        resultRank = { \
            "rank":{"description":"順位", "param":rank}, \
            "station_name":{"description":"駅名", "param":row_s.get('station_name',0)}, \
            "suumoEkiCode":{"description":"SUUMO駅コード", "param":row_s.get('SUUMOEkiCode',0)}, \
            "pref":{"description":"都道府県", "param":row_s.get('pref',0)}, \
            "lat":{"description":"緯度", "param":row_s.get('lat',0)}, \
            "lon":{"description":"経度", "param":row_s.get('lon',0)}, \
            "score":{"description":"総合スコア", "param":round(float(row_s.get('score',0)))}, \
            "values":town_values, \
        }

        resultRanks.append(resultRank)
    
    context = {
        'values' : user_values,
        'resultRanks' : resultRanks,
    }

    return render(request, 'dokosumi_app/result_rank.html', context)


# 距離の計算
def calc_dist_score(score_df, time_df, station_name):

    # 職場の最寄り駅からの距離を取得

    # 初期設定
    score_time_df = score_df
    score_time_df['time'] = 0

    if station_name != '':

        # 駅を順番通りに入れ替え
        score_time_df = pd.merge(score_df, time_df, on='station_name')
        score_time_np = score_time_df[station_name].astype(float).values
        
        # 最大1最小0で正規化
        # 時間が短いほどスコアは高くする
        score_time_np = 1 - (score_time_np - score_time_np.min()).astype(float) / (score_time_np.max() - score_time_np.min()).astype(float)

        # DataFrameに再格納
        score_time_df['time'] = score_time_np * 100

    return score_time_df['time']


# 街の詳細
def town_detail(request, station_name):
    if request.method == "POST":
        return redirect('town_detail')
    else:
        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table(dirname + '/data/score_by_station.tsv', dtype=str)

        town_score = score_df.loc[score_df['station_name'] == station_name]
        town_score = town_score.iloc[0]
        print(town_score)

        # 街のステータスを作成
        town_values = { \
            "access":{"description":"アクセスの良さ", "param":round(float(town_score.get('access',0)))}, \
            "landPrice":{"description":"家賃の安さ", "param":round(float(town_score.get('landPrice',0)))}, \
            "park":{"description":"公園の多さ", "param":round(float(town_score.get('park',0)))}, \
            "flood":{"description":"浸水危険度の低さ", "param":round(float(town_score.get('flood',0)))}, \
            "security":{"description":"治安の良さ", "param":round(float(town_score.get('security',0)))}, \
            "supermarket":{"description":"買い物のしやすさ", "param":round(float(town_score.get('supermarket',0)))}, \
        } 

        town_score = { \
            "station_name":{"description":"駅名", "param":town_score.get('station_name','')}, \
            "suumoEkiCode":{"description":"SUUMO駅コード", "param":town_score.get('SUUMOEkiCode','')}, \
            "pref":{"description":"都道府県", "param":town_score.get('pref',0)}, \
            "lat":{"description":"緯度", "param":float(town_score.get('lat',0))}, \
            "lon":{"description":"経度", "param":float(town_score.get('lon',0))}, \
            "values":town_values
        }

        context = {
            'town_score':town_score,
        }
        return render(request, 'dokosumi_app/town_detail.html', context)