from django.shortcuts import render
from .models import Event

# Create your views here.
def post_list(request):
    events = Event.objects.all()
    return render(request, 'hub/post_list.html', {'events':events})