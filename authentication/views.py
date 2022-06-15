from ast import Try
from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
# from matplotlib.pyplot import cla
# from matplotlib.style import use
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
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



# **************************************Validation du nom d'utilisateur********************************************** #
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username=data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'le nom d`utilisateur ne doit contenir que des caractères alphanumériques'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Désolé nom d`utilisateur en cours d`utilisation, choisissez-en un autre'},status=409)
        return JsonResponse({'username_valid':True})

# **************************************Validation d'email********************************************** #
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email=data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'L`adresse email n`est pas valide'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Désolé adresse email en cours d`utilisation, choisissez-en un autre'},status=409)
        return JsonResponse({'email_valid':True})

# **************************************Inscription********************************************** #
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
                    messages.warning(request,'Mot de passe trop court !!')
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active= False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))


                domain = get_current_site(request).domain
                link=reverse('activate',kwargs={'uidb64': uidb64, 'token':token_generator.make_token(user)})

                activate_url = 'http://'+domain+link

                email_subject = 'Activez votre compte'
                email_body = 'Salut '+user.username+ ' Veuillez utiliser ce lien pour vérifier votre compte\n' + activate_url
                mail = EmailMessage(
                    email_subject,
                    email_body,
                    "RecFac",
                    [email],
                )
                mail.send(fail_silently=False)
                messages.success(request,'Compte créé avec succès !! Vérifiez votre email')
                return render(request, 'authentication/register.html')
        return render(request, 'authentication/register.html')

# **************************************Vérification du lien d'activation********************************************** #
class VerificationView(View):
    def get(self ,request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('lgin'+'?message='+'Utilisateur déjà activé!!')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request,'Compte activé avec succès !!')
            return render(request, 'authentication/login.html')

        except Exception as ex:
            pass
        
        return redirect('login')

# **************************************Login********************************************** #
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
                    messages.success(request,'Bienvenue '+user.username+ ' Vous êtes maintenant connecté !!')
                    if user.is_superuser:
                        return redirect('/admin')
                    else:
                        return redirect('home')
                messages.warning(request,'Compte n`est pas activé, verifiez votre email !!')
                return render(request,'authentication/login.html')    
            messages.warning(request,'Informations d`identification non valides, réessayez!')
            return render(request,'authentication/login.html')
        messages.warning(request,'Veuillez remplir tous les champs!')
        return render(request,'authentication/login.html')

# **************************************Logout********************************************** #
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request,'Déconnexion réussie')
        return render(request,'authentication/login.html')

# **************************************Mot de passe Oublié********************************************** #
class RequestPasswordView(View):
    def get(self, request):
        return render(request,'authentication/reset-password.html')
    def post(self, request):
        email = request.POST['email']
        context = {
            'values':request.POST
        }
        if not validate_email(email):
            messages.warning(request,'Veuillez saisir une adresse email valide')
            return render(request,'authentication/reset-password.html',context)

        userr = User.objects.filter(email=email)

        if userr.exists():
           
            user = userr[0]
            uidb64 =  urlsafe_base64_encode(force_bytes(user.pk))
            domain =  get_current_site(request).domain
            
            link = reverse('reset-user-password', kwargs={'uidb64':uidb64,'token':PasswordResetTokenGenerator().make_token(user)})
            reset_url = 'http://'+domain+link

            email_subject = 'Réinitialisation du mot de passe'
            email_body = 'Salut, Veuillez utiliser ce lien pour réinitialiser votre mot de passe\n' + reset_url
            mail = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [email],
            )
            mail.send(fail_silently=False)
        messages.success(request,'Nous vous avons envoyé un email !!')
        return render(request,'authentication/reset-password.html')

# **************************************Reset Mot de Passe********************************************** #
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
                messages.info(request,'Le lien de réinitialisation du mot de passe n`est pas valide, veuillez en demander un nouveau')
                return render(request,'authentication/reset-password.html')
            return render(request,'authentication/set-new-password.html',context)    
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
            messages.warning(request,'Le mot de passe ne correspond pas')
            return render(request,'authentication/set-new-password.html',context)
        if len(password) < 6:
            messages.warning(request,'Mot de passe trop court')
            return render(request,'authentication/set-new-password.html',context)
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Réinitialisation du mot de passe avec succès !!')
            return redirect('login')
        except Exception as identifier:
            messages.info(request,'Quelque chose s`est mal passé, réessayez')
            return render(request,'authentication/set-new-password.html',context)


        # return render(request,'authentication/set-new-password.html',context)

# **************************************Profile Utilisateur********************************************** #
class ProfileView(View): 
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request):
        u = request.user
        username = u.username
        email = u.email
        return render(request,'authentication/profile.html',{'user':u})
    def post(self, request):
        u = request.user
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']
        if password != confirm:
            messages.warning(request,'Vérifiez les champs de mot de passe !!')
            return redirect('profile')
        elif password == "":
            u.username = username
            u.email = email
            u.save()
            messages.success(request,'Compte modifié avec succès !!')
            auth.logout(request)
            return redirect('login')
        else:
            u.username = username
            u.email = email
            u.set_password(password)
            u.save()
            messages.success(request,'Compte modifié avec succès !!')
            auth.logout(request)
            return redirect('login')

# **************************************Supprimer compte utilisateur********************************************** #
class DeleteAccount(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request):
        messages.success(request,'Compte supprimé !!')
        return redirect('login')
    def post(self, request):
        user = request.user
        user.delete()
        messages.success(request,'Compte supprimé !!')
        return redirect('login')