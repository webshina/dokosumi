import sys
import googlemaps
import pprint # list型やdict型を見やすくprintするライブラリ
import keys
import requests
import json
import searchPointsByKeyword
import pandas as pd
import time
import os
import xml.etree.ElementTree as ET 
import glob

# 名前空間を取得
ns = {'gml': 'http://www.opengis.net/gml/3.2', 'ksj':'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app', 'xlink':'http://www.w3.org/1999/xlink'}

# ファイル一覧を再帰的に取得
xml_list = glob.glob('D:\programs\Python\Dokosumi\data\浸水地域\A31**\A31*.xml', recursive=True)
print(xml_list)

df_all = pd.DataFrame(columns=['ID','LATLON','SCORE'])

for xml_file in xml_list:

    print('XML_FILE:' + xml_file)

    # XMLファイルを解析
    tree = ET.parse(xml_file) 

    # XMLを取得
    root = tree.getroot()

    # gml:Point以下を取得
    pointNodes = root.findall('gml:Curve', ns)

    # 座標DataFrameを作成
    df_pos = pd.DataFrame(columns=['href','LATLON'])

    # DataFrameにid,座標を追加
    for itemNode in pointNodes:
        # idを取得
        id = itemNode.attrib['{' + ns['gml'] + '}' + "id"]

        # 座標を取得
        latlon = itemNode.find('gml:segments', ns).find('gml:LineStringSegment', ns).find('gml:posList', ns).text.strip()

        # DataFrameにid,座標を追加
        df_pos_se = pd.Series([id, latlon], index=df_pos.columns)
        df_pos = df_pos.append(df_pos_se, ignore_index=True)
    
    # gml:Surface以下を取得
    surfaceNodes = root.findall('gml:Surface', ns)
    df_surface =  pd.DataFrame(columns=['ID','href'])

    # DataFrameにid,hrefを追加
    for itemNode in surfaceNodes:
        # idを取得
        id = itemNode.attrib['{' + ns['gml'] + '}' + "id"]

        # hrefを取得
        href = itemNode.find('gml:patches', ns)\
            .find('gml:PolygonPatch', ns)\
                .find('gml:exterior', ns)\
                    .find('gml:Ring', ns)\
                        .find('gml:curveMember', ns)\
                            .attrib['{' + ns['xlink'] + '}' + "href"].replace('#','')
        
        # DataFrameにid,座標を追加
        df_surface_se = pd.Series([id, href], index=df_surface.columns)
        df_surface = df_surface.append(df_surface_se, ignore_index=True)

    df_pos_surface = pd.merge(df_pos, df_surface, on='href')

    # # ksj:LandPrice以下を取得
    pointNodes = root.findall('ksj:ExpectedFloodArea', ns)

    # SCORE DataFrameを作成
    df_score = pd.DataFrame(columns=['ID','SCORE'])

    # DataFrameにid,SCOREを追加
    for itemNode in pointNodes:

        # idを取得
        id = itemNode.find('ksj:bounds', ns).attrib['{' + ns['xlink'] + '}' + "href"].replace('#','')
        # SCOREを取得
        score = itemNode.find('ksj:waterDepth', ns).text.strip()
        
        # DataFrameにid,座標を追加
        df_score_se = pd.Series([id, score], index=df_score.columns)
        df_score = df_score.append(df_score_se, ignore_index=True)

    df = pd.merge(df_pos_surface, df_score, on='ID')

    df_all = pd.concat([df_all, df], axis=0, join='inner')
    print(df_all)

print(df_all)
#結果をTSVファイルに保存
df_all.to_csv('D:\programs\Python\Dokosumi\data\score_by_latlon.tsv', index=False, sep='\t')