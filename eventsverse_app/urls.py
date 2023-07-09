from django.urls import path
from . import views

urlpatterns = [
    path('list/<str:country>/', views.get_country_events),
    path('/weather/<str:event_id>/', views.get_event_weather),
    path('/flights/<str:eventid>/<str:user_airport_code>/', views.get_flight_list),
]
