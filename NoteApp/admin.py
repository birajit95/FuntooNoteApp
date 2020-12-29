from django.contrib import admin
from .models import Notes, Label
@admin.register(Notes)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','title','content','date','label', 'is_archive']

admin.site.register(Label)