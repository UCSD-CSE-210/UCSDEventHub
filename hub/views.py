from django.shortcuts import render
from .models import Event
from .models import search_events
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
	events = search_events(search_keywords)
	return render(request, 'hub/search_page.html', {'events':events})
	
	