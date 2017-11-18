from django.db import models
from django.utils import timezone
import pytz
from .models import Event

def search_events(search_text):
    events_results = []
    for keywords in search_text.split():
        events_results += Event.objects.filter(title__icontains=keywords).all().values()
    events_results.sort(key = lambda item:item['start_date'])
    return events_results

def upcoming_events():
    now_time = timezone.now()
    events_results = list(Event.objects.filter(start_date__gte=now_time).all().values())
    events_results.sort(key = lambda item:item['start_date'])
    return events_results

def event_details(event_id):
    return list(Event.objects.filter(id=event_id).all().values())

def add_event_to_db(event):
	event.save()
