from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from .forms import RegistrationForm
from django.shortcuts import reverse


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = 'home'


class LoginView(TemplateView):
    template_name = 'accounts/login.html'


def logout(request):
    return reverse('home')
