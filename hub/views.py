from django.shortcuts import render
from .models import Event
from .models import event_details

import json
from django.http import HttpResponse
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

def event_detail(request):
    # making a call to the get event details api with an id of the event to get details. 
    # print eventId
    # print type(request.GET)
    eventId = request.GET.get("id")
    # print type(eventId)
    evntId = int(eventId)
    print evntId
    print type(evntId)
    # eventId = json.loads(eventIds)
    events = event_details(evntId)
    # events[0]
    # eventDict = {}
    l=events
    print l	

  	# print eventDetails
    # print events.get("description")
    # return HttpResponse("<h1>Hi</h1>")
    # return render(request, 'hub/event_details.html', {'description':str(events.get("description"))})
    return render(request, 'hub/event_details.html', {'events':events[0]})