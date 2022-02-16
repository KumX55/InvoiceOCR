from ast import Try
from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from matplotlib.pyplot import cla
from matplotlib.style import use
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.urls import reverse
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import   urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator



class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username=data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Sorry username in use, choose another one'},status=409)
        return JsonResponse({'username_valid':True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email=data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Sorry email in use, choose another one'},status=409)
        return JsonResponse({'email_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        #GET USER DATA
        #Validate
        #CREATE USER ACCOUNT
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }
            
        

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.warning(request,'Password Too Short !!')
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active= False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))


                domain = get_current_site(request).domain
                link=reverse('activate',kwargs={'uidb64': uidb64, 'token':token_generator.make_token(user)})

                activate_url = 'http://'+domain+link

                email_subject = 'Activate your account'
                email_body = 'Hi'+user.username+ 'Please use this link to verify your account\n' + activate_url
                mail = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@semycolon.com',
                    [email],
                )
                mail.send(fail_silently=False)
                messages.success(request,'Account Successfullt Created !!')
                return render(request, 'authentication/register.html')
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self ,request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('lgin'+'?message='+'User already activated !!')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request,'Account activated successfully !!')
            return render(request, 'authentication/login.html')

        except Exception as ex:
            pass
        
        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username,password=password)
            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome '+user.username+ ' Your are now logged in !!')
                    return redirect('expenses')
                messages.warning(request,'Account is not active, please check you email !!')
                return render(request,'authentication/login.html')    
            messages.warning(request,'Invalid credentials, try again!')
            return render(request,'authentication/login.html')
        messages.warning(request,'Please Fill all fields!')
        return render(request,'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request,'Successfully Logged Out')
        return redirect('login')

class RequestPasswordView(View):
    def get(self, request):
        return render(request,'authentication/reset-password.html')
    def post(self, request):
        email = request.POST['email']
        context = {
            'values':request.POST
        }
        if not validate_email(email):
            messages.warning(request,'Please enter a valid email')
            return render(request,'authentication/reset-password.html',context)

        userr = User.objects.filter(email=email)

        if userr.exists():
           
            user = userr[0]
            uidb64 =  urlsafe_base64_encode(force_bytes(user.pk))
            domain =  get_current_site(request).domain
            
            link = reverse('reset-user-password', kwargs={'uidb64':uidb64,'token':PasswordResetTokenGenerator().make_token(user)})
            reset_url = 'http://'+domain+link

            email_subject = 'Password reset'
            email_body = 'Hi there, Please use this link to reset your password\n' + reset_url
            mail = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [email],
            )
            mail.send(fail_silently=False)
        messages.success(request,'We have sent you an email !!')
        return render(request,'authentication/reset-password.html')

class CompletePasswordreset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request,'Password reset Link is ivalid, please request a new one')
                return render(request,'authentication/reset-password.html')
            messages.success(request,'Password reset successfully !!')
            return redirect('login')
        except Exception as identifier:
            pass
        return render(request,'authentication/set-new-password.html',context)
    def post(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        if password != confirm_password:
            messages.warning(request,'Password does not match')
            return render(request,'authentication/set-new-password.html',context)
        if len(password) < 6:
            messages.warning(request,'Password too short')
            return render(request,'authentication/set-new-password.html',context)
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfully !!')
            return redirect('login')
        except Exception as identifier:
            messages.info(request,'Something went wrong, try again')
            return render(request,'authentication/set-new-password.html',context)


        # return render(request,'authentication/set-new-password.html',context)
        