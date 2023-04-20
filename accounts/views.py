from django.views.generic.base import TemplateView


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'
