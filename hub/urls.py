from django.conf.urls import url
from django.views.generic import TemplateView
from hub import views
from hub.views import SearchListing, EventUpload, OrganizationPage, EventDetails, Homepage, Myevents, RSVP

urlpatterns = [
    #url(r'^$', views.event_list, name='event_list'),
    url(r'^'+Homepage.base_url,Homepage.render_page, name=Homepage.name),
    url(r'^'+EventUpload.base_url, EventUpload.render_page, name=EventUpload.name),
    url(r'^'+EventDetails.base_url, EventDetails.render_page, name=EventDetails.name),
    url(r'^'+SearchListing.base_url, SearchListing.render_page, name=SearchListing.name),
    url(r'^'+EventUpload.submit_url, EventUpload.event_upload_handler, name=EventUpload.submit_view_name),
    url(r'^login/', views.login,name='login'),
    url(r'^logout/', views.logout,name='logout'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^'+Myevents.base_url, Myevents.render_page, name=Myevents.name),
	url(r'^'+OrganizationPage.base_url, OrganizationPage.render_page, name=OrganizationPage.name),
	url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^'+RSVP.save_rsvp_base_url, RSVP.save_RSVP, name=RSVP.name),
    url(r'^'+RSVP.remove_rsvp_base_url, RSVP.remove_RSVP, name=RSVP.name),
    url(r'^permission_denied/$', TemplateView.as_view(template_name='permission_denied.html')),
]
