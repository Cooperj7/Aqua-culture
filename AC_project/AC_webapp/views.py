from django.shortcuts import render
from .models import SensorData

# Create your views here.

def Homepage(request):

    context = {
        }

    """ 'water_pH'=water_pH,
        'tds'=tds,
        'water_temp'=water_temp,
        'air_temp'=air_temp,
        'humidity'=humidity,
        'date_time'=date_time,
        'temperature'=temperature,
        'min_temperature'=min_temperature,
        'max_temperature'=max_temperature,
        'humidity'=humidity,
        'weather_label'=weather_label,
        'weather_description'=weather description,
        'cloudiness_level'=cloudiness level,
        'wind_speed'=wind speed,
        """

    return render(request, 'Homepage.htm', context=context)

# def sensordata(request):
#
#     ph = SensorData.water_pH
#     tds = SensorData.tds
#     water_temp = SensorData.water_temp
#     air_temp = SensorData.air_temp
#     humidity = SensorData.humidity
#
#     context={'ph': ph, "tds": tds, "water_temp": water_temp, "air_temp": air_temp, "humidity": humidity}
#
#     return render(request, "", context)

def ph(request):

    ph = SensorData.objects.latest("id")
    context = {"ph": ph}

    return render(request, "Homepage.html", context)