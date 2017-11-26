from django.db import models
from django.utils import timezone
from datetime import datetime
import pytz
from .models import Event, UserProfile, OrganizationDetails

pst = pytz.timezone('US/Pacific')
# Hard coding PST as timezone as one time fix.
# Need to update this to get dynamic tz conversion

def search_events(search_text):
    today_date = datetime.now(pst).replace(hour=0, minute=0, second=0)
    events_results = []
    for keywords in search_text.split():
        events_results += Event.objects.filter(
            title__icontains=keywords, start_date__gte=today_date).all().values()
    events_results.sort(key = lambda item:item['start_date'])
    return events_results

def upcoming_events():
    today_date = datetime.now(pst).replace(hour=0, minute=0, second=0)
    events_results = list(Event.objects.filter(start_date__gte=today_date).all().values())
    events_results.sort(key = lambda item:item['start_date'])
    return events_results

def event_details(event_id):
    return list(Event.objects.filter(id=event_id).all().values())

def add_event_to_db(event):
	event.save()

def check_user_name(username,is_org):
	if is_org:
		if(OrganizationDetails.objects.filter(user_name = username).exists()):
			return True
	else:
		if(UserProfile.objects.filter(user_name = username).exists()):
			return True
	return False
