from django.db import models
from django.utils import timezone
import pytz

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null = True)
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to="events")
    hashtags = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    contact_email = models.EmailField()
    # create_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # create_date = models.DateTimeField(null = False)
    # modify_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # modify_date = models.DateTimeField(null = False)
    # delete_date = models.DateTimeField(null = True)

def search_events(search_text):
    events_results = []
    for keywords in search_text.split():
        events_results += Event.objects.filter(title__icontains=keywords).all().values()
    return events_results

def upcoming_events():
    now_time = timezone.now()
    events_results = list(Event.objects.filter(start_date__gte=now_time).all().values())
    return events_results

def event_details(event_id):
    return list(Event.objects.filter(id=event_id).all().values())