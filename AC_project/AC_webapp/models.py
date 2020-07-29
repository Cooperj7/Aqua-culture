from django.db import models

# Create your models here.
class PumpSettings(models.Model):
    on_time = models.IntegerField(default=0)
    off_time = models.IntegerField(default=0)

    def __str__(self):
        return str(self.on_time) + str(off_time)
        
class FishFeederSettings(models.Model):
    fishfeeder_time = models.IntegerField(default=0)
    fishfeeder_amount = models.IntegerField(default=0)

    def __str__(self):
        return str(fishfeeder_time) + str(fishfeeder_amount)
    
class WeatherData(models.Model):
    date_time = models.CharField(max_length=40)
    temperature = models.FloatField(default=0)
    min_temperature = models.FloatField(default=0)
    max_temperature = models.FloatField(default=0)
    humidity = models.IntegerField(default=0)
    weather_label = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=200)
    cloudiness_level = models.IntegerField(default=0)
    wind_speed = models.FloatField(default=0)

    def __str__(self):
        return str(self.date_time) + str(self.temperature) + str(self.min_temperature) + str(self.max_temperature) + str(self.humidity) + str(self.weather_label) + str(self.weather_description) + str(self.cloudiness_level) + str(self.wind_speed)

class SensorData(models.Model):
    water_pH = models.FloatField(default=0)
    tds = models.IntegerField(default=0)
    water_temp = models.FloatField(default=0)
    air_temp = models.FloatField(default=0)
    humidity = models.FloatField(default=0)
    
    def __str__(self):
        return str(self.water_pH) + str(self.tds) + str(self.water_temp) + str(self.air_temp) + str(self.humidity)

class Settings(models.Model):
    Setting_name = models.CharField(max_length=25)
    Value = models.CharField(max_length=5)

    def __str__(self):
        return str(self.Setting_name) + str(self.Value)
    
class PlantBuddy(models.Model): 
    zipcode = models.CharField(max_length=10)
    phone_num = models.CharField(max_length=11)

    def __str__(self):
        return str(self.zipcode) + str(self.phone_num)


    
    
