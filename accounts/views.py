from django.views import View
from .forms import RegistrationForm
from .models import Account
from django.shortcuts import reverse, redirect, render
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/register.html', context={
            'form': RegistrationForm()
        })

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = Account.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=email.split('@')[0],
                email=email,
                password=form.cleaned_data['password']
            )
            user.phone_number = form.cleaned_data['phone_number']
            user.save()
            messages.success(request, 'Registration successful!')
        else:
            if form.errors.get('__all__'):
                messages.add_message(request, messages.ERROR, form.errors['__all__'])
            if form.errors.get('email'):
                messages.add_message(request, messages.ERROR, form.errors['email'])
        return redirect('accounts:register')


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user:
            auth.login(request, user)
            # messages.success(request, 'You have logged in successfully!')
            return redirect('home')
        messages.error(request, 'Invalid login credentials!')
        return redirect('accounts:login')


@login_required(login_url='accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out successfully')
    return redirect('accounts:login')
