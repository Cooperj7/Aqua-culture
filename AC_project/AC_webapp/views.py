from django.shortcuts import render, redirect
from .models import SensorData, WeatherData, Settings
from .forms import PumpSettingsMF
from django.http import HttpResponse


# Create your views here.

def Homepage(request):
    Homepage = SensorData.objects.latest("id")
    Weather = WeatherData.objects.latest("id")
    context = {"Homepage": Homepage, "Weather": Weather}

    return render(request, "Homepage.htm", context)

def Weather(request):
    Homepage = SensorData.objects.latest("id")
    Weather = WeatherData.objects.latest("id")
    context = {"Homepage": Homepage, "Weather": Weather}

    return render(request, "Weather.htm", context)

def PlantBuddy(request):
    Homepage = SensorData.objects.latest("id")
    PlantBuddy = Settings.objects.get(id=6)
    context = {"Homepage": Homepage,"PlantBuddy": PlantBuddy}
    
    return render(request, "PlantBuddy.htm", context)

def PumpSettings(request):
    Homepage = SensorData.objects.latest("id")
    PumpOnSettings = Settings.objects.get(id=1)
    PumpOffSettings = Settings.objects.get(id=2)
    if request.method == "POST":
        OnForm = PumpSettingsMF(request.POST, instance=PumpOnSettings)
        if OnForm.is_valid(): 
            OnForm.save()
            return redirect('PumpSettings')
        OffForm = PumpSettingsMF(request.POST, instance=PumpOffSettings)
        if OffForm.is_valid():
            OffForm.save()
            return redirect('PumpSettings')
    else:
        OnForm = PumpSettingsMF(request.POST, instance=PumpOnSettings)
        OffForm = PumpSettingsMF(request.POST, instance=PumpOffSettings)
    context = {"OnForm": OnForm, "OffForm": OffForm, "Homepage": Homepage, "PumpOnSettings": PumpOnSettings, "PumpOffSettings": PumpOffSettings}
    return render(request, "PumpSettings.htm", context)


def FishFeederSettings(request):
    Homepage = SensorData.objects.latest("id")
    FishFeederTime = Settings.objects.get(id=3)
    FishFeederAmount = Settings.objects.get(id=4)
    context = {"Homepage": Homepage, "FishFeederTime": FishFeederTime, "FishFeederAmount": FishFeederAmount}
    
    return render(request, "FishFeederSettings.htm", context)





    
