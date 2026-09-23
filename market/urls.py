from django.urls import path
from . import views
urlpatterns=[
path('',views.home,name='home'),path('tiles/',views.catalog,name='catalog'),path('tiles/<slug:slug>/',views.tile_detail,name='tile_detail'),
path('register/',views.register,name='register'),path('login/',views.login_view,name='login'),path('logout/',views.logout_view,name='logout'),
path('sell/',views.create_tile,name='create_tile'),path('sell/<int:pk>/media/',views.tile_media,name='tile_media'),path('sell/<int:pk>/edit/',views.edit_tile,name='edit_tile'),
path('dashboard/',views.dashboard,name='dashboard'),path('profile/',views.profile,name='profile'),path('tile/<int:pk>/like/',views.like_tile,name='like_tile'),path('tile/<int:pk>/favorite/',views.favorite_tile,name='favorite_tile'),
path('tile/<int:pk>/comment/',views.comment_tile,name='comment_tile'),path('tile/<int:pk>/question/',views.question_tile,name='question_tile'),path('tile/<int:pk>/inquiry/',views.inquiry_tile,name='inquiry_tile'),
path('tile/<int:pk>/message/',views.start_conversation,name='start_conversation'),path('messages/',views.inbox,name='inbox'),path('messages/<int:pk>/',views.conversation,name='conversation'),path('notifications/',views.notifications,name='notifications'),path('search/save/',views.save_search,name='save_search'),path('robots.txt',views.robots,name='robots')]
