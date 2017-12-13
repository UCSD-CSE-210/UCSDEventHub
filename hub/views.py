from django.shortcuts import render,redirect
from hub.models import Event,OrganizationDetails, UserProfile
from hub.models import Category
from hub.apis import add_event_to_db,event_details
from hub.apis import search_events
from hub.apis import upcoming_events, upcoming_events_by_org
from hub.apis import check_user_name
from hub.apis import user_event_rsvpd
from hub.apis import save_rsvp
from hub.apis import remove_rsvp
from hub.apis import get_rsvp_events
from hub.apis import is_user_attendee
from hub.apis import get_organization_id, get_org_details
from hub.apis import get_organization_name
from hub.apis import get_categories
from django.http import HttpResponse
from django.utils import dateparse
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.contrib.auth.models import User
import re
import json
from django.http import HttpResponse
from django.db.utils import IntegrityError
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


class Homepage():
	base_url = "$"
	template = Constants.app_name+"/Homepage.html"
	name ='event_list'

	def __init__(self, request):
		self.request = request
		user = request.user
		self.user_attendee = is_user_attendee(user)
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(user.username)
		else:
			self.org_id=None

	def _render_me(self):
		return render(self.request, Homepage.template, {'events':self.events, 'is_user_attendee': self.user_attendee, 'org_id': self.org_id, "categories":Category.objects.all()} )

	def event_list(self):
		user = self.request.user
		events=upcoming_events()
		for event in events:
			event["image_url"] = Utils.get_image_url(event["image"])
			event["start_date"] = event["start_date"].strftime("%a, %b %d, %I:%M %p")
			event["event_url"]= EventDetails.get_url(event["id"])
		return events
		#return render(request, 'hub/Homepage.html', {'events':events})

	def render(self):
		self.events = self.event_list()
		return self._render_me()

	@staticmethod
	def render_page(request):
		m = Homepage(request)
		return m.render()

	@staticmethod
	def get_url(id):
		return "/"+EventDetails.base_url +"?id="+str(id)

class EventDetails():
	name = "event_details"
	base_url = "event_details/"
	template = Constants.app_name+"/event_details.html"
	def __init__(self, request):
		self.request = request
		self.user_attendee = is_user_attendee(request.user)
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(request.user.username)
		else:
			self.org_id=None

	def _render_me(self):
		return render(
			self.request, EventDetails.template, {'event':self.event, 'is_user_attendee': self.user_attendee, 'org_id': self.org_id,"categories":Category.objects.all()})

	def _get_event_details(self,eventId):
		evntId = int(eventId)
		events = event_details(evntId)
		event = events[0]
		event["googleDate"] = event["start_date"].strftime("%Y%m%dT%H%M%S")+"/"+event["end_date"].strftime("%Y%m%dT%H%M%S")
		event["start_day"] = Utils.format_day(event["start_date"])
		event["end_day"] = Utils.format_day(event["end_date"])
		event["start_time"] = Utils.format_time(event["start_date"])
		event["end_time"] = Utils.format_time(event["end_date"])
		if event["start_day"] == event["end_day"]:
			event["ending_same_day"]=True
		else:
			event["ending_same_day"]=False
		event["image_url"] = Utils.get_image_url(event["image"])
		event["organizer_url"] = OrganizationPage.get_url(event["org_id"])
		event["org_name"] = get_organization_name(event["org_id"])
		event["rsvpd"] = self._get_rsvp_info(eventId)
		event["user"] = self.request.user
		event["categories"] = event["categories"]
		return event

	def _get_rsvp_info(self, eventId):
		user = self.request.user
		if user.is_authenticated:
			return user_event_rsvpd(user.id, eventId)
		else:
			return False

	def render(self):
		eventId = self.request.GET.get("id")
		# print("event_id",eventId)
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

	def __init__(self, request):
		self.request = request
		self.user_attendee = is_user_attendee(request.user)
		self.categories = Category.objects.all()
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(request.user.username)
		else:
			self.org_id=None

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
		if request.user.is_authenticated and not self.user_attendee:
			return render(request, self.template, {'div_elem': " ", 'is_user_attendee': self.user_attendee, 'categories': self.categories, 'org_id': self.org_id, "categories":Category.objects.all()})
		else:
			return render(request, 'hub/permission_denied.html', {"categories":Category.objects.all()})

	def _submit_event(self,request):
		data = request.POST.items()
		for key, value in data:
			print("%s %s" % (key, value))

		# Build the events
		new_event = Event()
		new_event.title = request.POST.get('n_title',"")
		new_event.contact_email = request.POST.get('n_email',"")
		# new_event.organizer = request.POST.get('n_org',"")
		new_event.location = request.POST.get('n_loc',"")
		new_event.description = request.POST.get('n_title',"n_desc")
		startdate_object = datetime.strptime(request.POST.get('n_startdate'),'%m/%d/%Y %I:%M %p')
		enddate_object = datetime.strptime(request.POST.get('n_enddate'),'%m/%d/%Y %I:%M %p')
		if enddate_object < startdate_object:
			return render(request, 'hub/event_upload.html', {'div_elem':self._get_alert_html('End date must be after the Start date!','fail'), "categories":Category.objects.all()})
		new_event.start_date = startdate_object
		new_event.end_date = enddate_object
		uploaded_poster = request.FILES['n_uploadedposter']
		new_event.image = uploaded_poster
		new_event.hashtags = request.POST.get('n_tags')
		new_event.org_id = get_organization_id(request.user.username)
		add_event_to_db(new_event)
		new_event.categories = get_categories(request.POST.getlist('n_category'))
		new_event.save()
		return render(request, 'hub/event_upload.html', {'div_elem':self._get_alert_html('Event Upload is Successful','sucess'), "categories":Category.objects.all()})

	@staticmethod
	def render_page(request):
		module = EventUpload(request)
		return module._render_event_upload(request)

	@staticmethod
	def event_upload_handler(request):
		module = EventUpload(request)
		return module._submit_event(request)


