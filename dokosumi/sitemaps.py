from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.shortcuts import resolve_url
import pandas as pd
import os

class TopPageSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['search_rank']

    def location(self, item):
        return reverse('search_rank')

class StaticViewSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "daily"
    priority = 1.0

    def items(self):
        # 駅名のTSVファイルを取得
        dirname = os.path.dirname(__file__)
        score_df = pd.read_table(dirname + '/../dokosumi_app/data/score_by_station.tsv')
        stations = score_df['station_name'].values.tolist()
        return stations

    def location(self, item):
        return reverse('town_detail', kwargs={'station_name':item})