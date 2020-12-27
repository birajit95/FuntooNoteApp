from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from .serialyzer import UserSerializer, ResetPasswordSerializer, ForgotPasswordSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .JWTAuthentication import JWTAuth
from .emailVarification import Email
from django.contrib.auth import authenticate, login, logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required


class UserRegistration(APIView):
    def get(self, request):
        return render(request, "userRegistrration.html")

    first_name = openapi.Parameter(
        'first_name', in_= openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    last_name = openapi.Parameter(
        'last_name', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    username = openapi.Parameter(
        'username', in_= openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    email = openapi.Parameter(
        'email', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    password = openapi.Parameter(
        'password', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[first_name, last_name, username, email, password])
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
    username = openapi.Parameter(
        'username', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    password = openapi.Parameter(
        'password', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[username, password])
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            responseMsg = {'msg': 'You are logged in successfully'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user and check_password(password, user.password):
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

@login_required(login_url='/user/login/')
def logoutUser(request):
    logout(request)
    responseMsg = {'msg': 'You are logged out successfully'}
    return HttpResponse(JSONRenderer().render(responseMsg))

class ForgotPassword(APIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data.get('email'))
            except User.DoesNotExist:
                responseMsg = {'msg': 'Your Mail id is not registered'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/reset-password/'+str(user.pk)+"/"+str(jwtToken)
            email_data = Email.configureResetPasswordMail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            responseMsg = {'msg': 'Password reset link is sent to your mail.'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))

class ResetPassword(APIView):
    def get(self, request, uid, token):
        response = JWTAuth.verifyToken(jwtToken=token)
        if not response:
            responseMsg = {'msg': 'Session for this token is expired!'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        responseMsg ={
            'uid':uid,
            'token':token
        }
        return HttpResponse(JSONRenderer().render(responseMsg))

    def put(self, request, uid, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.data.get('password')
            response = JWTAuth.verifyToken(jwtToken=token)
            if not response:
                responseMsg = {'msg': 'Session for this token is expired!'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            username=response.get('username')
            try:
                user = User.objects.get(username=username)
                user.set_password(raw_password=password)
                user.save()
                responseMsg = {'msg': 'Your password is reset successfully !'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            except Exception:
                responseMsg = {'msg': 'Something went wrong !'}
                return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))