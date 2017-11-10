from django.shortcuts import render
from .models import Event

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
