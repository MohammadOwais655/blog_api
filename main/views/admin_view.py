from django.contrib.admin import AdminSite
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.urls import path
from django.urls.resolvers import URLResolver
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django import forms
import pyotp
import qrcode
from io import BytesIO
import base64
import os
from ..models import User
from ..utils import generate_otp_secret


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)


class CustomAdminSite(AdminSite):
    # login_form = AuthenticationForm()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('login/', self.login, name='login'),
            path('two_factor_auth/', self.setup_two_factor, name='two_factor_auth'),
            path('otp/', self.otp_verification, name='otp_verification')
        ]

        return custom_urls + urls
    
    def generate_qr_code(self, secret, email):
        otp = pyotp.TOTP(secret)
        uri = otp.provisioning_uri(name=email, issuer_name="Blog App")
        qr = qrcode.make(uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return qr_code_base64
    
    def setup_two_factor(self, request):
        print("Request Method: ", request.method)
        print("Request User: ", request.user)
        if request.method == "POST":
            user_id = request.session.get('user_id')
            try:
                user = User.objects.get(pk = user_id)
            except User.DoesNotExist:

                return redirect('admin:login')
            print(user)
            if not user.is_two_factor_auth:
                secret = pyotp.random_base32()
                # user.two_factor_secret = secret
                print(secret)
                user.is_two_factor_auth = True
                user.secret_key = secret
                user.save()
                qr_code = self.generate_qr_code(secret, user.email)
                # qr_code_data = mark_safe(qr_code.encode('base64'))
                return render(request, 'setup_two_factor.html', {'qr_code': qr_code})
            else:
                return render(request, 'setup_two_factor.html')
        else:
            return render(request, 'setup_two_factor.html')
        


    def login(self, request, extra_context=None):
        print(f"Request method: {request.method}")
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = authenticate(request, email=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None and user.is_staff:
                    request.session['user_id'] = user.id
                    if user.is_two_factor_auth:
                        return redirect('admin:otp_verification')
                    else:
                        return redirect('admin:two_factor_auth')
            else:
                form = AuthenticationForm()
                context = self.each_context(request)
                context['form'] = form
                context.update(extra_context or {})
                return render(request, 'admin/login.html', context)
        else:
            form = AuthenticationForm()
            print("GET request, displaying form")

        context = self.each_context(request)
        context['form'] = form
        context.update(extra_context or {})
        return render(request, 'admin/login.html', context)
        

    def otp_verification(self, request):
        print("otp_verificatio method: ", request.method)
        if request.method == 'POST':
            otp = request.POST.get('otp')
            print("otp ",otp)
            user_id = request.session.get('user_id')
            try:
                user = User.objects.get(pk = user_id)
                otp_obj = pyotp.TOTP(user.secret_key)
                if otp_obj.verify(otp):
                    print("otp_verified")
                    auth_login(request, user)
                    return redirect('admin:index')
                else:
                    messages.error(request, 'invalid otp')
                    return redirect('admin:otp_verification')
            except OTP.DoesNotExist:
                pass
            # return render(request, 'otp.html', {'error': 'Invalid OTP code'})
        # form = OTPVerificationForm()
        return render(request, 'otp.html')
    

admin_site = CustomAdminSite()