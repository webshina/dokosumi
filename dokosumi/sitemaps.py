from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['search_rank']

    def location(self, items):
        return reverse(items)