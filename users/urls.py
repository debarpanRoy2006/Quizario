from django.urls import path
from .views import (
    register_user, 
    login_user, 
    logout_user, 
    PasswordResetRequestAPI, 
    PasswordResetConfirmAPI
)

urlpatterns = [
    path('register/', register_user, name="register"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),
    
    # URLs for the password reset flow
    path('reset-password/', PasswordResetRequestAPI.as_view(), name="reset_password_request"),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmAPI.as_view(), name='password_reset_confirm'),
]   