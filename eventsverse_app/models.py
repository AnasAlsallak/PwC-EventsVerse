from django.db import models

# Create your models here.

class EventsList (models.Model):
    event_id = models.CharField(max_length=100)
    event_name = models.CharField(max_length=100)
    event_country = models.CharField(max_length = 10)
    event_date = models.CharField(max_length=100)
    latitude= models.FloatField()
    longtude= models.FloatField()
    description = models.TextField()
    rank = models.IntegerField()
    created_at = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name

class EventWeather(models.Model):
    event_id = models.CharField(max_length=100)
    event_name = models.CharField(max_length=100)
    temperature = models.FloatField(default=0.0, blank=True)
    humidity = models.FloatField(default=0.0, blank=True)

    def __str__(self):
        return f"Weather for the event: {self.event.event_name} temp- {self.temperature} humid- {self.humidity}"

class FlightList(models.Model):
       event_id = models.CharField(max_length=64)
       outbound_flights = models.JSONField()
       inbound_flights = models.JSONField()

       def __str__(self):
            return f"Flights for the event: {self.event.event_name}"