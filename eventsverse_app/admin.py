from django.contrib import admin

# Register your models here.

from .models import EventsList, EventWeather, FlightList

admin.site.register(EventsList)
admin.site.register(EventWeather)
admin.site.register(FlightList)
