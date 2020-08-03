from django.forms import ModelForm
from .models import Settings

class PumpSettingsMF(ModelForm):
    class Meta:
        model = Settings
        fields = ['Value']
