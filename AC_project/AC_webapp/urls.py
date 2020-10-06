from django.urls import include, path
from . import views

urlpatterns = [
     path('', views.Homepage, name='Homepage'),
     path('SettingsPage/', views.SettingsPage, name='SettingsPage'),
     path('SettingsEdit/', views.SettingsEdit, name='SettingsEdit'),
     path('Weather/', views.Weather, name='Weather'),
]
