from django.shortcuts import render

# Create your views here.

def Homepage(request):
    Homepage = SensorData.objects.latest("id")
    context = {"water_pH": water_pH, "tds": tds, t"water_temp": water_temp, "air_temp": air_temp, "humidity": humidity}

    return render(request, "Homepage.html", context)

def Weather(request):
    Weather = Weather.objects.latest("id")
    context = {"date_time": date_time, "temperature": temperature, "min_temperature": min_temperature, "max_temperature": max_temperature, "humidity": humidity, "weather_label": weather_label, "weather_description": weather_description, "cloudiness_level": cloudiness_level, "wind_speed": wind_speed}

    return render(request, 'Weather.html', context)

def DataViz(request):

    return render(request, 'DataViz.html', context)

def PlantBuddy(request):
    PlantBuddy = PlantBuddy.objects.latest("id")
    context = {"phone_num": phone_num}
    
    return render(request, 'PlantBuddy.html', context)

def PumpSettings(request):
    PumpSettings = PumpSettings.objects.latest("id")
    context = {"on_time": on_time, "off_time": off_time}
    
    return render(request, 'PumpSettings.html', context)

def FishFeederSettings(request):
    FishFeederSettings = FishFeederSettings.objects.latest("id")
    context = {"fishfeeder_time": fishfeeder_time, "fishfeeder_amount": fishfeeder_amount}
    
    return render(request, 'FishFeederSettings.html', context)

    
