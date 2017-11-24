from django.shortcuts import render
from .models import Event,OrganizationDetails, UserProfile
from .apis import add_event_to_db,event_details
from .apis import search_events
from .apis import upcoming_events
from django.http import HttpResponse
from django.utils import dateparse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import re

import json
from django.http import HttpResponse
# Create your views here.

class Utils():

	@staticmethod
	def format_day(date):
		return date.strftime("%a, %b %d")

	@staticmethod
	def format_time(date):
		return date.strftime("%I:%M %p")

	@staticmethod
	def format_date(date):
		return Utils.format_day(date)+" "+Utils.format_time(date)

	@staticmethod
	def get_image_url(image):
		return Constants.media_path+image

	@staticmethod
	def get_alert_html(text,alerttype):
		div=""
		if alerttype == 'fail':
			div = '<div id="valErr" class="row viewerror clearfix">\n'
			div = div + '   <div class="alert alert-danger">'+text+'</div>\n'
			div = div+'</div>'
		else:
			div = '<div id="valErr" class="row viewerror clearfix">\n'
			div = div + '   <div class="alert alert-success">'+text+'</div>\n'
			div = div+'</div>'
		return div


class Constants():
	app_name="hub"
	media_path="/media/"


def event_list(request):
    events=upcoming_events()#.sort(key=lambda e: e.date)[:3]
    for event in events:
        event["image_url"] = Utils.get_image_url(event["image"])
        event["start_date"] = event["start_date"].strftime("%a, %b %d, %I:%M %p")
        event["event_url"]= EventDetails.get_url(event["id"])
    return render(request, 'hub/Homepage.html', {'events':events})

class EventDetails():
	name = "event_details"
	base_url = "event_details/"
	template = Constants.app_name+"/event_details.html"
	
	
	def __init__(self, request):
		self.request = request
	def _render_me(self):
		return render(self.request, EventDetails.template, {'event':self.event})
		
	def _get_event_details(self,eventId):
		evntId = int(eventId)
		events = event_details(evntId)
		event = events[0]
		event["googleDate"] = event["start_date"].strftime("%Y%m%dT%H%M%S")+"/"+event["end_date"].strftime("%Y%m%dT%H%M%S")
		event["start_day"] = event["start_date"].strftime("%a, %b %d")
		event["start_time"] = event["start_date"].strftime("%I:%M %p")
		event["image_url"] = Utils.get_image_url(event["image"])
		event["organizer_url"] = OrganizationPage.get_url(1)
			
		return event
	def render(self):
		eventId = self.request.GET.get("id")
		print("event_id",eventId)
		self.event = self._get_event_details(eventId)
		return self._render_me()
		
	@staticmethod
	def render_page(request):
		m = EventDetails(request)
		return m.render()
		
	@staticmethod
	def get_url(id):
		return "/"+EventDetails.base_url +"?id="+str(id)

class EventUpload():
	name = "event_upload_form"
	base_url = "event_upload/"
	submit_url = "submit_event/"
	submit_view_name = "submit_event"
	template = Constants.app_name+"/event_upload.html"

	# Event Upload related views
	def _get_alert_html(self,text,alerttype):
		div=""
		if alerttype == 'fail':
			div = '<div id="valErr" class="row viewerror clearfix">\n'
			div = div + '   <div class="alert alert-danger">'+text+'</div>\n'
			div = div+'</div>'
		else:
			div = '<div id="valErr" class="row viewerror clearfix">\n'
			div = div + '   <div class="alert alert-success">'+text+'</div>\n'
			div = div+'</div>'
		return div

	def _render_event_upload(self,request):
		return render(request, self.template, {'div_elem': " "})

	def _submit_event(self,request):
		data = request.POST.items()
		for key, value in data:
			print("%s %s" % (key, value))

		# Build the events
		new_event = Event()
		new_event.title = request.POST.get('n_title',"")
		new_event.contact_email = request.POST.get('n_email',"")
		new_event.organizer = request.POST.get('n_org',"")
		new_event.location = request.POST.get('n_loc',"")
		new_event.description = request.POST.get('n_title',"n_desc")
		startdate_object = datetime.strptime(request.POST.get('n_startdate'),'%m/%d/%Y %I:%M %p')
		enddate_object = datetime.strptime(request.POST.get('n_enddate'),'%m/%d/%Y %I:%M %p')
		new_event.start_date = startdate_object
		new_event.end_date = enddate_object
		uploaded_poster = request.FILES['n_uploadedposter']
		new_event.image = uploaded_poster
		new_event.hashtags = request.POST.get('n_tags')
		add_event_to_db(new_event)
		return render(request, 'hub/event_upload.html', {'div_elem':self._get_alert_html('Event Upload is Successful','sucess')})

	@staticmethod
	def render_page(request):
		module = EventUpload()
		return module._render_event_upload(request)

	@staticmethod
	def event_upload_handler(request):
		module = EventUpload()
		return module._submit_event(request)


