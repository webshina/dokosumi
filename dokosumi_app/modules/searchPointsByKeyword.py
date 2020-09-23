import sys
import googlemaps
import pprint # list型やdict型を見やすくprintするライブラリ
import keys
import requests
import json 
import time

class SearchPointsByKeyword:
    def __init__(self):
        sample = ''

    def searchPointsByKeyword(self,longitude,latitude,radius,keyword):
        key = str(keys.google_api_key)
        client = googlemaps.Client(key) #インスタンス生成

        result_set = []
        next_page_token = 0
        while next_page_token != -1 :

            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
            url = url \
                +  "location=" + str(longitude) + ',' + str(latitude) \
                +  "&radius=" + str(radius) \
                +  "&keyword=" + keyword \
                +  "&key=" + key

            #つぎのページがあればpagetokenを付与
            if next_page_token != 0:
                url = url + "&pagetoken=" + next_page_token

            #リクエストを送信して結果を取得
            print('GET : ' + url)
            r = requests.get(url)
            result = r.json()['results']
            result_set.extend(result)

            #20件以上結果がある場合、次の20件を取得
            if 'next_page_token' in r.json():
                next_page_token = r.json()['next_page_token']
                time.sleep(2)
            #次の20件がなければブレーク
            else:
                next_page_token = -1

        #結果リストを返す
        return result_set