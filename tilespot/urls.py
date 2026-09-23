from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from market.sitemaps import TileSitemap
from market import views
urlpatterns=[path('admin/',admin.site.urls),path('',include('market.urls')),path('sitemap.xml',sitemap,{'sitemaps':{'tiles':TileSitemap}}),path('robots.txt',views.robots,name='robots')]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
