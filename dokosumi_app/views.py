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
import math
import numpy as np

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

        # ユーザーの価値観ポイント取得
        value_1 = request.POST.get('value_1', False)
        print('VALUE_1: ' + str(value_1))
        value_2 = request.POST.get('value_2', False)
        print('VALUE_2: ' + str(value_2))
        value_np = np.array([value_1, value_2], dtype=float)

        # 駅名のTSVファイルを取得
        score_tsv_file = 'D:\programs\Python\Dokosumi\data\score_by_station\score_by_station.tsv'
        score_df = pd.read_table(score_tsv_file)

        # Numpyに変換
        score_np = score_df[['landPrice', 'population']].values
        print(score_np)

        # 内積計算
        score_np = np.dot(score_np, value_np)
        print(score_np)

        # DataFrameにSCORE格納
        score_df['SCORE'] = score_np
        print(score_df)

        # dictのlist
        score_list = []
        for row_s in score_df.itertuples():
            score_list.append(row_s)
        
        context = {
            'score_list' : score_list
        }
        return render(request, 'dokosumi_app/result_rank.html', context)

    else:
        context = {
        }
        return render(request, 'dokosumi_app/search_rank.html', context)