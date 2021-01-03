from django.urls import path
from .views import UserRegistration, VerifyEmail, UserLogin,\
    UserLogOut, ForgotPassword, ResetPassword, UserProfile, ChangePassword, UpdateProfilePictureAPI

urlpatterns = [
    path('registration/', UserRegistration.as_view(), name="userRegistration"),
    path('verify-email/', VerifyEmail.as_view(), name="verifyEmail"),
    path('login/', UserLogin.as_view(), name="userLogin"),
    path('logout/', UserLogOut.as_view(), name="userLogout"),
    path('forgot-password/', ForgotPassword.as_view(), name="forgotPassword"),
    path('reset-password/<uid>/<token>/', ResetPassword.as_view(), name="resetPassword"),
    path('profile/',UserProfile.as_view(), name='userProfile'),
    path('profile/upload_profile_pic/', UpdateProfilePictureAPI.as_view(), name='userProfilePic'),
    path('change-password/', ChangePassword.as_view(), name='changePassword'),

]
