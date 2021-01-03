from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from .serialyzer import UserSerializer, ResetPasswordSerializer,\
    ForgotPasswordSerializer, UserLoginSerializer, UserProfileSerializer,\
    ChangePasswordSerializer, UserDataSerializer, UserProfileDataSerializer, UserProfilePicSerializer
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
from rest_framework.generics import GenericAPIView
from .models import TokenBlackLists
from .models import Profile
from django.utils.decorators import method_decorator
import os

class UserRegistration(GenericAPIView):
    serializer_class =  UserSerializer
    def get(self, request):
        return render(request, "userRegistrration.html")

    @swagger_auto_schema(responses={200: UserSerializer()})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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
    token = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    @swagger_auto_schema(manual_parameters=[token])
    def get(self, request):
        jwtToken = request.GET.get('token')
        try:
            blacklist_token = TokenBlackLists.objects.get(token=jwtToken)
        except TokenBlackLists.DoesNotExist:
            blacklist_token = None
        if blacklist_token is None:
            response = JWTAuth.verifyToken(jwtToken=jwtToken)
            if not response:
                responseMsg = {'msg': 'Session for this token is expired!'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            username = response.get('username')
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
            TokenBlackLists(token=jwtToken).save()
            responseMsg = {'msg': 'Your account is activated! Now you can log in'}
            return HttpResponse(JSONRenderer().render(responseMsg))
        responseMsg = {'msg': 'This link is no valid longer'}
        return HttpResponse(JSONRenderer().render(responseMsg))

class UserLogin(GenericAPIView):
    serializer_class = UserLoginSerializer
    @swagger_auto_schema(responses={200: UserLoginSerializer()})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                redirect_url = request.GET.get('next')
                if redirect_url:
                    return redirect(redirect_url)
                return redirect('/notes/')
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
        return HttpResponse(JSONRenderer().render(serializer.errors))

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserLogOut(APIView):
    def get(self, request):
        logout(request)
        responseMsg = {'msg': 'You are logged out successfully'}
        return HttpResponse(JSONRenderer().render(responseMsg))


class ForgotPassword(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    @swagger_auto_schema(responses={200: ForgotPasswordSerializer()})
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

class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    def get(self, request, uid, token):
        try:
            blacklist_token = TokenBlackLists.objects.get(token=token)
        except TokenBlackLists.DoesNotExist:
            blacklist_token = None
        if blacklist_token is None:
            response = JWTAuth.verifyToken(jwtToken=token)
            if not response:
                responseMsg = {'msg': 'Session for this token is expired!'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            responseMsg = {
                'uid': uid,
                'token': token
            }
            return HttpResponse(JSONRenderer().render(responseMsg))
        responseMsg = {'msg':'This link is no valid longer'}
        return HttpResponse(JSONRenderer().render(responseMsg))

    def put(self, request, uid, token):
        serializer = self.serializer_class(data=request.data)
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
                TokenBlackLists(token=token).save()
                responseMsg = {'msg': 'Your password is reset successfully !'}
                return HttpResponse(JSONRenderer().render(responseMsg))
            except Exception:
                responseMsg = {'msg': 'Something went wrong !'}
                return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserProfile(GenericAPIView):
    serializer_class = UserProfileDataSerializer
    def get(self, request):
        user = User.objects.get(pk=request.user.pk)
        userSerializer = dict(UserDataSerializer(user).data)
        profileSerializer = UserProfileSerializer(request.user.profile)
        userSerializer.update(profileSerializer.data)
        return HttpResponse(JSONRenderer().render(userSerializer))

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                profile = Profile.objects.get(user=request.user.pk)
                user = User.objects.get(pk=request.user.pk)
                profile.bio = serializer.data.get('bio')
                profile.dob = serializer.data.get('dob')
                profile.save()
                user.first_name = serializer.data.get('firstName')
                user.last_name = serializer.data.get('lastName')
                user.save()
                responseMsg = {'msg': "Your Profile is updated"}
            except Profile.DoesNotExist:
                responseMsg = {'msg':"Some error occured"}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))


@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UpdateProfilePictureAPI(GenericAPIView):
    serializer_class = UserProfilePicSerializer
    def put(self, request):
        img = request.FILES['image']
        serializer = self.serializer_class(data={'image':img})
        serializer.is_valid(raise_exception=True)
        request.user.profile.image = img
        request.user.profile.save()
        return HttpResponse(JSONRenderer().render("Uploaded"))


    def delete(self, request):
        image_name = request.user.profile.image.name
        if image_name != 'profile_pics/default.jpg':
            media_dir = "/WebApplicationsUsingDjango/FundooNotes/FuntooNote/media/"
            actual_path = os.path.join(os.getcwd(), media_dir,image_name )
            os.remove(actual_path)
            request.user.profile.image = 'profile_pics/default.jpg'
            request.user.profile.save()
            return HttpResponse(JSONRenderer().render({'msg': "Profile picture is deleted"}))
        return HttpResponse(JSONRenderer().render({'msg':'No image to be deleted'}))


@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class ChangePassword(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(pk=request.user.pk)
            if check_password(serializer.data.get('old_password'), user.password):
                user.set_password(raw_password=serializer.data.get('password'))
                user.save()
                responseMsg = {'msg': "Your password is changed"}
                return HttpResponse(JSONRenderer().render(responseMsg))
            responseMsg = {'msg': "Old password does not match!"}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render({'msg': serializer.errors["non_field_errors"][0]}))
