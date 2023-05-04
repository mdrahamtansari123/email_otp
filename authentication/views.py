from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django_otp import devices_for_user
from django_otp.decorators import otp_required
from .forms import SignupForm, OTPVerificationForm
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp
import time
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser

from django.contrib.auth import logout

from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.http import HttpResponseRedirect

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp_device = TOTPDevice.objects.create(user=user, name='email')
            otp_device.save()
            
            # Generate the OTP only if it's not already in the session
          
            otp = totp(otp_device.bin_key, step=otp_device.step, t0=otp_device.t0, digits=otp_device.digits)
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            
            print(f"-----Generated OTP for {user.email}: {otp} and user_id: {user.id}-----")

            return redirect('otp_verify')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def otp_verify(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user_id = request.session.get('user_id')
            print("user_id: ", user_id)
            try:
                user = CustomUser.objects.get(pk=user_id)  # Retrieve the user using the stored ID
            except CustomUser.DoesNotExist:
                user = None

            if user is not None:
                otp_verified = False
                for device in devices_for_user(user):
                    if device.verify_token(otp):
                        otp_verified = True
                        break

                if otp_verified:
                    login(request, user)  # Log in the user
                    return HttpResponseRedirect(reverse('home'))
                else:
                    messages.error(request, 'Incorrect OTP. Please try again.')
            else:
                messages.error(request, 'Error: user not found. Please try again.')
        else: 
              messages.error(request, 'Not a valid form. Please try again.')        
        
    else:
        form = OTPVerificationForm()
    otp = request.session.get('otp', None)    
    return render(request, 'otp_verify.html', {'form': form,'otp': otp})


def home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            logout(request)
            return HttpResponseRedirect(reverse('login'))
        else:
            return render(request, 'home.html')
    else:
        return redirect('login')
    
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            
            auth_login(request, form.get_user())
            return redirect('home')
        else: 
            messages.error(request, 'Error: user not found. Please try again.')
                
    else:
        form = AuthenticationForm()
 
    return render(request, 'login.html', {'form': form})