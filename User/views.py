from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from django.views import View
from .models import User
from django.contrib.auth.hashers import make_password


class UserRegistration(APIView):

    def get(self, request):
        return render(request, "userRegistrration.html")

    def post(self, request):
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        userName = request.POST['userName']
        email = request.POST['email']
        password = request.POST['pass1']
        hashPass = make_password(password)
        User(firstName=firstName, lastName=lastName, userName=userName, email=email, password=hashPass).save()
        return HttpResponse("Registration is done")
