from django.conf.urls import url
from django.views.generic import TemplateView
from . import views
from .views import SearchListing
from .views import EventUpload
urlpatterns = [
    url(r'^$', views.event_list, name='event_list'),
    url(r'^'+EventUpload.base_url, EventUpload.render_page, name=EventUpload.name),
    url(r'^event_detail/', views.event_detail, name='event_detail'),
    url(r'^'+SearchListing.base_url, SearchListing.render_page, name=SearchListing.name),
    url(r'^'+EventUpload.submit_url, EventUpload.event_upload_handler, name=EventUpload.submit_view_name)
]
