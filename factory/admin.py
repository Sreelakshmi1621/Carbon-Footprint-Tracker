from django.contrib import admin
from .models import Factory, Asset, Usage

# Register your models here
admin.site.register(Factory)
admin.site.register(Asset)
admin.site.register(Usage)
