from django.shortcuts import render

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
