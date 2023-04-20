from django.views.generic.base import TemplateView


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'


class LoginView(TemplateView):
    template_name = 'accounts/login.html'