class SearchListing():
	name = "search_page"
	base_url = "event_search/"
	template = Constants.app_name+"/search_page.html"

	class Response():
		def __init__(self):
			self.events = []
			self.empty_search = True
			self.prefill = ""

	def __init__(self, request):
		self.response = SearchListing.Response()
		self.request = request
		self.user_attendee = is_user_attendee(request.user)
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(request.user.username)
		else:
			self.org_id=None

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
			event["organizer_url"] = OrganizationPage.get_url(event["org_id"])
			event["org_name"] = get_organization_name(event["org_id"])
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
								"empty_search":self.response.empty_search, 'is_user_attendee': self.user_attendee, 'org_id': self.org_id, "search_box_prefill":self.response.prefill,"categories":Category.objects.all()})


	def render(self):
		search_keywords = self._get_keywords()
		self.response.prefill=search_keywords
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


	def __init__(self, request):
		self.request = request
		self.user_attendee = is_user_attendee(request.user)
		self.org_details = None
		self.events = []
		self.invalid = False
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(request.user.username)
		else:
			self.org_id=None

	def _get_id(self):
		return self.request.GET.get("id")

	def _render_me(self):

		for event in self.events:
			event["image_url"] = Utils.get_image_url(event["image"])
			event["start_date"] = event["start_date"].strftime("%a, %b %d, %I:%M %p")
			event["event_url"]= EventDetails.get_url(event["id"])
		#print(str(self.org_details))
		if self.org_details:
			self.org_details.org_image = Utils.get_image_url(str(self.org_details.org_image))
		return render(self.request, OrganizationPage.template,
								{"organizer": self.org_details,
								"events":self.events, 'is_user_attendee': self.user_attendee,
								"invalid":self.invalid, 'org_id': self.org_id,"categories":Category.objects.all()})

	def render(self):
		id = self._get_id()
		if not id:
			self.invalid = True
		self.org_details = get_org_details(id)
		if self.org_details:
			self.events = upcoming_events_by_org(id)
		else:
			self.invalid = True
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
		if not check_user_name(user_name, is_org=True) and not check_user_name(user_name, is_org=False):
			return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('User is not registered. Please Signup','fail'), "categories":Category.objects.all()})
		# is_org = request.POST.get('n_is_org',False)
		# if not check_user_name(user_name,is_org):
		# 	return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('User is not registered. Please Signup','fail')})

		user = authenticate(request, username=user_name, password=password)
		if user is not None:
			auth.login(request,user)
			return redirect(Homepage.render_page)
		else:
			return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('Wrong Username, Password combination','fail'), "categories":Category.objects.all()})
	else:
		return render(request, 'hub/login.html', {"categories":Category.objects.all()})

def logout(request):
	auth.logout(request)
	return redirect(Homepage.render_page)

