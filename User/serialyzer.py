from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Profile
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def validate_password(self, password):
        return make_password(password)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered! Try with different one")
        return email

class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class ResetPasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(min_length=6)
    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password does not match!")
        elif len(data.get('password')) < 6:
            raise serializers.ValidationError("Password length must be 6 or above")
        return data

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=4)
    password = serializers.CharField(min_length=6)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio','dob','image']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=6)
    password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError('Password does not match!')
        return data

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileDataSerializer(serializers.Serializer):
    firstName = serializers.CharField(max_length=30, min_length=0)
    lastName = serializers.CharField(max_length=150, min_length=0)
    bio = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    dob = serializers.DateField(allow_null=True)

    def validate_dob(self, dob):
        if dob > date.today():
            raise serializers.ValidationError("Invalid Date of Birth")
        return dob

class UserProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']