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
import sys
sys.path.append("..")
from FuntooNote.logger import logger

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
        """
        This API is used to authenticate user to access resources
        @param request: user credential like username and password
        @return: Redirects to all notes url on successful login
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                logger.info(f"{username} is authenticated")
                login(request, user)
                logger.info(f"{username} is logged in")
                redirect_url = request.GET.get('next')
                if redirect_url:
                    logger(f'Redirects to {redirect_url}')
                    return redirect(redirect_url)
                logger.info(f'Redirects to /notes/')
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
                logger.info(f"{username}'s account is not active, activation mail is sent to {user.email}")
                msg = 'Your account is not active. Please activate your account from the link shared in your mail'
                return Response({'response_msg':msg}, status=status.HTTP_100_CONTINUE)
            msg = 'Bad Credential found'
            logger.error(f"Credential failure for {username}")
            return Response({'response_msg':msg}, status=status.HTTP_401_UNAUTHORIZED)
        logger.error(serializer.errors)
        return Response({'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserLogOut(APIView):
    def get(self, request):
        """
        This api is for user log out
        @return: release all resources from user on logged out
        """
        logout(request)
        msg = 'You are logged out successfully'
        logger.info(f"{request.user.username} is logged out")
        return Response({'response_msg':msg},status=status.HTTP_204_NO_CONTENT)


class ForgotPassword(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    @swagger_auto_schema(responses={200: ForgotPasswordSerializer()})
    def post(self, request):
        """
        This api is used to send reset password request to server
        @param request: user registered email id
        @return: sends a password reset link to user validated email id
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data.get('email'))
            except User.DoesNotExist:
                msg = 'Your Mail id is not registered'
                logger.info(f"{serializer.data.get('email')} is not registered")
                return Response({'response_msg':msg}, status=status.HTTP_404_NOT_FOUND)
            jwtToken = JWTAuth.getToken(user.username, user.password)
            current_site = get_current_site(request).domain
            relative_url = 'user/reset-password/'+str(user.pk)+"/"+str(jwtToken)
            email_data = Email.configureResetPasswordMail(jwtToken, user, current_site, relative_url)
            Email.sendEmail(email_data)
            msg = 'Password reset link is sent to your mail.'
            logger.info(f'password reset link is sent to {user.email}')
            return Response({'response_msg':msg, 'response_data':jwtToken}, status=status.HTTP_100_CONTINUE)
        logger.error(serializer.errors)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    def get(self, request, uid, token):
        """
        This api accepts the get request hit from the email on clicked on link
        @param : user id and token
        @return: user id and token after verification
        """
        try:
            blacklist_token = TokenBlackLists.objects.get(token=token)
        except TokenBlackLists.DoesNotExist:
            blacklist_token = None
        if blacklist_token is None:
            response = JWTAuth.verifyToken(jwtToken=token)
            if not response:
                msg = 'Session for this token is expired!'
                logger.info('Token session expired!')
                return Response({'response_msg':msg},status=status.HTTP_401_UNAUTHORIZED)
            responseMsg = {
                'uid': uid,
                'token': token
            }
            return Response({'response_msg':responseMsg}, status=status.HTTP_200_OK)
        logger.info('This token is already used!')
        msg = 'This link is no valid longer'
        return Response({'response_msg':msg},status=status.HTTP_403_FORBIDDEN)

    def put(self, request, uid, token):
        """
        This API is used to reset user password
        @param: uid and token fetched for get request
        @return: reset user password
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.data.get('password')
            response = JWTAuth.verifyToken(jwtToken=token)
            if not response:
                msg = 'Session for this token is expired!'
                logger.info('Token session expired!')
                return Response({'response_msg':msg}, status=status.HTTP_403_FORBIDDEN)
            username=response.get('username')
            try:
                user = User.objects.get(username=username)
                user.set_password(raw_password=password)
                user.save()
                TokenBlackLists(token=token).save()
                msg = 'Your password is reset successfully !'
                logger.info(f"{username}'s password reset successfully")
                return Response({'response_msg':msg}, status=status.HTTP_200_OK)
            except Exception as e:
                msg = 'Something went wrong !'
                logger.error(e)
                return Response({'response_msg':msg}, status=status.HTTP_403_FORBIDDEN)
        logger.error(serializer.errors)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UserProfile(GenericAPIView):
    serializer_class = UserProfileDataSerializer
    def get(self, request):
        """
        This api is used to fetch user profile
        @return: User profile data
        """
        user = User.objects.get(pk=request.user.pk)
        userSerializer = dict(UserDataSerializer(user).data)
        profileSerializer = UserProfileSerializer(request.user.profile)
        userSerializer.update(profileSerializer.data)
        logger.info(f"{request.user.username}'s profile is accessed")
        return Response({'response_msg':userSerializer},status=status.HTTP_200_OK)

    def put(self, request):
        """
        This API is used to update user profile
        @param: user profile data
        @return: updates user profile
        """
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
                logger.info(f"{user.username}'s profile is updated")
                return Response({'response_msg':msg},status=status.HTTP_200_OK)
            except Profile.DoesNotExist as e:
                msg = "Some error occurred"
                logger.error(e)
            return Response({'response_msg': msg}, status=status.HTTP_403_FORBIDDEN)
        logger.error(serializer.errors)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class UpdateProfilePictureAPI(GenericAPIView):
    serializer_class = UserProfilePicSerializer
    def put(self, request):
        """
        This api is used to update user profile picture
        @param: profile picture
        @return: updates profile picture
        """
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
            logger.info(f"{request.user.username}'s profile picture is updated")
            return Response({'response_msg':'Your profile picture is uploaded'}, status=status.HTTP_200_OK)
        logger.error("Blank image filed is found on put request")
        return Response({'response_msg':'select a file'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        """
        This API is used to delete current profile picture and reset to default
        @return:
        """
        image_name = request.user.profile.image.name
        if image_name != 'profile_pics/default.jpg':
            actual_path = os.path.join(os.getcwd(), 'media',image_name )
            os.remove(actual_path)
            request.user.profile.image = 'profile_pics/default.jpg'
            request.user.profile.save()
            logger.info(f"{request.user.username}'s profile picture is deleted")
            return Response({'response_msg': "Profile picture is deleted"}, status=status.HTTP_200_OK)
        logger.info("No profile picture is found to be deleted")
        return Response({'response_msg':'No image to be deleted'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class ChangePassword(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    def put(self, request):
        """
        This API is used to change user password
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(pk=request.user.pk)
            if check_password(serializer.data.get('old_password'), user.password):
                user.set_password(raw_password=serializer.data.get('password'))
                user.save()
                msg = "Your password is changed"
                logger.info(f"{user.username}'s password changed")
                return Response({'response_msg':msg}, status=status.HTTP_200_OK)
            msg = "Old password does not match!"
            logger.warning(f"{user.username}'s old password does not match")
            return Response({'response_msg':msg}, status=status.HTTP_401_UNAUTHORIZED)
        logger.error(serializer.errors)
        return Response({'msg': serializer.errors["non_field_errors"][0]}, status=status.HTTP_400_BAD_REQUEST)
