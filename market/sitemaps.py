from django.contrib.sitemaps import Sitemap
from .models import Tile
class TileSitemap(Sitemap):
    changefreq='daily'; priority=0.8
    def items(self): return Tile.objects.filter(status='published')
    def lastmod(self,obj): return obj.updated_at
