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
import json
import datetime
import re

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

    print("result_rank - 処理開始")

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

    # 駅から駅への所要時間のTSVファイルを取得
    time_df = pd.read_table(dirname + '/data/TimeToArriveByStation.tsv')

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

    # 各駅から職場の最寄り駅への経路情報のJSONファイルを取得
    routes_dict = {}
    print("駅から駅への経路情報のJSONファイルを取得 - 処理開始")
    if station_name != '':
        json_file = dirname + '/data/routes_stationA_to_stationB/to_' + station_name + '.json'
        with open(json_file, encoding='utf-8') as f:
            routes_dict_tmp = json.load(f)
        routes_dict.update(routes_dict_tmp)

    # 各駅からパートナーの職場の最寄り駅への経路情報のJSONファイルを取得
    print("駅から駅への経路情報のJSONファイルを取得 - 処理開始")
    if partners_station_name != '':
        json_file = dirname + '/data/routes_stationA_to_stationB/to_' + partners_station_name + '.json'
        with open(json_file, encoding='utf-8') as f:
            routes_dict_tmp = json.load(f)
        routes_dict.update(routes_dict_tmp)

    # ランキングを作る元keyword(ユーザーの価値観ポイント)を取得
    params_only_numbers = params.copy()
    for key, value in params.items():
        #駅名は数値情報ではないので削除
        if key == 'station_name' or key == 'partners_station_name':
            del params_only_numbers[key]
    
    value_np = np.array(list(params_only_numbers.values()), dtype=float)
    print("ユーザーの価値観" + str(value_np))

    # 通勤時間を計算
    score_df['dist_to_office'] = calc_dist_score(score_df, time_df, station_name)
    print("score_df['dist_to_office']:" + str(score_df['dist_to_office']))
    # パートナーの通勤時間を計算
    score_df['dist_to_partners_office'] = calc_dist_score(score_df, time_df, partners_station_name)

    # 通勤混雑度を取得
    score_df['congestion'] = calc_congestion(score_df, routes_dict, station_name)
    # パートナーの通勤混雑度を取得
    score_df['partners_congestion'] = calc_congestion(score_df, routes_dict, partners_station_name)
    
    print("score_df:" + str(score_df))

    # 物件数が少なく、住むのに向いていないであろう街を除外
    score_df = score_df[score_df['livable'] != "0.0"]
    print("score_df:" + str(score_df))

    # 駅ごとのスコアリストをNumpyに変換
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
    town_scores = []
    rank = 0
    for town_score in score_df.to_dict(orient='records'):
        rank += 1


        # 街のステータスを作成
        town_values_all = { \
            "access":{
                "description":"アクセスの良さ", 
                "remarks":{
                    "0":{
                        "description":"乗り入れ路線数",
                        "value":str(town_score.get('line_num',0)),
                        "unit":"路線",
                    },
                },
                "param":round(float(town_score.get('access',0))),
            }, \
            "landPrice":{
                "description":"家賃の安さ",  
                "remarks":{
                    "0":{
                        "description":"家賃相場(ワンルーム)",
                        "value":str(town_score.get('rent_oneRoom',0)),
                        "unit":"万円",
                    },
                    "1":{
                        "description":"家賃相場(1K)",
                        "value":str(town_score.get('rent_1K',0)),
                        "unit":"万円",
                    },
                    "2":{
                        "description":"家賃相場(1LDK)",
                        "value":str(town_score.get('rent_1LDK',0)),
                        "unit":"万円",
                    },
                    "3":{
                        "description":"家賃相場(2LDK)",
                        "value":str(town_score.get('rent_2LDK',0)),
                        "unit":"万円",
                    },
                    "4":{
                        "description":"家賃相場(3LDK)",
                        "value":str(town_score.get('rent_3LDK',0)),
                        "unit":"万円",
                    },
                },
                "param":round(float(town_score.get('landPrice',0))),
            }, \
            "park":{
                "description":"公園の多さ",  
                "remarks":{

                },
                "param":round(float(town_score.get('park',0))),
            }, \
            "flood":{
                "description":"浸水危険度の低さ", 
                "remarks":{
                    
                }, 
                "param":round(float(town_score.get('flood',0))),
            }, \
            "security":{
                "description":"治安の良さ", 
                "remarks":{
                    "0":{
                        "description":"駅周辺のパチンコ店",
                        "value":str(town_score.get('pachinko',0)),
                        "unit":"店舗",
                    },
                    "1":{
                        "description":"駅周辺の風俗店",
                        "value":str(town_score.get('sexShop',0)),
                        "unit":"店舗",
                    },
                }, 
                "param":round(float(town_score.get('security',0))),
            }, \
            "supermarket":{
                "description":"買い物のしやすさ", 
                "remarks":{
                    "0":{
                        "description":"駅周辺の食料品店",
                        "value":str(town_score.get('supermarket_num',0)),
                        "unit":"店舗",
                    },
                }, 
                "param":round(float(town_score.get('supermarket',0))),
            }, \
        } 

        # ユーザーの価値観が0以上のパラメータのみ採用
        town_values = {}
        for key in town_values_all.keys():
            # ユーザーの価値観が0以上のパラメータおよび通勤経路情報を取得
            if user_values.get(key).get("param") > 0:
               town_values[key] = town_values_all[key]
        

        #職場の最寄り駅が設定されていれば、通勤系の情報を追加
        if station_name != '':
            # 職場の最寄り駅への時間を取得
            # station_name列が対象の駅名と一致する行を取得
            time_to_station = time_df[time_df['station_name'] == station_name]
            # station_name列が対象の駅名と一致する行を取得
            time_to_station = time_to_station[town_score.get('station_name',0)].astype(float).values[0]
            hh = int(time_to_station / 60)
            mm = int(time_to_station % 60)
            time_to_station = '約' + str(hh) + '時間' + str(mm) + '分'

            # 職場の最寄り駅への経路情報を取得
            route_dict = routes_dict.get(str(town_score.get('station_name',0))+'_'+str(station_name), '')

            # テンプレートに渡す情報を格納
            town_values["commutingRoot"] = {
                "description":"通勤経路情報", 
                "remarks":route_dict,
            }

            town_values["dist_to_office"] = {
                "description":"通勤時間", 
                "remarks":{
                    "0":{
                        "description":"通勤時間(乗り換え時間含む)",
                        "value":time_to_station,
                        "unit":"",
                    },
                },
                "param":round(float(town_score.get('dist_to_office',0))),
            }
            
            town_values["congestion"] = {
                "description":"通勤混雑度の低さ", 
                "remarks":{
                },
                "param":round(float(town_score.get('congestion',0))),
            }
            

        #パートナーの職場の最寄り駅が設定されていれば、通勤系の情報を追加
        if partners_station_name != '':
            # station_name列が対象の駅名と一致する行を取得
            time_to_partners_station = time_df[time_df['station_name'] == partners_station_name]
            # station_name列が対象の駅名と一致する行を取得
            time_to_partners_station = time_to_partners_station[town_score.get('station_name',0)].astype(float).values[0]
            hh = int(time_to_partners_station / 60)
            mm = int(time_to_partners_station % 60)
            time_to_partners_station = '約' + str(hh) + '時間' + str(mm) + '分'

            # 職場の最寄り駅への経路情報を取得
            partners_route_dict = routes_dict.get(str(town_score.get('station_name',0))+'_'+str(partners_station_name), '')
            
            # テンプレートに渡す情報を格納
            town_values["partners_commutingRoot"] = {
                "description":"パートナーの通勤経路情報", 
                "remarks":route_dict,
            }
            
            town_values["dist_to_partners_office"] = {
                "description":"パートナーの通勤時間", 
                "remarks":{
                    "0":{
                        "description":"パートナーの通勤時間(乗り換え時間含む)",
                        "value":time_to_partners_station,
                        "unit":"",
                    },
                },
                "param":round(float(town_score.get('dist_to_partners_office',0))),
            }
            
            town_values["partners_congestion"] = {
                "description":"パートナーの通勤混雑度の低さ", 
                "remarks":{
                },
                "param":round(float(town_score.get('partners_congestion',0))),
            }

        # 街の属性情報を作成
        town_score = { \
            "rank":{"description":"順位", "param":rank}, \
            "station_name":{"description":"駅名", "param":town_score.get('station_name',0)}, \
            "suumoEkiCode":{"description":"SUUMO駅コード", "param":town_score.get('suumoEkiCode',0)}, \
            "pref":{"description":"都道府県", "param":town_score.get('pref',0)}, \
            "lat":{"description":"緯度", "param":town_score.get('lat',0)}, \
            "lon":{"description":"経度", "param":town_score.get('lon',0)}, \
            "score":{"description":"総合スコア", "param":round(float(town_score.get('score',0)))}, \
            "values":town_values, \
        }

        town_scores.append(town_score)
    
    context = {
        'values' : user_values,
        'town_scores' : town_scores,
    }

    return render(request, 'dokosumi_app/result_rank.html', context)


