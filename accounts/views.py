from django.views.generic.base import TemplateView
from django.views import View
from django.views.generic.edit import CreateView
from .forms import RegistrationForm
from .models import Account
from django.shortcuts import reverse, redirect, render


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/register.html', context={
            'form': RegistrationForm()
        })

    def post(self, request, *args, **kwargs):
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
        return redirect('home')


class LoginView(TemplateView):
    template_name = 'accounts/login.html'


def logout(request):
    return reverse('home')
