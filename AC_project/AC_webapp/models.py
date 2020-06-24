from django.db import models

# Create your models here.

class Weather(models.Model):
    date_time = models.CharField(max_length=40)
    temperature = models.FloatField(default=0)
    min_temperature = models.FloatField(default=0)
    max_temperature = models.FloatField(default=0)
    humidity = models.IntegerField(default=0)
    weather_label = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=200)
    cloudiness_level = models.IntegerField(default=0)
    wind_speed = models.FloatField(default=0)

class SensorData(models.Model):
    water_pH = models.FloatField(default=0)
    tds = models.IntegerField(default=0)
    water_temp = models.FloatField(default=0)
    air_temp = models.FloatField(default=0)
    humidity = models.FloatField(default=0)

    
    
    

    
    
