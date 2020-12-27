from django.urls import path
from .views import UserRegistration, VerifyEmail, UserLogin, logoutUser, ForgotPassword, ResetPassword

urlpatterns = [
    path('registration/', UserRegistration.as_view(), name="userRegistration"),
    path('verify-email/', VerifyEmail.as_view(), name="verifyEmail"),
    path('login/', UserLogin.as_view(), name="userLogin"),
    path('logout/', logoutUser, name="userLogout"),
    path('forgot-password/', ForgotPassword.as_view(), name="forgotPassword"),
    path('reset-password/<uid>/<token>/', ResetPassword.as_view(), name="resetPassword"),

]