# 職場の最寄り駅への通勤時間の取得
def calc_dist_score(score_df, time_df, station_name):

    # 初期設定
    score_time_df = score_df
    score_time_df['time'] = 0

    if station_name != '':

        # 駅を順番通りに入れ替え
        score_time_df = pd.merge(score_df, time_df, on='station_name')
        score_time_np = score_time_df[station_name].astype(float).values
        
        # 最大1最小0で正規化
        score_time_np = (score_time_np - score_time_np.min()).astype(float) / (score_time_np.max() - score_time_np.min()).astype(float)
        # 効用関数を適用
        score_time_np = score_time_np ** (1/1.5)
        # 時間が短いほどスコアは高くする
        score_time_np = 1 - score_time_np

        # DataFrameに再格納
        score_time_df['time'] = score_time_np * 100

    return score_time_df['time']
    


# 通勤混雑度を取得
def calc_congestion(score_df, routes_dict, station_name):

    # 初期設定
    score_congestion_df = score_df
    score_congestion_df['congestion'] = 0.5

    if station_name != '':

        # 各駅の混雑度を計算
        for stationA in score_congestion_df["station_name"]:
            print("各駅から職場の最寄り駅への経路取得：" + stationA + "から" + station_name)

            if stationA != station_name:
                
                #各駅から職場の最寄り駅への経路情報取得
                route_dict = routes_dict.get(stationA + '_' + station_name, '')

                if route_dict != '':
                    #経路情報から合計乗車時間・乗車時間*混雑度を取得
                    times = []
                    time_congestions = []
                    for value in route_dict.values():
                        if value.get("route_block","") == 1:
                            #時間のフォーマット変換 分単位に直す
                            time = value.get('time', 0)
                            
                            #時間を取得
                            hh = re.match(r'(.*?)時間.*', time)
                            if hh != None:
                                hh = float(hh.group(1))
                            else:
                                hh = 0.0
                            
                            #分を取得
                            mm = re.match(r'.*時間(.*?)分.*', time)
                            if mm != None:
                                mm = float(mm.group(1))
                            else:
                                mm = re.match(r'(.*?)分.*', time)
                                if mm != None:
                                    mm = float(mm.group(1))
                                else:
                                    mm = 0.0
                            
                            #分単位に換算
                            time = hh * 60 + mm

                            #混雑度を数値に変換
                            congestion = value.get("congestion","")
                            if congestion == "余裕で座れる":
                                congestion_score = 1.0
                            elif congestion == "席はいっぱい":
                                congestion_score = 0.3
                            elif congestion == "普通に立てる":
                                congestion_score = 0.5
                            elif congestion == "圧迫される":
                                congestion_score = 0.7
                            elif congestion == "身動き不可":
                                congestion_score = 0.8
                            elif congestion == "乗れない":
                                congestion_score = 0.0
                            else:
                                congestion_score = 0.5

                            #合計乗車時間・乗車時間*混雑度を取得
                            times.append(time)
                            time_congestions.append(time * congestion_score)

                        else:
                            continue
                    
                    #平均混雑度を取得
                    if sum(times) != 0:
                        congestion_avg = sum(time_congestions) / sum(times)
                    else:
                        congestion_avg = 1
                    
                    # DataFrameのアップデート
                    score_congestion_df['congestion'].loc[score_congestion_df['station_name'] == stationA] = congestion_avg * 100
                else:
                    continue
            else:
                score_congestion_df['congestion'].loc[score_congestion_df['station_name'] == stationA] = 100

    return score_congestion_df['congestion']


