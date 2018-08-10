from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Create your views here.


def signin(request):
    if request.method == 'POST':
        username = request.POST['userid']
        password = request.POST['password']
        try:
            user = auth.authenticate(username= username, password=password)
            if user is not None:
                auth.login(request, user)
                return render(request, 'welcome.html')
            else:
                messages.error(request, 'Username and password did not matched')
        except:
            pass
    return render(request, 'signin.html')


def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        return HttpResponse("invalid...", user)
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        message = "Email activation success. Please fill up the form to continue"
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form, 'message':message})
    else:
        return HttpResponse('Activation link is invalid!')


def register(request):
    return HttpResponse("You are successfully registered....")