from django.urls import path
from .views import UserRegistration, VerifyEmail, UserLogin, logoutUser

urlpatterns = [
    path('registration/', UserRegistration.as_view(), name="userRegistration"),
    path('verify-email/', VerifyEmail.as_view(), name="verifyEmail"),
    path('login/', UserLogin.as_view(), name="userLogin"),
    path('logout/', logoutUser, name="userLogout"),
]
