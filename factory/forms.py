from django import forms
from .models import Factory

class FactoryProfileForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = [
            'name', 'factory_type', 'registration_number', 'established_year',
            'address', 'city', 'country', 'phone_number', 'email', 'profile_picture'  # ✅ added
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
