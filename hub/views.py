from django.shortcuts import render
from .models import Event,add_event_to_db
from .models import search_events
from django.http import HttpResponse
from django.utils import dateparse
from datetime import datetime
import re

# Create your views here.
def post_list(request):
    events = Event.objects.all()
    return render(request, 'hub/Homepage.html', {'events':events})

def event_list(request):
    events1 = Event.objects.all()
    events = events1 #.sort(key=lambda e: e.date)[:3]
    return render(request, 'hub/Homepage.html', {'events':events})

    
def event_upload(request):
    return render(request, 'hub/event_upload.html', {})

def event_details(request):
    # making a call to the get event details api with an id of the event to get details. 
    return render(request, 'hub/event_details.html', {'events':events})
	
def render_search_page(request):
	search_keywords = request.GET.get("q")
	def clean(key):
		key = re.sub(' ', '-', key)
		key = re.sub('[^A-Za-z0-9-]', '', key)
		key = re.sub('-+',' ', key)
		return key
	search_keywords = clean(search_keywords)
	#print("search=",search_keywords)
	events = search_events(search_keywords)
	for event in events:
		event["start_day"] = event["start_date"].strftime("%a, %b %m")
		event["start_time"] = event["start_date"].strftime("%I:%M %p")
	#print(events)
	return render(request, 'hub/search_page.html', {'events':events})

# Event Upload related views
def get_alert(text,alerttype):
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

def event_upload(request):
    return render(request, 'hub/event_upload.html', {'div_elem': " "})
   
def submit_event(request):
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
	return render(request, 'hub/event_upload.html', {'div_elem':get_alert('Event Upload is Successful','sucess')})


