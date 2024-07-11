from unicodedata import name
from django.urls import path

from .views import (
        AdminRegisterView,
        LoginUserView,
        LogoutApiView,
        PasswordResetConfirm,
        PasswordResetRequestView,
        RegisterAndBookWalkInView,
        RegisterView,
        RegisterWalkInView,
        SetNewPasswordView,
        TestingAuthenticatedReq,
        UserByPhoneView,
        UsersView,
        VerifiedUserDetailsView, 
        VerifyUserEmail,
        UserView,
        VerificationView,
        AdminLoginView
       )
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
        #AUTH ROUTES
        path('auth/token-refresh', TokenRefreshView.as_view(), name='token_refresh'),
        path('auth/login', LoginUserView.as_view(), name='login-user'),
        path('auth/logout', LogoutApiView.as_view(), name='logout'),
        #path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
        #path('get-something/', TestingAuthenticatedReq.as_view(), name='just-for-testing'),
        path('password-reset', PasswordResetRequestView.as_view(), name='password-reset'),
        path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
        path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
        
        #USER ROUTES
        #path('accounts/register-walk-in-user', RegisterWalkInView.as_view(), name='register-walkin'),
        path('accounts/register-walk-in-user', RegisterAndBookWalkInView.as_view(), name='register-walkin'),
        
        path('accounts/register-user', RegisterView.as_view(), name='register-user'),
        path('accounts/register-admin', AdminRegisterView.as_view(), name='register-admin'),
        path('accounts/login-admin', AdminLoginView.as_view(), name='login-admin'),
        path('accounts/user', UserView.as_view(), name='user'),
        path('accounts/verified-user-details/<str:user_id>', VerifiedUserDetailsView.as_view(), name='user'),
        path('accounts/users', UsersView.as_view(), name='user'),
        path('accounts/user-by-phone/<str:mobile>', UserByPhoneView.as_view(), name='user-by-phone'),
        path('accounts/verify-user-by-phone/<str:mobile>', VerificationView.as_view(), name='verify-user-by-phone')
    ]