from django.contrib import admin
from .models import Notes
@admin.register(Notes)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','title','content','date','label', 'is_archive']
