from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from .forms import RegistrationForm
from .models import Account
from django.shortcuts import reverse, redirect


class RegisterView(CreateView):
    model = Account
    template_name = 'accounts/register.html'
    form_class = RegistrationForm

    def post(self, request, *args, **kwargs):
        super(RegisterView, self).post(request)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()
        return redirect('accounts:login')


class LoginView(TemplateView):
    template_name = 'accounts/login.html'


def logout(request):
    return reverse('home')
