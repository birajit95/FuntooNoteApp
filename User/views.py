from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from .serialyzer import UserSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .JWTAuthentication import JWTAuth
from .emailVarification import Email
from django.contrib.auth import authenticate, login


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
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/verify-email/'
            email_data = Email.configureEmail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            response = {'msg': "data is created and a confirmation mail is sent to your mail"}
            return HttpResponse(JSONRenderer().render(response))
        return HttpResponse(JSONRenderer().render(serializer.errors))

class VerifyEmail(APIView):
    def get(self, request):
        jwtToken = request.GET.get('token')
        response = JWTAuth.verifyToken(jwtToken=jwtToken)
        if not response:
            responseMsg = {'msg': 'Session for this token is expired!'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        username = response.get('username')
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        responseMsg = {'msg': 'Your account is activated! Now you can log in'}
        return HttpResponse(JSONRenderer().render(responseMsg))


class UserLogin(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            responseMsg = {'msg': 'You are logged in successfully'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        user = User.objects.get(username=username)
        if user:
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/verify-email/'
            email_data = Email.configureEmail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            responseMsg = {'msg': 'Your account is not active. Please activate your account from the link shared in '
                                  'your mail '}
            return HttpResponse(JSONRenderer().render(responseMsg))
        responseMsg = {'msg': 'Bad Credential found'}
        return HttpResponse(JSONRenderer().render(responseMsg))
