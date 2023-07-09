from django.http import JsonResponse
import requests
from rest_framework.decorators import api_view
from .models import EventsList, EventWeather, FlightList
from datetime import datetime

# Create your views here.

def event_response(country):
    try:
        response = requests.get(
            url="https://api.predicthq.com/v1/events/",
            headers={
                "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
                "Accept": "application/json",
            },
            params={
                "country": country,
                "sort": "rank",
                "limit": 10
            }
        )
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response
    except requests.RequestException as e:
        # Handle request exceptions (e.g., network errors)
        return None

@api_view(['GET'])
def get_country_events(request, country):
    try:
        current_time = datetime.now().time().hour
        database_data = EventsList.objects.filter(event_country=country)

        if database_data:
            filter = EventsList.objects.filter(event_country=country).values()
            f_list = list(filter)
            add_time = f_list[0]

            hour = add_time['created_at'].hour

            if current_time - hour >= 6:
                events_response = event_response(country)

                if events_response is None:
                    return JsonResponse({"error": "Failed to fetch events data"}, status=500)

                events = events_response.json().get('results', [])
                EventsList.objects.filter(event_country=country).delete()

                for event in events:
                    EventsList.objects.create(
                        event_name=event['title'],
                        event_id=event['id'],
                        event_country=event['country'],
                        event_date=event['start'],
                        latitude=event["location"][0],
                        longtude=event["location"][1],
                        rank=event['rank'],
                        description=event["description"]
                    )

            events = EventsList.objects.filter(event_country=country).values()
            return JsonResponse(list(events), safe=False)
        else:
            events = EventsList.objects.filter(event_country=country).values()
            return JsonResponse(list(events), safe=False)
    except Exception as e:
        # Handle other exceptions that may occur
        return JsonResponse({"error": str(e)}, status=500)
    

@api_view(['GET'])
def get_event_weather(request, event_id):
    # Get current hour
    current_time = datetime.now().time().hour
    
    # Check if weather data exists in the database
    database_data = EventWeather.objects.filter(event_id=event_id)

    # Get event details from Events model
    event_list = list(EventsList.objects.filter(event_id=event_id).values())[0]
    lat = event_list['latitude']
    lon = event_list['longitude']
    
    # Create URL for weather API
    url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=f22892654725839a44ff6db985f0b151'.format(lat, lon)

    if database_data:
        # Checks if the weather data exists in the database
        if current_time - event_list['created_at'].hour >= 6:
            # If more than 6 hours have passed since last update, fetch new weather data
            try:
                res = requests.get(url)
                res.raise_for_status()  # Check for any request errors

                event_weather = res.json().get('main', {})

                # Update weather data in the database
                EventWeather.objects.filter(event_id=event_id).delete()
                EventWeather.objects.create(
                    event_id = event_id,
                    event_name = event_list['event_name'],
                    temperature = event_weather.get("temp"),
                    humidity = event_weather.get("humidity")
                )

                event_database = EventWeather.objects.filter(event_id=event_id).values()
                return JsonResponse(list(event_database), safe=False)
            except requests.exceptions.RequestException as e:
                # Handle request exception errors
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Less than 6 hours have passed since last update, return existing weather data
            event_database = EventWeather.objects.filter(event_id=event_id).values()
            return JsonResponse(list(event_database), safe=False)
    else:
        # Weather data does not exist in the database, fetch new data
        try:
            res = requests.get(url)
            res.raise_for_status()  # Check for any request errors

            event_weather = res.json().get('main', {})

            # Save weather data to the database
            EventWeather.objects.create(
                event_id=event_id,
                event_name = event_list['event_name'],
                temperature = event_weather.get("temp"),
                humidity = event_weather.get("humidity")
            )

            event_database = EventWeather.objects.filter(event_id=event_id).values()
            return JsonResponse(list(event_database), safe=False)
        except requests.exceptions.RequestException as e:
            # Handle request exception errors
            return JsonResponse({'error': str(e)}, status=500)
        

def get_flight_list(request, event_id, user_airport_code):
    try:
        current_time = datetime.now().time().hour
        database_data = FlightList.objects.filter(event_id=event_id)
        event_list = list(EventsList.objects.filter(event_id=event_id).values())[0]
        lat = event_list['latitude']
        lon = event_list['longitude']
        url_to_get_nearby_airports = 'https://airlabs.co/api/v9/nearby?lat={}&lng={}&distance=200&api_key=cf76d9e8-1207-4e6a-81be-ca3e77c1156c'.format(lat, lon)

        if database_data:
            if current_time - event_list['created_at'].hour >= 6:
                res = requests.get(url_to_get_nearby_airports)
                event_nearby_airports_iata_codes = res.json().get('response', [])

                if len(event_nearby_airports_iata_codes['airports']) >= 1:
                    event_nearby_airports_iata_codes = event_nearby_airports_iata_codes['airports'][0]['iata_code']
                else:
                    err_message = "No airports (within 200km) from the event location"
                    return JsonResponse({"response": err_message})

                outbound_flights_list = get_flight_schedule(user_airport_code, event_nearby_airports_iata_codes)
                inbound_flights_list = get_flight_schedule(event_nearby_airports_iata_codes, user_airport_code)

                FlightList.objects.filter(event_id=event_id).delete()
                FlightList.objects.create(event_id=event_id, outbound_flights=outbound_flights_list, inbound_flights=inbound_flights_list)

                flight_database = FlightList.objects.filter(event_id=event_id).values()
                return JsonResponse(list(flight_database), safe=False)

            else:
                flight_database = FlightList.objects.filter(event_id=event_id).values()
                return JsonResponse(list(flight_database), safe=False)
        else:
            event_nearby_airports_iata_codes = get_nearby_airport_iata_code(lat, lon)

            if len(event_nearby_airports_iata_codes['airports']) >= 1:
                event_nearby_airports_iata_codes = event_nearby_airports_iata_codes['airports'][0]['iata_code']
            else:
                err_message = "No airports (within 200km) from the event location"
                return JsonResponse({"response": err_message})

            outbound_flights_list = get_flight_schedule(user_airport_code, event_nearby_airports_iata_codes)
            inbound_flights_list = get_flight_schedule(event_nearby_airports_iata_codes, user_airport_code)

            FlightList.objects.create(event_id=event_id, outbound_flights=outbound_flights_list, inbound_flights=inbound_flights_list)

            flight_database = FlightList.objects.filter(event_id=event_id).values()
            return JsonResponse(list(flight_database), safe=False)

    except Exception as e:
        # Handle any exceptions or errors that occur during the execution of the code
        err_message = "An error occurred: {}".format(str(e))
        return JsonResponse({"response": err_message})


def get_nearby_airport_iata_code(lat, lon):
    url_to_get_nearby_airports = 'https://airlabs.co/api/v9/nearby?lat={}&lng={}&distance=200&api_key=cf76d9e8-1207-4e6a-81be-ca3e77c1156c'.format(lat, lon)
    res = requests.get(url_to_get_nearby_airports)
    return res.json().get('response', [])


def get_flight_schedule(dep_iata, arr_iata):
    url_to_get_flight_schedule = f'https://airlabs.co/api/v9/schedules?dep_iata={dep_iata}&arr_iata={arr_iata}&api_key=cf76d9e8-1207-4e6a-81be-ca3e77c1156c'
    res = requests.get(url_to_get_flight_schedule)
    flights_list = res.json().get('response', [])

    if not flights_list:
        flights_list = [{"response": "There are no flights available for the given airports."}]

    return flights_list
