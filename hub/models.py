from django.db import models
from django.utils import timezone

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null = True)
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to="events")
    hastags = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    contact_email = models.EmailField()
    # create_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # create_date = models.DateTimeField(null = False)
    # modify_user = models.CharField(max_length = 255, validators=[MinLengthValidator(1)])
    # modify_date = models.DateTimeField(null = False)
    # delete_date = models.DateTimeField(null = True)

def find_event(key):
    events_results = []
    for keywords in key.split():
        events_results += Event.objects.filter(title__icontains=keywords).all().values()
    return events_results
