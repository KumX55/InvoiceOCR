from email import message
import imp
from tkinter import W
from django.utils.decorators import method_decorator
from unicodedata import name
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from numpy import NaN
from django.core.mail import EmailMessage

from .models import Facture, Fournisseur, Client, Produit
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator
import os
import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import csv
import xlwt

# ****************************************************************************************************************** #
    # **************************************Factures********************************************** #
                    # *********************************************************************** #
def search_factures(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        factures = Facture.objects.filter(files__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          date__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          name__icontains=search_str,owner=request.user)
        data = factures.values()
        return JsonResponse(list(data),safe=False)

# **************************************Importer Facture********************************************** #
@login_required(login_url='/authentication/login')
def upload(request):
    # if request.method == 'GET':
    #     f = Fournisseur.objects.create(name="Wiki",adress="03 rue Beji matrix",email="Wiki@gmail.com",phone="98030303",owner=request.user)
    #     f.save()
    #     c = Client.objects.create(name="Wiki matrix 2",adress="03 rue Taher hadded",email="Icon@gmail.com",phone="54245862",owner=request.user)
    #     c.save()
    #     facture = Facture.objects.create(name="Deuxième Facture",owner=request.user,ref_fac="F-889-R652",date="25/06/2022",total="8500TND",status="P",fournisseur=f,client=c)
    #     facture.save()
    #     p1 = Produit.objects.create(name="Gun M16",prix_u_ht=6756,qty=1,tva="10%",montant=6349,facture=facture,owner=request.user)
    #     p1.save()
    #     p2 = Produit.objects.create(name="Dell G15",prix_u_ht=6875,qty=1,tva="15%",montant=8220,facture=facture,owner=request.user)
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

# **************************************Visualiser Facture********************************************** #
class showFac(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        produit = Produit.objects.filter(facture=facture,owner=request.user)
        return  render(request,'facture/show.html',{'facture':facture, "produit":produit})
    def post(self, request, id):
        facture = Facture.objects.get(pk=id)
        ref_fac = request.POST['ref_fac'] 
        date = request.POST['date']
        total = request.POST['total']
        status = request.POST['status']
        facture.ref_fac = ref_fac
        facture.date = date
        facture.total = total
        facture.status = status
        facture.save()
        messages.success(request, 'Facture Modifiée avec succès !!')
        return redirect('show', id)
# **************************************Supprimer Facture********************************************** #
@login_required(login_url='/authentication/login')
def delete(request,id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    facture.delete()
    messages.success(request,'Facture supprimée !!')
    return redirect('home')

# **************************************Supprimer tous les Factures********************************************** #
@login_required(login_url='/authentication/login')
def deleteAll(request):
    factures = Facture.objects.filter(owner=request.user)
    factures.delete()
    messages.success(request,'Factures supprimé !!')
    return redirect('home')

# **************************************Supprimer tous les Factures d'aujourd'hui********************************************** #
@login_required(login_url='/authentication/login')
def deleteToday(request):
    factures = Facture.objects.filter(owner=request.user,creation_date=datetime.now().date())
    factures.delete()
    messages.success(request,'Factures supprimé !!')
    return redirect('home')

# **************************************Historique des Factures********************************************** #
@login_required(login_url='/authentication/login')
def history(request):
    factures = Facture.objects.filter(owner=request.user)
    paginator = Paginator(factures,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'facture/tous.html',{'factures':factures, 'page_obj': page_obj})

# **************************************Modifier Facture********************************************** #
class editFac(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        return render(request,'facture/edit.html',{'facture':facture})
    def post(self, request, id):
        file = request.FILES.getlist('facture')
        name = request.POST['name']
        facture = Facture.objects.get(pk=id, owner=request.user)

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

# **************************************Créer Facture********************************************** #
class createFacture(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request):
        return render(request,'facture/create_facture.html')
    def post(self,request):
       name = request.POST['name']
       ref_fac = request.POST['ref_fac']
       date = request.POST['date']
       total = request.POST['total']
       status = request.POST['status']
       nameF = request.POST['nameF']
       addresseF = request.POST['addresseF']
       emailF = request.POST['emailF']
       telF = request.POST['telF']
       nameC = request.POST['nameC']
       addresseC = request.POST['addresseC']
       emailC = request.POST['emailC']
       telC = request.POST['telC']
       f = Fournisseur.objects.create(name=nameF,adress=addresseF,email=emailF,phone=telF,owner=request.user)
       f.save()
       c = Client.objects.create(name=nameC,adress=addresseC,email=emailC,phone=telC,owner=request.user)
       c.save()
       facture = Facture.objects.create(name=name,owner=request.user,ref_fac=ref_fac,date=date,total=total,status=status,fournisseur=f,client=c)
       facture.save()
       messages.success(request,'Facture Créé avec succès !!')
       return redirect('historique')

# ****************************************************************************************************************** #
    # **************************************Fournisseurs Et Clients********************************************** #
                    # *********************************************************************** #
# Fournisseur
    # Fournisseur
    # Fournisseur
# Fournisseur
@login_required(login_url='/authentication/login')
def listeFournisseurs(request):
    fournisseurs = Fournisseur.objects.filter(owner=request.user)
    return render(request,'fournisseur/liste_fournisseurs.html',{"fournisseurs":fournisseurs})

# **************************************Profile Fournisseur********************************************** #
@login_required(login_url='/authentication/login')
def profileFournisseur(request,id): 
    fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(fournisseur=fournisseur,owner=request.user)
    paginator = Paginator(factures,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'fournisseur/profile_fournisseur.html',{"fournisseur":fournisseur, "factures":factures, 'page_obj': page_obj})


# **************************************Créer Client********************************************** #
class createFour(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request):
        return render(request,'fournisseur/create_fournisseur.html')
    def post(self,request):
        name = request.POST['name']
        adress = request.POST['addresse']
        email = request.POST['email']
        phone = request.POST['tel']
        f = Fournisseur.objects.create(name=name,adress=adress,email=email,phone=phone,owner=request.user)
        f.save()
        messages.success(request,'Fournisseur Créé avec succès !!')
        return redirect('fourlist')

# **************************************supprimer fournisseur********************************************** #
@login_required(login_url='/authentication/login')
def deleteFournisseur(request,id):
    fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
    fournisseur.delete()
    messages.success(request,'Fournisseur supprimé avec succès !!')
    return redirect('fourlist')

# **************************************supprimer factures fournisseur********************************************** #
@login_required(login_url='/authentication/login')
def deleteFacturesFournisseur(request,id):
    fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(owner=request.user,fournisseur=fournisseur)
    factures.delete()
    messages.success(request,'Factures supprimé avec succès !!')
    return redirect('fourprof',id)


# **************************************Modifier Fournisseur********************************************** #
class editFournisseur(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request,id):
        fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
        return render(request,'fournisseur/edit_fournisseur.html',{"fournisseur":fournisseur})
    def post(self,request,id):
        fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
        name = request.POST['name']
        adress = request.POST['addresse']
        email = request.POST['email']
        phone = request.POST['tel']
        fournisseur.name = name
        fournisseur.adress = adress
        fournisseur.email = email
        fournisseur.phone = phone
        fournisseur.save()
        messages.success(request,'Fournisseur Modifié avec succès !!')
        return redirect('editfourni',id)


# Client
    # Client
    # Client
# Client
@login_required(login_url='/authentication/login')
def listeClients(request):
    clients = Client.objects.filter(owner=request.user)
    return render(request,'client/liste_client.html',{"clients":clients})

# **************************************Profile Client********************************************** #
@login_required(login_url='/authentication/login')
def profileClient(request,id):
    client = Client.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(client=client,owner=request.user)
    paginator = Paginator(factures,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'client/profile_client.html',{"client":client, "factures":factures, 'page_obj': page_obj})


# **************************************Créer Client********************************************** #
class createCli(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request):
        return render(request,'client/create_client.html')
    def post(self,request):
        name = request.POST['name']
        adress = request.POST['addresse']
        email = request.POST['email']
        phone = request.POST['tel']
        c = Client.objects.create(name=name,adress=adress,email=email,phone=phone,owner=request.user)
        c.save()
        messages.success(request,'Client Créé avec succès !!')
        return redirect('clilist')
 
# **************************************supprimer client********************************************** #
@login_required(login_url='/authentication/login')
def deleteClient(request,id):
    client = Client.objects.get(pk=id, owner=request.user)
    client.delete()
    messages.success(request,'Client supprimé avec succès !!')
    return redirect('clilist')

# **************************************supprimer factures client********************************************** #
@login_required(login_url='/authentication/login')
def deleteFacturesClient(request,id):
    client = Client.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(owner=request.user,client=client)
    factures.delete()
    messages.success(request,'Factures supprimé avec succès !!')
    return redirect('cliprof',id)

# **************************************Modifier Client********************************************** #
class editClient(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request,id):
        client = Client.objects.get(pk=id, owner=request.user)
        return render(request,'client/edit_client.html',{"client":client})
    def post(self,request,id):
        client = Client.objects.get(pk=id, owner=request.user)
        name = request.POST['name']
        adress = request.POST['addresse']
        email = request.POST['email']
        phone = request.POST['tel']
        client.name = name
        client.adress = adress
        client.email = email
        client.phone = phone
        client.save()
        messages.success(request,'Client Modifié avec succès !!')
        return redirect('editclient',id)
# **************************************Contactez Fournisseur********************************************** #
@login_required(login_url='/authentication/login')
def contactFour(request,id):
    if request.method == "POST":
        user = request.user
        fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
        emailF = fournisseur.email
        emailU = user.email
        nameU = user.username
        message = request.POST['message']
        subject = request.POST['subject']
        coord = request.POST['coord']

        email_body = 'Message de : '+nameU+'\n'+ 'Son adresse email : '+emailU+'\nMessage : \n'+message+ '\n' + 'Ses coordonnées : '+coord+" ."
        mail = EmailMessage(
            subject,
            email_body,
            'recfac@Contact.com',
            [emailF],
        )
        mail.send(fail_silently=False)
        messages.success(request,'Message bien envoyé !!')
        return redirect('fourprof', id)
# **************************************Contactez Client********************************************** #
@login_required(login_url='/authentication/login')
def contactCli(request,id):
    if request.method == "POST":
        user = request.user
        client = Client.objects.get(pk=id, owner=request.user)
        emailC = client.email
        emailU = user.email
        nameU = user.username
        message = request.POST['message']
        subject = request.POST['subject']
        coord = request.POST['coord']

        email_body = 'Message de : '+nameU+'\n'+ 'Son adresse email : '+emailU+'\nMessage : \n'+message+ '\n' + 'Ses coordonnées : '+coord+" ."
        mail = EmailMessage(
            subject,
            email_body,
            'recfac@Contact.com',
            [emailC],
        )
        mail.send(fail_silently=False)
        messages.success(request,'Message bien envoyé !!')
        return redirect('cliprof', id)
# **************************************Créer Produit********************************************** #
class createProd(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request,id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        return render(request,'produit/create_produit.html',{"facture":facture})
    def post(self,request,id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        name = request.POST['name']
        prix_u_ht = request.POST['prix_u_ht']
        qty = request.POST['qty']
        tva = request.POST['tva']
        montant = request.POST['montant']
        p = Produit.objects.create(name=name,prix_u_ht=prix_u_ht,qty=qty,tva=tva,montant=montant,facture=facture,owner=request.user)
        p.save()
        messages.success(request,'Produit Créé avec succès !!')
        return redirect('show', id)
# **************************************Créer Produit********************************************** #
@login_required(login_url='/authentication/login')
def listeProd(request, id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    produits = Produit.objects.filter(facture=facture, owner=request.user)
    paginator = Paginator(produits,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'produit/liste_produits_facture.html',{"facture":facture, "produits":produits, "page_obj": page_obj})
# **************************************Visualiser/Modifier Produit********************************************** #
class showProd(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        produit = Produit.objects.get(pk=id, owner=request.user)
        return render(request, 'produit/profile_produit.html',{"produit":produit})
    def post(self, request, id):
        p = Produit.objects.get(pk=id, owner=request.user)
        name = request.POST['name']
        prix_u_ht = request.POST['prix_u_ht']
        qty = request.POST['qty']
        tva = request.POST['tva']
        montant = request.POST['montant']
        p.name = name
        p.prix_u_ht = prix_u_ht
        p.qty = qty
        p.tva = tva
        p.montantp = montant
        p.save()
        messages.success(request,'Produit Modifié avec succès !!')
        return redirect('showProd', id)
# **************************************Supprimer Produit********************************************** #
@login_required(login_url='/authentication/login')
def deleteProd(request, id):
    produit = Produit.objects.get(pk=id, owner=request.user)
    produit.delete()
    messages.success(request,'Produit Supprimé avec succès !!')
    return redirect("home")
# **************************************Supprimer Produits********************************************** #
@login_required(login_url='/authentication/login')
def deleteAllProd(request, id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    produits = Produit.objects.filter(facture=facture, owner=request.user)
    produits.delete()
    messages.success(request,'Produits Supprimés avec succès !!')
    return redirect("show", id)

# ****************************************************************************************************** #
# *****************************************Export CSV*************************************************** #
def export_facture_csv(request,id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Facture'+facture.name+'_'+facture.creation_date+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Référence', 'Date', 'Total', 'Status', 
                     'Nom Fournisseur','Addresse Fournisseur','Email Fournisseur','Tel Fournisseur',
                     'Nom Client','Addresse Client','Email Client','Tel Client',
                     'Nom Produit','Prix Unité Hors Taxi','Quantité','TVA','Montant',])
    
    produits = Produit.objects.filter(facture=facture, owner=request.user)

    writer.writerow([facture.name, facture.ref_fac, facture.date, facture.total, facture.status, 
                     facture.fournisseur.name,facture.fournisseuradress,facture.fournisseuremail,facture.fournisseurphone,
                     facture.client.name,facture.clientadress,facture.clientemail,facture.clientphone,
                     produits[0].name,produits[0].prix_u_ht,produits[0].qty,produits[0].tva,produits[0].montant,])
    
    produits = produits[1:]

    for produit in produits:
        writer.writerow(['', '', '', '', '', 
                        '','','','',
                        '','','','',
                        produit.name,produit.prix_u_ht,produit.qty,produit.tva,produit.montant,])
    return response
# *****************************************Export Excel*************************************************** #
def export_facture_excel(request,id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Facture'+facture.name+'_'+facture.creation_date+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Facture')
    row_num = 0
    font_style =xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nom', 'Référence', 'Date', 'Total', 'Status', 
               'Nom Fournisseur','Addresse Fournisseur','Email Fournisseur','Tel Fournisseur',
               'Nom Client','Addresse Client','Email Client','Tel Client',
               'Nom Produit','Prix Unité Hors Taxi','Quantité','TVA','Montant',]
    
    for  col_num in range(len(columns)):
        ws.wrtie(row_num, col_num, columns[col_num], font_style)

    rows = facture.values_list()

    return response