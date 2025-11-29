from django.urls import path
from . import views

app_name = 'user_control'

urlpatterns = [
    # Authentication endpoints
    path('api/v1/auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/v1/auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/v1/auth/refresh/', views.RefreshTokenAPIView.as_view(), name='refresh'),
    path('api/v1/auth/logout/', views.LogoutAPIView.as_view(), name='logout'),

    # User profile endpoints
    path('api/v1/users/profile/', views.ProfileRetrieveAPIView.as_view(), name='profile_retrieve'),
    path('api/v1/users/profile/update/', views.ProfileUpdateAPIView.as_view(), name='profile_update'),

    # Signature and authentication endpoints
    path('api/v1/users/signature/upload/', views.SignatureUploadAPIView.as_view(), name='signature_upload'),
    path('api/v1/users/pin/setup/', views.PINSetupAPIView.as_view(), name='pin_setup'),
    path('api/v1/users/2fa/setup/', views.TwoFactorSetupAPIView.as_view(), name='two_factor_setup'),
]
