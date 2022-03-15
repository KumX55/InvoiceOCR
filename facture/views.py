from email import message
import imp
from unicodedata import name
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from numpy import NaN
from .models import Facture, Fournisseur, Client, Produit
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
import os
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
# @login_required(login_url='/authentication/login')
# def index(request):
#     return render(request,'appbase.html')
def search_factures(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        factures = Facture.objects.filter(files__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          date__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          name__icontains=search_str,owner=request.user)
        data = factures.values()
        return JsonResponse(list(data),safe=False)

@login_required(login_url='/authentication/login')
def upload(request):
    # if request.method == 'GET':
    #     f = Fournisseur.objects.create(name="Mytek",adress="03 rue habib bourguiba",email="hello@gmail.com",phone="55445851",owner=request.user)
    #     f.save()
    #     c = Client.objects.create(name="Mytek matrix 2",adress="04 rue habib bourguiba",email="byebye@gmail.com",phone="99856321",owner=request.user)
    #     c.save()
    #     facture = Facture.objects.create(name="Facture Test",owner=request.user,ref_fac="F-2598-TT8",date="17/07/2000",tva="20%",total="4500TND",status="P",fournisseur=f,client=c)
    #     facture.save()
    #     p1 = Produit.objects.create(name="Zephyrus M16",price=6349,facture=facture,owner=request.user)
    #     p1.save()
    #     p2 = Produit.objects.create(name="Zephyrus G15",price=8269,facture=facture,owner=request.user)
    #     p2.save()
    if request.method == 'POST':
        factures = request.FILES.getlist('factures')
        for f in factures:
            Facture.objects.create(files=f,name=f.name,owner=request.user)
    factures = Facture.objects.filter(owner=request.user,creation_date=datetime.now().date())
    paginator = Paginator(factures,4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'facture/upload.html',{'factures':factures, 'page_obj': page_obj})

def show(request,id):
    facture = Facture.objects.get(pk=id)
    return  render(request,'facture/show.html',{'facture':facture})
def delete(request,id):
    facture = Facture.objects.get(pk=id)
    facture.delete()
    messages.success(request,'Facture supprimée !!')
    return redirect('home')
def deleteAll(request):
    factures = Facture.objects.filter(owner=request.user)
    factures.delete()
    messages.success(request,'Factures supprimé !!')
    return redirect('home')
def deleteToday(request):
    factures = Facture.objects.filter(owner=request.user,creation_date=datetime.now().date())
    factures.delete()
    messages.success(request,'Factures supprimé !!')
    return redirect('home')

def history(request):
    factures = Facture.objects.filter(owner=request.user)
    paginator = Paginator(factures,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'facture/tous.html',{'factures':factures, 'page_obj': page_obj})

class editFac(View):
    def get(self, request, id):
        facture = Facture.objects.get(pk=id)
        return render(request,'facture/edit.html',{'facture':facture})
    def post(self, request, id):
        file = request.FILES.getlist('facture')
        name = request.POST['name']
        facture = Facture.objects.get(pk=id)

        try:
            facture.files = file[0]
            facture.name = name
            facture.save()
            messages.success(request,'Facture Modifiée avec succès !!')
            return redirect('edit',id) 
        except Exception as identifier:
            facture.name = name
            facture.save()
            messages.success(request,'Facture Modifié avec succès !!')
            return redirect('edit',id) 

def listeFournisseurs(request):
    return render(request,'fournisseur/liste_fournisseurs.html')

def listeClients(request):
    return render(request,'client/liste_client.html')

def profileFournisseur(request):
    return render(request,'fournisseur/profile_fournisseur.html')

def profileClient(request):
    return render(request,'client/profile_client.html')

def editFournisseur(request):
    return render(request,'fournisseur/edit_fournisseur.html')
def editClient(request):
    return render(request,'client/edit_client.html')