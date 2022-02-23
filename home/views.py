from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.core.mail import EmailMessage

# Create your views here.

class HomeView(View):
    def get(self, request):
        return render(request,'index.html')
    def post(self, request):
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        email_subject = subject

        email_body = 'Message de : '+name+'\n'+ 'Son adresse email : '+email+'\nMessage : \n'+message
        mail = EmailMessage(
            email_subject,
            email_body,
            'noreply@semycolon.com',
            ['degla996@gmail.com'],
        )
        mail.send(fail_silently=False)
        messages.success(request,'Message bien envoyé !! nous vous contacterons bientôt')
        return render(request, 'index.html')


# def index(request):
#     return render(request,'index.html')