class SearchListing():
	name = "search_page"
	base_url = "event_search/"
	template = Constants.app_name+"/search_page.html"
		
	class Response():
		def __init__(self):
			self.events = []
			self.empty_search = True
		
	def __init__(self, request):
		self.response = SearchListing.Response()
		self.request = request
		
	def _get_keywords(self):
		return self.request.GET.get("q")
	
	def _clean_search_keywords(self, key):
		key = re.sub(' ', '-', key)
		key = re.sub('[^A-Za-z0-9-]', '', key)
		key = re.sub('-+',' ', key)
		return key
	
	def _generate_repsonse(self, events):
		
		for event in events:
			event["start_day"] = Utils.format_day(event["start_date"])
			event["end_day"] = Utils.format_day(event["end_date"])
			event["start_time"] = Utils.format_time(event["start_date"])
			event["end_time"] = Utils.format_time(event["end_date"])
			event["organizer_url"] = OrganizationPage.get_url(1)
			if event["start_day"] == event["end_day"]:
				event["ending_same_day"]=True
			else:
				event["ending_same_day"]=False
			event["image_url"] = Utils.get_image_url(event["image"])
			event["event_url"] = EventDetails.get_url(event["id"])
		self.response.empty_search = False
		self.response.events = events
	
	def _render_me(self):
		return render(self.request, SearchListing.template, 
								{"events":self.response.events, 
								"empty_search":self.response.empty_search}
								)
								
	
	def render(self):
		search_keywords = self._get_keywords()
		
		if not search_keywords:
			return self._render_me()
		
		search_keywords = self._clean_search_keywords(search_keywords)
		
		events = search_events(search_keywords)
		
		self._generate_repsonse(events)
		
		return self._render_me()

	@staticmethod
	def render_page(request):
		module = SearchListing(request)
		return module.render()
	
	def get_url(self, keywords):
		return "/"+SearchListing.base_url+"?q="+keywords

def get_event_details(id):
	return OrganizationDetails() 
	
class OrganizationPage():
	name = "Organization"
	base_url = "organizer/"
	template = Constants.app_name+"/org_details.html"
	
	class Response():
		def __init__(self):
			self.org_details = None
		
	def __init__(self, request):
		self.request = request
		self.response = OrganizationPage.Response()
		
	def _get_id(self):
		return self.request.GET.get("id")
	
	def _render_me(self):
		dummy = {
			"name":"GSA@UCSD",
			"description": "GSA is graduate student body",
			"id":1,
			"phone":"1234221234",
			"address": "Somewhere, at, UCSD",
			"image": Utils.get_image_url("events/Halloween-Hero-1-A.jpeg"),
			"email":"gsa@ucsd.com"
		}
		return render(self.request, OrganizationPage.template, 
								{"organizer": dummy}
								)
	
	def render(self):
		id = self._get_id()
		organizer = get_event_details(id)
		self.response.org_details = organizer
		return self._render_me()
		
	@staticmethod
	def render_page(request):
		module = OrganizationPage(request)
		return module.render()

	@staticmethod
	def get_url(id):
		return "/"+OrganizationPage.base_url+"?id="+str(id)


def login(request):
	if(request.method == "POST"):
		user_name = request.POST['n_username']
		password = request.POST['n_password']
		user = authenticate(request, username=user_name, password=password)
		if user is not None:
			return HttpResponse("<h1>dsa</h1>")
		else:
			return render(request, 'hub/login.html', {})
	else:
		return render(request, 'hub/login.html', {})

def signup(request):
	if(request.method == "POST"):
		user_name = request.POST.get('n_user_name',"")
		if user_name != "":
			#This request is for new user
			password = request.POST.get('n_user_password',"")
			email = request.POST.get('n_user_email',"")
			new_django_user = User.objects.create_user(user_name, email, password)
			new_custom_user = UserProfile()
			new_custom_user.user = new_django_user
			new_custom_user.user_is_organization = False
			new_custom_user.user_image = request.FILES['n_user_img']
			new_custom_user.user_first_name = request.POST.get('n_user_fn',"")
			new_custom_user.user_last_name = request.POST.get('n_user_ln',"")
			new_custom_user.user_email = request.POST.get('n_user_email',"")
			new_custom_user.save()
			return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('New User Registration Sucessful, Please Login','sucess')})
		else:
			#This request is for new org
			user_name = request.POST.get('n_org_uname',"")
			password = request.POST.get('n_org_password',"")
			email = request.POST.get('n_org_email',"")
			new_django_user = User.objects.create_user(user_name, email, password)
			new_org = OrganizationDetails()
			new_org.user = new_django_user
			new_org.description = request.POST.get("n_org_desc","")
			new_org.contact_first_name = request.POST.get("n_org_poc_fn","")
			new_org.contact_last_name = request.POST.get("n_org_poc_ln","")
			new_org.contact_email = request.POST.get("n_org_poc_email","")
			new_org.contact_number = request.POST.get("n_org_poc_phone","")
			new_org.org_image = request.FILES['n_org_img']
			new_org.address = (request.POST.get("n_org_addr","")+'\n' +
				request.POST.get("n_org_city","") + '\n' +
				request.POST.get("n_org_state","") + '\n' +
				request.POST.get("n_org_zip",""))
			new_org.save()
			return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('New Organization Registration Sucessful, Please Login','sucess')})
	else:
		return render(request, 'hub/signup.html', {})

#@login_required
def myevents(request):
	#dummy content until APIs for rsvp retreival are written
	events=upcoming_events()#.sort(key=lambda e: e.date)[:3]
	for event in events:
		event["image_url"] = "/media/" + event["image"]
		event["start_date"] = event["start_date"].strftime("%a, %b %d, %I:%M %p")
	return render(request, 'hub/my_events.html', {'events':events})
