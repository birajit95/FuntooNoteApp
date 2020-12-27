from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_active']

    def validate_password(self, password):
        return make_password(password)

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
        if data.get('password') != data.get('password'):
            raise serializers.ValidationError("Password does not match!")
        elif len(data.get('password')) < 6:
            raise serializers.ValidationError("Password length must be 6 or above")
        return data
