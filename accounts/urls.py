from django.urls import path
from .views import RegisterView, LoginView, logout, activate, DashboardView
from .views import ResetPassword, ForgotPassword, reset_password_validate

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', reset_password_validate,
         name='reset_password_validate'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password'),
]