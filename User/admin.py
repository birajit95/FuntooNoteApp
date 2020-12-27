from django.contrib import admin
from .models import Profile, TokenBlackLists

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id','user','bio','dob']

admin.site.register(TokenBlackLists)
