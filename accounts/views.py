from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from carts.models import CartItem
from carts.views import get_cart
from orders.models import Order
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import requests

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

            # Create user profile
            user_profile = UserProfile(user=user)
            user_profile.profile_picture = 'default/default_avatar.jpg'
            user_profile.save()

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

        # Group with existing items in profile
        if user:
            cart = get_cart(request)
            cart_items = CartItem.objects.filter(cart=cart)
            user_items = CartItem.objects.filter(user=user)
            if cart_items.exists():
                u_items_to_del = list()
                for item in cart_items:         # Loop through anonymous user items
                    if user_items.exists():
                        for u_item in user_items:   # Loop through authenticated user items

                            # Find the same item with the same variations
                            if u_item.product == item.product and \
                                    sorted(list(u_item.variations.all()),
                                           key=lambda x: x.variation_category) == \
                                    sorted(list(item.variations.all()),
                                           key=lambda x: x.variation_category):

                                # Quantity of both identical items to one of them
                                item.quantity += u_item.quantity
                                u_items_to_del.append(u_item)
                                break

                    # Assign item to user
                    item.user = user
                    item.save()

                # Delete duplicates whose quantity has been assigned to user items
                if u_items_to_del:
                    for ui in u_items_to_del:
                        ui.delete()
            auth.login(request, user)
            messages.success(request, 'You have logged in successfully!')
            url = request.META.get('HTTP_REFERER')
            query = requests.utils.urlparse(url).query
            if query:
                params = dict(x.split('=') for x in query.split('&'))
                if 'redirect_to' in params:
                    return redirect(params['redirect_to'])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_count'] = Order.objects.filter(
            user=self.request.user,
            is_ordered=True
        ).count()
        return context


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'accounts/my_orders.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return super(MyOrdersView, self).get_queryset().filter(
            user=self.request.user,
            is_ordered=True
        )


class ProfileView(View):
    def get(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'user_profile': user_profile
        }
        return render(request, 'accounts/profile.html', context)

    def post(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
        messages.error(request, 'Invalid input! Please, check your information.')
        return redirect('accounts:profile')
