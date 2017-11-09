from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^event_upload/', views.event_upload, name='event_upload'),
]
