from django.urls import path, include
from .views import index, video_feed, ajax

urlpatterns = [
    path('', index),
    path('video_feed', video_feed, name="video_feed"),
    path('ajax_url', ajax, name='ajax_url'),
]