# 通勤混雑度を文字列に変換
def congestion_to_remark(congestion):

    if congestion == 1:
        congestion_remark = "座って通勤可能"
    elif congestion == 2:
        congestion_remark = "席はいっぱい"
    elif congestion == 3:
        congestion_remark = "立って通勤"
    elif congestion == 4:
        congestion_remark = "周りから押される"
    elif congestion == 5:
        congestion_remark = "すし詰め状態"
    else:
        congestion_remark = "乗れない"
    
    return congestion_remark



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
            "access":{
                "description":"アクセスの良さ", 
                "remarks":{
                    "0":{
                        "description":"乗り入れ路線数",
                        "value":str(town_score.get('line_num',0)),
                        "unit":"路線",
                    },
                },
                "param":round(float(town_score.get('access',0))),
            }, \
            "landPrice":{
                "description":"家賃の安さ",  
                "remarks":{
                    "0":{
                        "description":"家賃相場(ワンルーム)",
                        "value":str(town_score.get('rent_oneRoom',0)),
                        "unit":"万円",
                    },
                    "1":{
                        "description":"家賃相場(1K)",
                        "value":str(town_score.get('rent_1K',0)),
                        "unit":"万円",
                    },
                    "2":{
                        "description":"家賃相場(1LDK)",
                        "value":str(town_score.get('rent_1LDK',0)),
                        "unit":"万円",
                    },
                    "3":{
                        "description":"家賃相場(2LDK)",
                        "value":str(town_score.get('rent_2LDK',0)),
                        "unit":"万円",
                    },
                    "4":{
                        "description":"家賃相場(3LDK)",
                        "value":str(town_score.get('rent_3LDK',0)),
                        "unit":"万円",
                    },
                },
                "param":round(float(town_score.get('landPrice',0))),
            }, \
            "park":{
                "description":"公園の多さ",  
                "remarks":{
                    "0":{
                        "description":"駅周辺の総公園面積",
                        "value":str(town_score.get('park_area',0)),
                        "unit":"㎡",
                    },
                },
                "param":round(float(town_score.get('park',0))),
            }, \
            "flood":{
                "description":"浸水危険度の低さ", 
                "remarks":{
                    "0":{
                        "description":"駅周辺の最大浸水深",
                        "value":str(town_score.get('water_depth',0)),
                        "unit":"m",
                    },
                }, 
                "param":round(float(town_score.get('flood',0))),
            }, \
            "security":{
                "description":"治安の良さ", 
                "remarks":{
                    "0":{
                        "description":"駅周辺のパチンコ店",
                        "value":str(town_score.get('pachinko',0)),
                        "unit":"店舗",
                    },
                    "1":{
                        "description":"駅周辺の風俗店",
                        "value":str(town_score.get('sexShop',0)),
                        "unit":"店舗",
                    },
                }, 
                "param":round(float(town_score.get('security',0))),
            }, \
            "supermarket":{
                "description":"買い物のしやすさ", 
                "remarks":{
                    "0":{
                        "description":"駅周辺の食料品店",
                        "value":str(town_score.get('supermarket_num',0)),
                        "unit":"店舗",
                    },
                }, 
                "param":round(float(town_score.get('supermarket',0))),
            }, \
        } 

        town_score = { \
            "station_name":{"description":"駅名", "param":town_score.get('station_name','')}, \
            "comment":{"description":"コメント", "param":str(town_score.get('comment','')).replace('nan','この街へのコメント募集中！Twitterボタンからこの街へのコメントをTweetしてください')}, \
            "pref":{"description":"都道府県", "param":town_score.get('pref',0)}, \
            "suumoEkiCode":{"description":"SUUMO駅コード", "param":town_score.get('suumoEkiCode',0)}, \
            "lat":{"description":"緯度", "param":float(town_score.get('lat',0))}, \
            "lon":{"description":"経度", "param":float(town_score.get('lon',0))}, \
            "values":town_values
        }

        context = {
            'town_score':town_score,
        }
        return render(request, 'dokosumi_app/town_detail.html', context)