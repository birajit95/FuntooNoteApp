from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from .serialyzer import UserSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User


class UserRegistration(APIView):
    def get(self, request):
        return render(request, "userRegistrration.html")

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.data.get('username'))
            user.is_active = False
            user.save()
            response = {'msg': "data is created"}
            return HttpResponse(JSONRenderer().render(response))
        return HttpResponse(JSONRenderer().render(serializer.errors))
