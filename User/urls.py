from django.urls import path
from .views import UserRegistration, VerifyEmail

urlpatterns = [
    path('registration/', UserRegistration.as_view(), name="userRegistration"),
    path('verify-email/', VerifyEmail.as_view(), name="verifyEmail"),

]
