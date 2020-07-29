from django.urls import include, path
from . import views

urlpatterns = [
     path('', views.Homepage, name='Homepage'),
     path('FishFeederSettings/', views.FishFeederSettings, name='FishFeederSettings'),
     path('PlantBuddy/', views.PlantBuddy, name='PlantBuddy'),
     path('PumpSettings/', views.PumpSettings, name='PumpSettings'),
     path('Weather/', views.Weather, name='Weather'),
     #path('DataViz/', views.DataViz, name='DataViz'),
]
