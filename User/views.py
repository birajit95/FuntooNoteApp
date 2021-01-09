from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from .serialyzer import UserSerializer, ResetPasswordSerializer,\
    ForgotPasswordSerializer, UserLoginSerializer, UserProfileSerializer,\
    ChangePasswordSerializer, UserDataSerializer, UserProfileDataSerializer, UserProfilePicSerializer
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
from rest_framework import status
from rest_framework.response import Response
from FuntooNote.FuntooNote.logger import logger

class UserRegistration(GenericAPIView):
    serializer_class =  UserSerializer
    @swagger_auto_schema(responses={200: UserSerializer()})
    def post(self, request):
        """
        This api is for user registration to this application

        @param request: user registration data like username, email, password, firstname, lastname
        @return: account verification link to registered email once registration is successful
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.data.get('username'))
            user.is_active = False
            user.save()
            logger.info(f"{user.username} is registered")
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/verify-email/'
            email_data = Email.configureEmail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            logger.info(f'Account activation link is sent to {user.email}')
            msg= "Your account is created and a confirmation mail is sent to your mail for account activation"
            return Response({'response_msg':msg, 'response_data':jwtToken},status = status.HTTP_201_CREATED)
        logger.error(serializer.errors)
        return Response({'response_msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(APIView):
    token = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    @swagger_auto_schema(manual_parameters=[token])
    def get(self, request):
        """
        This Api verifies the user email and jwt token sent to the email and activates the account
        @param request: Get request hits with jwt token which contains user information
        @return: Account activation confirmation
        """
        jwtToken = request.GET.get('token')
        try:
            blacklist_token = TokenBlackLists.objects.get(token=jwtToken)
        except TokenBlackLists.DoesNotExist:
            blacklist_token = None
        if blacklist_token is None:
            response = JWTAuth.verifyToken(jwtToken=jwtToken)
            if not response:
                msg = 'Session for this token is expired!'
                logger.info('token session expired!')
                return Response({'response_msg':msg}, status=status.HTTP_401_UNAUTHORIZED)
            username = response.get('username')
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
            TokenBlackLists(token=jwtToken).save()
            msg = 'Your account is activated! Now you can log in'
            logger.info(f"{user.username}'s account is activated")
            return Response({'response_msg':msg}, status=status.HTTP_200_OK)
        msg = 'This link is no valid longer'
        logger.info('This link is already used')
        return Response({'response_msg':msg}, status=status.HTTP_403_FORBIDDEN)

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
                msg = 'Your account is not active. Please activate your account from the link shared in your mail'
                return Response({'response_msg':msg}, status=status.HTTP_100_CONTINUE)
            msg = 'Bad Credential found'
            return Response({'response_msg':msg}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserLogOut(APIView):
    def get(self, request):
        logout(request)
        msg = 'You are logged out successfully'
        return Response({'response_msg':msg},status=status.HTTP_204_NO_CONTENT)


class ForgotPassword(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    @swagger_auto_schema(responses={200: ForgotPasswordSerializer()})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data.get('email'))
            except User.DoesNotExist:
                msg = 'Your Mail id is not registered'
                return Response({'response_msg':msg}, status=status.HTTP_404_NOT_FOUND)
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/reset-password/'+str(user.pk)+"/"+str(jwtToken)
            email_data = Email.configureResetPasswordMail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            msg = 'Password reset link is sent to your mail.'
            return Response({'response_msg':msg, 'response_data':jwtToken}, status=status.HTTP_100_CONTINUE)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
                msg = 'Session for this token is expired!'
                return Response({'response_msg':msg},status=status.HTTP_401_UNAUTHORIZED)
            responseMsg = {
                'uid': uid,
                'token': token
            }
            return Response({'response_msg':responseMsg}, status=status.HTTP_200_OK)
        msg = 'This link is no valid longer'
        return Response({'response_msg':msg},status=status.HTTP_403_FORBIDDEN)

    def put(self, request, uid, token):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.data.get('password')
            response = JWTAuth.verifyToken(jwtToken=token)
            if not response:
                msg = 'Session for this token is expired!'
                return Response({'response_msg':msg}, status=status.HTTP_403_FORBIDDEN)
            username=response.get('username')
            try:
                user = User.objects.get(username=username)
                user.set_password(raw_password=password)
                user.save()
                TokenBlackLists(token=token).save()
                msg = 'Your password is reset successfully !'
                return Response({'response_msg':msg}, status=status.HTTP_200_OK)
            except Exception:
                msg = 'Something went wrong !'
                return Response({'response_msg':msg}, status=status.HTTP_403_FORBIDDEN)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserProfile(GenericAPIView):
    serializer_class = UserProfileDataSerializer
    def get(self, request):
        user = User.objects.get(pk=request.user.pk)
        userSerializer = dict(UserDataSerializer(user).data)
        profileSerializer = UserProfileSerializer(request.user.profile)
        userSerializer.update(profileSerializer.data)
        return Response({'response_msg':userSerializer},status=status.HTTP_200_OK)

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
                msg = "Your Profile is updated"
                return Response({'response_msg':msg},status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                msg = "Some error occurred"
            return Response({'response_msg': msg}, status=status.HTTP_403_FORBIDDEN)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UpdateProfilePictureAPI(GenericAPIView):
    serializer_class = UserProfilePicSerializer
    def put(self, request):
        if request.FILES:
            img = request.FILES['image']
            serializer = self.serializer_class(data={'image':img})
            serializer.is_valid(raise_exception=True)
            old_image_name = request.user.profile.image.name
            if old_image_name != 'profile_pics/default.jpg':
                actual_path = os.path.join(os.getcwd(), 'media', old_image_name)
                os.remove(actual_path)
            request.user.profile.image = img
            request.user.profile.save()
            return Response({'response_msg':'Your profile picture is uploaded'}, status=status.HTTP_200_OK)
        return Response({'response_msg':'select a file'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        image_name = request.user.profile.image.name
        if image_name != 'profile_pics/default.jpg':
            actual_path = os.path.join(os.getcwd(), 'media',image_name )
            os.remove(actual_path)
            request.user.profile.image = 'profile_pics/default.jpg'
            request.user.profile.save()
            return Response({'response_msg': "Profile picture is deleted"}, status=status.HTTP_200_OK)
        return Response({'response_msg':'No image to be deleted'}, status=status.HTTP_400_BAD_REQUEST)


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
                msg = "Your password is changed"
                return Response({'response_msg':msg}, status=status.HTTP_200_OK)
            msg = "Old password does not match!"
            return Response({'response_msg':msg}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'msg': serializer.errors["non_field_errors"][0]}, status=status.HTTP_400_BAD_REQUEST)
