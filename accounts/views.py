from django.views import View
from django.views.generic.base import TemplateView
from .forms import RegistrationForm
from .models import Account
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please, activate your account!'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you! We have sent a verification '
            #                           'link to your email address. Please, verify it!')
            return redirect(f'/accounts/login/?command=verification&email={email}')
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
            messages.success(request, 'You have logged in successfully!')
            return redirect('accounts:dashboard')
        messages.error(request, 'Invalid login credentials!')
        return redirect('accounts:login')


@login_required(login_url='accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out successfully')
    return redirect('accounts:login')


def activate(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    try:
        user = Account._default_manager.get(id=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account has been activated!')
        return redirect('accounts:login')
    messages.error(request, 'Invalid activation link!')
    return redirect('accounts:register')


def reset_password_validate(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    try:
        user = Account._default_manager.get(id=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please, reset your password!')
        return redirect('accounts:reset_password')
    messages.error(request, 'This link has been expired!')
    return redirect('accounts:login')


class ForgotPassword(View):
    def get(self, request):
        return render(request, 'accounts/forgot_password.html')

    def post(self, request):
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password!'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,
                             'Password reset email has been sent '
                             'to your email address!')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('accounts:forgot_password')


class ResetPassword(View):
    def get(self, request):
        return render(request, 'accounts/reset_password.html')

    def post(self, request):
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('accounts:login')
        messages.error(request, 'Password does not match!')
        return redirect('accounts:reset_password')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
