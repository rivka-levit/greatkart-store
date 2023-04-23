from django.urls import path
from .views import RegisterView, LoginView, logout, activate, DashboardView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
