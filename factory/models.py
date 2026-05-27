from django.db import models
from django.contrib.auth.models import User



class Factory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='factories')
    name = models.CharField(max_length=255)
    factory_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    established_year = models.PositiveIntegerField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        # ✅ New field for profile picture
    profile_picture = models.ImageField(
        upload_to='factory_logos/',        # folder inside media/ where images will be stored
        default='factory_logos/default.png',  # default image if user doesn't upload
        blank=True
    )


    def __str__(self):
        return self.name




class Asset(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    emission_factor = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.factory.name})"
    

class Usage(models.Model):
    # Link usage to a specific asset
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='usages')
    
    # Usage details
    date = models.DateField()
    usage_amount = models.FloatField()        # amount of usage (kWh, liters, etc.)
    emission = models.FloatField()            # calculated emission in kg CO2

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.name} - {self.date} - {self.emission} kg CO2"




class FactoryProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   # ✅ allows multiple factories
    name = models.CharField(max_length=255)
    factory_type = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)  # unique per factory
    established_year = models.IntegerField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()


class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    factory_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.factory_owner.email})"


# factory/models.py

from django.db import models
from django.contrib.auth.models import User

# factory/models.py
from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='admin_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


from django.db import models
from django.contrib.auth.models import User
from .models import Factory

class Report(models.Model):
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Report by {self.submitted_by.username} for {self.factory.name}"
