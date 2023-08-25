from django.shortcuts import render
import requests
import datetime
import json
import time 

def index(request):

    today = datetime.datetime.today()

    today_time = today.strftime("%I:%M %p")
    month = today.strftime("%B")[:3]
    today_date = today.strftime("%A, %d")+" "+ month

    # API_Key = "jdtbNYS1yVhqytxc1XffOmPESoVUgFUL"
    API_Key = "GdGnN234oKfubtDbATRJRnDCgMWq41uL"

    weather_url = "http://dataservice.accuweather.com/currentconditions/v1/{}?apikey={}&details=true"
    first_day_weather_url = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/{}?apikey={}&details=true&metric=true"
    forecast_url = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/{}?apikey={}&details=true&metric=true"
    location_code_url = "http://dataservice.accuweather.com/locations/v1/cities/search?apikey={}&q={}"
    
    if request.method == "POST":

        city = request.POST["city"]
        city_name , city_code , country = location_code(city, API_Key, location_code_url)

        weather_data,forecast_data = city_weather_details(city_name , country , city_code , API_Key , weather_url , forecast_url , first_day_weather_url)
        
        context = {
            'weather_data' : weather_data,
            'forecast_data' : forecast_data,
            'today_time' : today_time,
            'today_date' : today_date,
        }
        
        return render(request ,"weathercheckapp/index.html" , context)

    else:
        city = "New Delhi"
        city_name , city_code , country = location_code(city, API_Key, location_code_url)

        weather_data,forecast_data = city_weather_details(city_name , country , city_code , API_Key , weather_url , forecast_url , first_day_weather_url)
        
        context = {
            'weather_data' : weather_data,
            'forecast_data' : forecast_data,
            'today_time' : today_time,
            'today_date' : today_date,
        }
        return render(request ,"weathercheckapp/index.html" , context)
    
def location_code(city, API_Key, location_code_url):

    location_code_response = requests.get(location_code_url.format(API_Key,city)).json()
    return location_code_response[0]['LocalizedName'] , location_code_response[0]['Key'] , location_code_response[0]['Country']['LocalizedName']


def city_weather_details(city_name , country , city_code , API_Key , weather_url , forecast_url , first_day_weather_url):

    weather_response = requests.get(weather_url.format(city_code,API_Key)).json()

    first_day_response = requests.get(first_day_weather_url.format(city_code,API_Key)).json()

    forecast_response = requests.get(forecast_url.format(city_code,API_Key)).json()

    weather_data = {
        'city' : city_name,
        'country' : country,
        'temperature' : weather_response[0]['Temperature']['Metric']['Value'],
        'min_temp' : first_day_response["DailyForecasts"][0]['Temperature']['Minimum']['Value'],
        'max_temp' : first_day_response["DailyForecasts"][0]['Temperature']['Maximum']['Value'],
        'feel_like' : weather_response[0]['RealFeelTemperature']['Metric']['Value'],
        'sun_rise' : datetime.datetime.fromtimestamp(first_day_response["DailyForecasts"][0]['Sun']['EpochRise']).strftime('%I:%M %p'),
        'sun_set' : datetime.datetime.fromtimestamp(first_day_response["DailyForecasts"][0]['Sun']['EpochSet']).strftime('%I:%M %p'),
        'pressure' : weather_response[0]['Pressure']['Metric']['Value'],
        'humidity' : weather_response[0]['RelativeHumidity'],
        'visibility' : weather_response[0]['Visibility']['Metric']['Value'],
        'description' : weather_response[0]['WeatherText'],
        'DewPoint' : weather_response[0]['DewPoint']['Metric']['Value'],
        'icon' : weather_response[0]['WeatherIcon'],
        'wind' : weather_response[0]['Wind']['Speed']['Metric']['Value'],
    }

    forecast_data = []
    for daily_data in forecast_response['DailyForecasts']:
        forecast_data.append({ 
            'day' : datetime.datetime.fromtimestamp(daily_data['EpochDate']).strftime("%A"),
            'date' : datetime.datetime.fromtimestamp(daily_data['EpochDate']).strftime("%d/%m"),
            'min_max_Temp' : "{} / {}".format(daily_data['Temperature']['Minimum']['Value'],daily_data['Temperature']['Maximum']['Value']),
            'wind' : daily_data['Day']['Wind']['Speed']['Value'],
        })
    
    return weather_data , forecast_data