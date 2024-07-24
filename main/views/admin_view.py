from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.urls import path
from django.urls.resolvers import URLResolver
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django import forms
import os
from ..models import OTP


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)


class CustomAdminSite(AdminSite):
    # login_form = AuthenticationForm()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('login/', self.login, name='login'),
            path('otp/', self.otp_verification, name='otp_verification')
        ]

        return custom_urls + urls

    def login(self, request, extra_context=None):
        print(f"Request method: {request.method}")
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(request, email=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None and user.is_staff:
                    otp_code = get_random_string(length=6, allowed_chars='0123456789')
                    print("otp code: ", otp_code)
                    otp = OTP.objects.create(user=user, otp=otp_code)
                    otp.save()
                    mail_res = send_mail(
                        'Your OTP Code',
                        f'Your OTP code is {otp_code}',
                        os.getenv('EMAIL'),
                        [user.email]
                    )
                    request.session['otp_user_id'] = user.id
                    return redirect('admin:otp_verification')
                
        else:
            form = AuthenticationForm()
            print("GET request, displaying form")

        context = self.each_context(request)
        context['form'] = form
        context.update(extra_context or {})
        return render(request, 'admin/login.html', context)
        

    def otp_verification(self, request):
        if request.method == 'POST':
            form = OTPVerificationForm(data=request.POST)
            user_id = request.session.get('otp_user_id')
            if form.is_valid():
                try:
                    otp = OTP.objects.get(user_id=user_id, otp=form.cleaned_data['otp'])
                    if otp.is_valid():
                        user = otp.user
                        auth_login(request, user)
                        otp.delete()  # Optionally delete the OTP after successful login
                        return redirect('admin:index')
                except OTP.DoesNotExist:
                    pass
                return render(request, 'otp.html', {'error': 'Invalid OTP code'})
        form = OTPVerificationForm()
        return render(request, 'otp.html', {'form': form})
    

admin_site = CustomAdminSite()