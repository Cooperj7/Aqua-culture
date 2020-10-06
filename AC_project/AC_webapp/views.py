from django.shortcuts import render, redirect
from .models import SensorData, WeatherData, Settings
from .forms import SettingsMF
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

def SettingsPage(request):
    Homepage = SensorData.objects.latest("id")
    PumpOnSettings = Settings.objects.get(id=1)
    PumpOffSettings = Settings.objects.get(id=2)
    FishFeederTime = Settings.objects.get(id=3)
    FishFeederAmount = Settings.objects.get(id=4)
    
    if request.method == "POST" and 'btnform1' in request.POST:
        OnForm = SettingsMF(request.POST, instance=PumpOnSettings)    
        if OnForm.is_valid():  
            OnForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform2' in request.POST:
        OffForm = SettingsMF(request.POST, instance=PumpOffSettings)
        if OffForm.is_valid():
            OffForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform3' in request.POST:
        OnForm = SettingsMF(request.POST, instance=FishFeederTime)    
        if OnForm.is_valid():  
            OnForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform4' in request.POST:
        OffForm = SettingsMF(request.POST, instance=FishFeederAmount)
        if OffForm.is_valid():
            OffForm.save()
            return redirect('SettingsPage')
    else:
        OnForm = SettingsMF(request.POST, instance=PumpOnSettings)
        OffForm = SettingsMF(request.POST, instance=PumpOffSettings)
        TimeForm = SettingsMF(request.POST, instance=FishFeederTime)
        FoodForm = SettingsMF(request.POST, instance=FishFeederAmount)
        
    context = {"Homepage": Homepage,"PumpOnSettings": PumpOnSettings, "PumpOffSettings": PumpOffSettings,"FishFeederTime": FishFeederTime, "FishFeederAmount": FishFeederAmount,"OnForm": OnForm, "OffForm": OffForm,"TimeForm": TimeForm, "FoodForm": FoodForm}
    return render(request, "SettingsPage.htm", context)


def SettingsEdit(request):
    Homepage = SensorData.objects.latest("id")
    PumpOnSettings = Settings.objects.get(id=1)
    PumpOffSettings = Settings.objects.get(id=2)
    FishFeederTime = Settings.objects.get(id=3)
    FishFeederAmount = Settings.objects.get(id=4)

    if request.method == "POST" and 'btnform1' in request.POST:
        OnForm = SettingsMF(request.POST, instance=PumpOnSettings)
        if OnForm.is_valid():
            OnForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform2' in request.POST:
        OffForm = SettingsMF(request.POST, instance=PumpOffSettings)
        if OffForm.is_valid():
            OffForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform3' in request.POST:
        TimeForm = SettingsMF(request.POST, instance=FishFeederTime)
        if OnForm.is_valid():
            OnForm.save()
            return redirect('SettingsPage')
    if request.method == "POST" and 'btnform4' in request.POST:
        FoodForm = SettingsMF(request.POST, instance=FishFeederAmount)
        if OffForm.is_valid():
            OffForm.save()
            return redirect('SettingsPage')
    else:
        OnForm = SettingsMF(request.POST, instance=PumpOnSettings)
        OffForm = SettingsMF(request.POST, instance=PumpOffSettings)
        TimeForm = SettingsMF(request.POST, instance=FishFeederTime)
        FoodForm = SettingsMF(request.POST, instance=FishFeederAmount)

    context = {"Homepage": Homepage, "PumpOnSettings": PumpOnSettings, "PumpOffSettings": PumpOffSettings,
               "FishFeederTime": FishFeederTime, "FishFeederAmount": FishFeederAmount, "OnForm": OnForm,
               "OffForm": OffForm, "TimeForm": TimeForm, "FoodForm": FoodForm}
    return render(request, "SettingsEdit.htm", context)
    