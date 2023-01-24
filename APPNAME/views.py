from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

import random

from django.core.mail import send_mail

from cryptography.fernet import Fernet
from mechanize import Browser

from .models import Password

import favicon

br = Browser()
br.set_handle_robots(False)
fernet = Fernet(settings.KEY.encode())


def home(request):

    if request.method == 'POST':
        if 'signup-form' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            # if password are not identical

            if password != password2:
                msg = f"Please make sure you are using the same password!!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

            # if username is exist 

            elif User.objects.filter(username=username).exists():
                msg = f"{username} already exists!!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

            elif User.objects.filter(email=email).exists():
                msg = f"{email} already exists!!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)


            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username = username, password = password)
                
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username} thanks for subscribing!!"
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)

        elif 'logout' in request.POST:
            msg = f"{request.user} you logged out"
            logout(request)
           
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)


        elif 'login-form' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            new_login = authenticate(request, username = username, password = password)
            
            if new_login is None:
                msg = f" Login failed ! make sure you're using the right a/c"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

            else:
                code = str(random.randint(100000, 999999))

                global global_code

                global_code = code

                send_mail(
                    "Django Password Manager: confirm email",
                    f"Your verification code is {code}.",
                    settings.EMAIL_HOST_USER,
                    [new_login.email],
                    fail_silently=False,
                )

                return render(request, 'home.html', 
                {
                    'code' : code,
                    'user' : new_login,
                })


        elif 'confirm' in request.POST:
            input_code = request.POST.get('code')
            user = request.POST.get('user')

            if input_code != global_code:
                msg = f"{input_code} is wrong!! "
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)

            else:
                login(request, User.objects.get(username=user))
                msg = f"{request.user} welcome again!! "
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)


        elif 'add-password' in request.POST:
            url = request.POST.get('url')
            email = request.POST.get('email')
            password = request.POST.get('password')


            # encrypation

            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())

            # get the title of website

            br.open(url)
            # title = br.title()
            title = "aivi"

            # get the logo URL

            try:
                icon = favicon.get(url)[0].url
            except:
                icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"

            print('\n\n\n')
            print(encrypted_email)
            print(encrypted_password)
            print(title)
            print(icon)    


            new_pass = Password.objects.create(
                user = request.user,
                name = title,
                password = encrypted_password.decode(),

                email = encrypted_email.decode(), 
                logo = icon
            )

            msg = f"{title} added successfully !! "
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)

        elif "delete" in request.POST:
                to_delete = request.POST.get("password-id")
                msg = f"{Password.objects.get(id=to_delete).name} deleted."
                Password.objects.get(id=to_delete).delete()
                messages.success(request, msg)
                return HttpResponseRedirect(request.path)

    

    context = {}
    if request.user.is_authenticated:
        passwords = Password.objects.all().filter(user=request.user)     
        for password in passwords:
            password.email = fernet.decrypt(password.email.encode()).decode()
            password.password = fernet.decrypt(password.password.encode()).decode()
            # password.save()

        context = {
            "passwords" : passwords,

        }


    return render(request, "home.html", context)