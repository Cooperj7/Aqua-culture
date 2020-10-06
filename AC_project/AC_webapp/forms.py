from django.forms import ModelForm
from .models import Settings

class SettingsMF(ModelForm):
    class Meta:
        model = Settings
        fields = ['Value']
