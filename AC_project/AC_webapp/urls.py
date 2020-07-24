from django.urls import path
from . import views

urlpatterns = [
     path('', views.ph, name='Homepage'),
     path('', views.ph, name='DataViz'),
     path('', views.ph, name='FishFeederSettings'),
     path('', views.ph, name='PlantBuddy'),
     path('', views.ph, name='PumpSettings'),
     path('', views.ph, name='Weather'),
]
