from django.views.generic.base import TemplateView
from django.shortcuts import reverse


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'


class LoginView(TemplateView):
    template_name = 'accounts/login.html'


def logout(request):
    return reverse('home')
