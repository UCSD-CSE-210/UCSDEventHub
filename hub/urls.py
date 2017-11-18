from django.conf.urls import url
from django.views.generic import TemplateView
from . import views
from .views import SearchListing
urlpatterns = [
    url(r'^$', views.event_list, name='event_list'),
    url(r'^event_upload/', views.event_upload, name='event_upload'),
    url(r'^event_detail/', views.event_detail, name='event_detail'),
    url(r'^'+SearchListing.base_url, SearchListing.render_page, name=SearchListing.name),
    url(r'^submit_event/', views.submit_event, name='submit_event'),
]
