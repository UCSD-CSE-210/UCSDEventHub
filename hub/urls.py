from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.event_list, name='event_list'),
    url(r'^event_upload/', views.event_upload, name='event_upload'),
    url(r'^event_detail/', views.event_detail, name='event_detail'),
    url(r'^search/', views.render_search_page, name="search_page"),
    url(r'^submit_event/', views.submit_event, name='submit_event')
]
