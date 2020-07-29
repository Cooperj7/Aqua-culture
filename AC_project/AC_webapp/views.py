from django.shortcuts import render
from .models import SensorData, WeatherData, Settings

# Create your views here.

def Homepage(request):
    Homepage = SensorData.objects.all()
    context = {"Homepage": Homepage}

    return render(request, "Homepage.htm", context)

def Weather(request):
    Weather = WeatherData.objects.all()
    context = {"Weather": Weather}

    return render(request, "Weather.htm", context)

def PlantBuddy(request):
    PlantBuddy = Settings.objects.all()
    context = {"PlantBuddy": PlantBuddy}
    
    return render(request, "PlantBuddy.htm", context)

def PumpSettings(request):
    PumpSettings = Settings.objects.all()
    context = {"PumpSettings":PumpSettings}
    
    return render(request, "PumpSettings.htm", context)

def FishFeederSettings(request):
    FishFeederSettings = Settings.objects.all()
    context = {"FishFeederSettings": FishFeederSettings}
    
    return render(request, "FishFeederSettings.htm", context)

    