def signup(request):
	if(request.method == "POST"):
		user_name = request.POST.get('n_user_name',"")
		if user_name != "":
			#This request is for new user
			try:
				password = request.POST.get('n_user_password',"")
				email = request.POST.get('n_user_email',"")
				new_django_user = User.objects.create_user(user_name, email, password)
				new_custom_user = UserProfile()
				new_custom_user.user = new_django_user
				new_custom_user.user_name = user_name
				new_custom_user.user_is_organization = False
				new_custom_user.user_image = request.FILES['n_user_img']
				new_custom_user.user_first_name = request.POST.get('n_user_fn',"")
				new_custom_user.user_last_name = request.POST.get('n_user_ln',"")
				new_custom_user.user_email = request.POST.get('n_user_email',"")
				new_custom_user.save()
				return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('New User Registration Successful, Please Login','success'), "categories":Category.objects.all()})
			except IntegrityError as e:
				if(str(e)=="UNIQUE constraint failed: auth_user.username"):
					return render(request, 'hub/signup.html', {'div_elem':Utils.get_alert_html('Username '+user_name+' already registered. Please register with a new username','fail'), "categories":Category.objects.all()})
				else:
					return render(request, 'hub/signup.html', {'div_elem':Utils.get_alert_html(str(e),'fail'), "categories":Category.objects.all()})
		else:
			#This request is for new org
			try:
				user_name = request.POST.get('n_org_uname',"")
				password = request.POST.get('n_org_password',"")
				email = request.POST.get('n_org_email',"")
				new_django_user = User.objects.create_user(user_name, email, password)
				new_org = OrganizationDetails()
				new_org.user = new_django_user
				new_org.user_name = user_name
				new_org.org_name = request.POST.get("n_org_name", "")
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
				return render(request, 'hub/login.html', {'div_elem':Utils.get_alert_html('New Organization Registration Successful, Please Login','success'), "categories":Category.objects.all()})
			except IntegrityError as e:
				if(str(e)=="UNIQUE constraint failed: auth_user.username"):
					return render(request, 'hub/signup.html', {'div_elem1':Utils.get_alert_html('Username '+user_name+' already registered. Please register with a new username','fail'), "categories":Category.objects.all()})
				else:
					return render(request, 'hub/signup.html', {'div_elem1':Utils.get_alert_html(str(e),'fail'), "categories":Category.objects.all()})
	else:
		return render(request, 'hub/signup.html', {"categories":Category.objects.all()})

class Myevents():
	base_url = "myevents/"
	template = Constants.app_name+"/my_events.html"
	name ='My Events Page'

	def __init__(self, request):
		self.request = request
		self.user_attendee = is_user_attendee(request.user)
		if request.user.is_authenticated and not self.user_attendee:
			self.org_id = get_organization_id(request.user.username)
		else:
			self.org_id=None

	def _render_me(self):
		return render(self.request, Myevents.template, {'events':self.events, 'is_user_attendee': self.user_attendee, 'org_id': self.org_id, "categories":Category.objects.all()})

	def event_list(self):
		events=get_rsvp_events(self.request.user.id)
		for event in events:
			event["start_day"] = Utils.format_day(event["start_date"])
			event["end_day"] = Utils.format_day(event["end_date"])
			event["start_time"] = Utils.format_time(event["start_date"])
			event["end_time"] = Utils.format_time(event["end_date"])
			event["organizer_url"] = OrganizationPage.get_url(event["org_id"])
			event["org_name"] = get_organization_name(event["org_id"])
			if event["start_day"] == event["end_day"]:
				event["ending_same_day"]=True
			else:
				event["ending_same_day"]=False
			event["image_url"] = Utils.get_image_url(event["image"])
			event["event_url"] = EventDetails.get_url(event["id"])


		return events

	def render(self):
		self.events = self.event_list()
		return self._render_me()

	#@login_required
	@staticmethod
	def render_page(request):
		m = Myevents(request)
		return m.render()

	@staticmethod
	def get_url(id):
		return "/"+Myevents.base_url +"?id="+str(id)

class RSVP():
	name = "updateRSVP"
	save_rsvp_base_url = "ajax/saveRSVP/"
	remove_rsvp_base_url = "ajax/removeRSVP/"

	def __init__(self, request):
		self.request = request

	@staticmethod
	def save_RSVP(request):
	    user_id = request.GET.get('userId', None)
	    event_id = request.GET.get('eventId', None)
	    save_rsvp(user_id,event_id)
	    response ={}
	    response["isSuccess"] = True
	    return HttpResponse(json.dumps(response), content_type = "application/json")

	@staticmethod
	def remove_RSVP(request):
		user_id = request.GET.get('userId', None)
		# user_id = 2
		event_id = request.GET.get('eventId', None)
		remove_rsvp(user_id,event_id)
		response ={}
		response["isSuccess"] = True
		return HttpResponse(json.dumps(response), content_type = "application/json")

def validate_username(request):
    username = request.GET.get('username', None)
    response ={}
    response["isSuccess"] = True
    return HttpResponse(json.dumps(response), content_type = "application/json")
