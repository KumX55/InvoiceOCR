from email import message
from fileinput import filename
import imp
from urllib import response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from unicodedata import name
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from matplotlib import image
from matplotlib.pyplot import get
from numpy import NaN
from django.core.mail import EmailMessage
from django.utils.timezone import now
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
from .encryption_utils import encrypt, decrypt
from .predictions import prediction
import re
from pdf2image import convert_from_path
from pathlib import Path
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
# ****************************************************************************************************************** #
    # **************************************Factures********************************************** #
                    # *********************************************************************** #
def pdf_to_jpg(path, filename):
    image = convert_from_path(path)
    image[0].save('./media/'+Path('./media/'+filename).stem+'.jpg','JPEG')

def clean(prida):
    for key in prida:
        if not prida[key]:
            prida[key].append(None)
    return prida
def search_factures(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        factures = Facture.objects.filter(files__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          date__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          name__icontains=search_str,owner=request.user)
        data = factures.values()
        return JsonResponse(list(data),safe=False)

# **************************************Importer Facture********************************************** #
class upload(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request):
        factures = Facture.objects.filter(owner=request.user,creation_date=datetime.now().date())
        paginator = Paginator(factures,4)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator,page_number)
        # print(prediction('/home/kumx55/Desktop/OCR-PFE/OCR-DJANGO/factures/0.jpg'))
        return render(request,'facture/upload.html',{'factures':factures, 'page_obj': page_obj})
    def post(self, request):
        factures = request.FILES.getlist('factures')
        for f in factures:
            fac = Facture.objects.create(files=f,name=f.name,owner=request.user) 
            fac.save()
            if str(fac.files).endswith('.pdf'):
                pdf_to_jpg('./media/'+str(fac.files), str(fac.files.name)) 
                fac.files = Path('./media/'+str(fac.files.name)).stem+'.jpg'
                fac.save()
            predictionsa = prediction('./media/'+str(fac.files))
            predictions = clean(predictionsa)
            #*************************** OCR ***************************************#
            fac.ref_fac = predictions['IREF'][0]
            fac.date = predictions['IDATE'][0]
            fac.total = predictions['ITOTAL'][0]
            if predictions['ISTATUS'][0] != None:
                fac.status = predictions['ISTATUS'][0]
            else:
                pass
            fac.save()
            if predictions['CNAME'][0] != None:
                c = Client.objects.create(name=predictions['CNAME'][0],adress=predictions['CADD'][0],email=predictions['CMAIL'][0],phone=predictions['CPHONE'][0],owner=request.user)
                c.save()
                fac.client = c
                fac.save()
            if predictions['FNAME'][0] !=None:
                four = Fournisseur.objects.create(name=predictions['FNAME'][0],adress=predictions['FADD'][0],email=predictions['FMAIL'][0],phone=predictions['FPHONE'][0],owner=request.user)
                four.save()
                fac.fournisseur = four
                fac.save()
            if predictions['PNAME'][0] != None:
                i = 0
                for produit in predictions['PNAME']:
                    try:
                        PPUHT = predictions['PPUHT'][i]
                    except:
                        PPUHT = None
                    try:
                        PQTY = predictions['PQTY'][i]
                    except:
                        PQTY = None
                    try:
                        PTVA = predictions['PTVA'][i]
                    except:
                        PTVA = None
                    try:
                        PTTC = predictions['PTTC'][i]
                    except:
                        PTTC = None
                    p = Produit.objects.create(name=produit,prix_u_ht=PPUHT,qty=PQTY,tva=PTVA,montant=PTTC,owner=request.user)
                    p.save()
                    fac.produit_set.add(p)
                    fac.save()
                    i += 1
            fac.save()
            #*************************** /OCR/ ************************************#
        return redirect('home')
# **************************************Visualiser Facture********************************************** #
class showFac(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        produit = Produit.objects.filter(facture=facture,owner=request.user)
        status = ['P','N','A']
        if facture.status:
            status.remove(facture.status)
        try:
            four_assoc = Fournisseur.objects.filter(owner=request.user).exclude(pk=facture.fournisseur.pk)
        except:
            four_assoc = Fournisseur.objects.filter(owner=request.user)
        try:
            cli_assoc = Client.objects.filter(owner=request.user).exclude(pk=facture.client.pk)
        except:
            cli_assoc = Client.objects.filter(owner=request.user)
        ids = []
        for i in range(0,len(produit)):
            ids.append(produit[i].name)
        p_select = Produit.objects.filter(owner=request.user).exclude(name__in=ids)
        return  render(request,'facture/show.html',{'facture':facture, "produit":produit, "status":status, "four_assoc":four_assoc, "cli_assoc":cli_assoc, 'p_select':p_select})
    def post(self, request, id):
        facture = Facture.objects.get(pk=id, owner=request.user)
        try:
            id_p = request.POST.getlist('produit')
            if id_p[0] != "":
                for i in id_p:
                    p = Produit.objects.get(pk=i, owner=request.user)
                    facture.produit_set.add(p)
        except:
            pass
        try:
            id_f = request.POST['fournisseur']
            fournisseur = Fournisseur.objects.get(owner=request.user, pk=id_f)
            facture.fournisseur = fournisseur
        except:
            pass
        try:
            id_c = request.POST['client']
            client = Client.objects.get(owner=request.user, pk=id_c)
            facture.client = client
        except:
            pass
        ref_fac = request.POST['ref_fac'] 
        date = request.POST['date']
        total = request.POST['total']
        status = request.POST['status']
        # if id_p[0] != "":
        #     for i in id_p:
        #         p = Produit.objects.get(pk=i, owner=request.user)
        #         facture.produit_set.add(p)
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
        founisseurs = Fournisseur.objects.filter(owner=request.user)
        clients = Client.objects.filter(owner=request.user)
        return render(request,'facture/create_facture.html',{"fournisseurs":founisseurs, "clients":clients})
    def post(self,request):
        jsonStr = request.POST['jsonTable']
        
        
        name = request.POST['name']
        ref_fac = request.POST['ref_fac']
        date = request.POST['date']
        total = request.POST['total']
        status = request.POST['status']
        try:
            id_f = request.POST['fournisseur']
            f = Fournisseur.objects.get(pk=id_f)
        except:
            nameF = request.POST['nameF']
            addresseF = request.POST['addresseF']
            emailF = request.POST['emailF']
            telF = request.POST['telF']
            f = Fournisseur.objects.create(name=nameF,adress=addresseF,email=emailF,phone=telF,owner=request.user)
            f.save()
        try:
            id_c = request.POST['client']
            c = Client.objects.get(pk=id_c)
        except:
            nameC = request.POST['nameC']
            addresseC = request.POST['addresseC']
            emailC = request.POST['emailC']
            telC = request.POST['telC']
            c = Client.objects.create(name=nameC,adress=addresseC,email=emailC,phone=telC,owner=request.user)
            c.save()
        facture = Facture.objects.create(name=name,owner=request.user,ref_fac=ref_fac,date=date,total=total,status=status,fournisseur=f,client=c)
        facture.save()
        prodList = json.loads(jsonStr)
        for l in range(0,len(prodList)):
            p = Produit.objects.create(name=prodList[l]['nom'],prix_u_ht=prodList[l]['prixunitairehorstaxe'],qty=prodList[l]['quantité'],tva=prodList[l]['tva'],montant=prodList[l]['montant'],owner=request.user)
            p.facture.add(facture)
            p.save()
        messages.success(request,'Facture Créé avec Succès !!')
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
    paginator = Paginator(fournisseurs,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'fournisseur/liste_fournisseurs.html',{"fournisseurs":fournisseurs , 'page_obj':page_obj})

# **************************************Profile Fournisseur********************************************** #
@login_required(login_url='/authentication/login')
def profileFournisseur(request,id): 
    fournisseur = Fournisseur.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(fournisseur=fournisseur,owner=request.user)
    paginator = Paginator(factures,6)
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
    paginator = Paginator(clients,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'client/liste_client.html',{"clients":clients, 'page_obj':page_obj})

# **************************************Profile Client********************************************** #
@login_required(login_url='/authentication/login')
def profileClient(request,id):
    client = Client.objects.get(pk=id, owner=request.user)
    factures = Facture.objects.filter(client=client,owner=request.user)
    paginator = Paginator(factures,6)
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
        p = Produit.objects.create(name=name,prix_u_ht=prix_u_ht,qty=qty,tva=tva,montant=montant,owner=request.user)
        p.facture.add(facture)
        p.save()
        messages.success(request,'Produit Créé avec succès !!')
        return redirect('show', id)
# **************************************Créer Produit********************************************** #
class AjoutProduit(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self,request):
        return render(request,'produit/create_produit_sans_facture.html')
    def post(self,request):
        name = request.POST['name']
        prix_u_ht = request.POST['prix_u_ht']
        qty = request.POST['qty']
        tva = request.POST['tva']
        montant = request.POST['montant']
        p = Produit.objects.create(name=name,prix_u_ht=prix_u_ht,qty=qty,tva=tva,montant=montant,owner=request.user)
        p.save()
        messages.success(request,'Produit Créé avec succès !!')
        return redirect('AllProd')
# **************************************Liste Produit********************************************** #
@login_required(login_url='/authentication/login')
def AllProd(request):
    produits = Produit.objects.filter(owner=request.user)
    paginator = Paginator(produits,8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'produit/liste_produits.html',{"produits":produits, 'page_obj':page_obj})
# **************************************Liste Produit Facture********************************************** #
@login_required(login_url='/authentication/login')
def listeProd(request, id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    produits = facture.produit_set.all()
    paginator = Paginator(produits,6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'produit/liste_produits_facture.html',{"facture":facture, "produits":produits, "page_obj": page_obj})
# **************************************Visualiser Produit********************************************** #
class showProd(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        produit = Produit.objects.get(pk=id, owner=request.user)
        factures = produit.facture.all()
        paginator = Paginator(factures,6)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator,page_number)
        return render(request, 'produit/profile_produit.html',{"produit":produit,'factures':factures, 'page_obj': page_obj})
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
        p.montant = montant
        p.save()
        messages.success(request,'Produit Modifié avec succès !!')
        return redirect('showProd', id)
# **************************************Modifier Produit********************************************** #
class editProd(View):
    @method_decorator(login_required(login_url='/authentication/login'))
    def get(self, request, id):
        produit = Produit.objects.get(pk=id, owner=request.user)
        facturesP = produit.facture.all()
        ids = []
        for i in range(0,len(facturesP)):
            ids.append(facturesP[i].name)
        factures = Facture.objects.filter(owner=request.user).exclude(name__in=ids)
        return render(request, 'produit/edit_produit.html',{"produit":produit, "factures":factures})
    def post(self, request, id):
        p = Produit.objects.get(pk=id, owner=request.user)
        id_f = request.POST.getlist('facture')
        name = request.POST['name']
        prix_u_ht = request.POST['prix_u_ht']
        qty = request.POST['qty']
        tva = request.POST['tva']
        montant = request.POST['montant']
        if id_f[0] != "":
            for i in id_f:
                facture = Facture.objects.get(owner=request.user,pk=i)
                p.facture.add(facture)
        p.name = name
        p.prix_u_ht = prix_u_ht
        p.qty = qty
        p.tva = tva
        p.montant = montant
        p.save()
        messages.success(request,'Produit Modifié avec succès !!')
        return redirect('showProd', id)
# **************************************Supprimer Produit********************************************** #
@login_required(login_url='/authentication/login')
def deleteProd(request, id):
    produit = Produit.objects.get(pk=id, owner=request.user)
    produit.delete()
    messages.success(request,'Produit Supprimé avec succès !!')
    return redirect("AllProd")
# **************************************Supprimer Produits********************************************** #
@login_required(login_url='/authentication/login')
def deleteAllProd(request, id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    produits = Produit.objects.filter(facture=facture, owner=request.user)
    produits.delete()
    messages.success(request,'Produits Supprimés avec succès !!')
    return redirect("show", id)
# **************************************Détacher Facture du Produit********************************************** #
def removeFacProd(request, idf, idp):
        f = Facture.objects.get(pk=idf, owner=request.user)
        produit = Produit.objects.get(pk=idp, owner=request.user)
        produit.facture.remove(f)
        #f.produit_set.remove(produit)
        messages.success(request,'Facture détachée avec succès !! ')
        return redirect('showProd', idp)

# ****************************************************************************************************** #
# *****************************************Export CSV*************************************************** #
def export_facture_csv(request,id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Facture'+facture.name+'_'+str(facture.creation_date)+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Référence', 'Date', 'Total', 'Status', 
                     'Nom Fournisseur','Addresse Fournisseur','Email Fournisseur','Tel Fournisseur',
                     'Nom Client','Addresse Client','Email Client','Tel Client',
                     'Nom Produit','Prix Unitaire Hors Taxe','Quantité','TVA','Montant',])
    
    produits = Produit.objects.filter(facture=facture, owner=request.user)

    writer.writerow([facture.name, facture.ref_fac, facture.date, facture.total, facture.status, 
                     facture.fournisseur.name,facture.fournisseur.adress,facture.fournisseur.email,facture.fournisseur.phone,
                     facture.client.name,facture.client.adress,facture.client.email,facture.client.phone,
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
    facture = Facture.objects.filter(pk=id, owner=request.user)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Facture'+facture[0].name+'_'+str(facture[0].creation_date)+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Facture')
    row_num = 0
    font_style =xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nom', 'Référence', 'Date', 'Total', 'Status', 
               'Nom Fournisseur','Addresse Fournisseur','Email Fournisseur','Tel Fournisseur',
               'Nom Client','Addresse Client','Email Client','Tel Client',
               'Nom Produit','Prix Unitaire Hors Taxe','Quantité','TVA','Montant']
    
    for  col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    rows = facture.values_list('name','ref_fac','date','total','status')

    for row in rows:
        row_num+=1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]), font_style)
    wb.save(response)
    
    return response


def export_factures_csv(request):
    factures = Facture.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Facture Tous_les_factures'+str(now)+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Référence', 'Date', 'Total', 'Status', 
                     'Nom Fournisseur','Addresse Fournisseur','Email Fournisseur','Tel Fournisseur',
                     'Nom Client','Addresse Client','Email Client','Tel Client',
                     'Nom Produit','Prix Unitaire Hors Taxe','Quantité','TVA','Montant',])
    
    for facture in factures:
            produits = Produit.objects.filter(facture=facture, owner=request.user)

            if produits:
                writer.writerow([facture.name, facture.ref_fac, facture.date, facture.total, facture.status, 
                facture.fournisseur.name,facture.fournisseur.adress,facture.fournisseur.email,facture.fournisseur.phone,
                facture.client.name,facture.client.adress,facture.client.email,facture.client.phone,
                produits[0].name,produits[0].prix_u_ht,produits[0].qty,produits[0].tva,produits[0].montant,])
            else:
                writer.writerow([facture.name, facture.ref_fac, facture.date, facture.total, facture.status, 
                facture.fournisseur.name,facture.fournisseur.adress,facture.fournisseur.email,facture.fournisseur.phone,
                facture.client.name,facture.client.adress,facture.client.email,facture.client.phone,
                '','','','','',])
            produits = produits[1:]

            for produit in produits:
                writer.writerow(['', '', '', '', '', 
                                '','','','',
                                '','','','',
                                produit.name,produit.prix_u_ht,produit.qty,produit.tva,produit.montant,])
    return response

def export_fournisseurs_csv(request):
    fournisseurs = Fournisseur.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Fournisseur Tous_les_fournisseurs'+str(now)+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Addresse', 'Email', 'Phone'])
    
    for fournisseur in fournisseurs:
                writer.writerow([fournisseur.name, fournisseur.adress, fournisseur.email, fournisseur.phone])
    return response
 
def export_clients_csv(request):
    clients = Client.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Client Tous_les_clients'+str(now)+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Addresse', 'Email', 'Phone'])
    
    for client in clients:
                writer.writerow([client.name, client.adress, client.email, client.phone])
    return response

def export_produits_csv(request):
    produits = Produit.objects.filter(owner=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Produit Tous_les_produits'+str(now)+'.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prix Unitaire hors taxe', 'Quanit', 'TVA', 'Montant'])
    
    for produit in produits:
                writer.writerow([produit.name, produit.prix_u_ht, produit.qty, produit.tva, produit.montant])
    return response
#***********************************************PDF************************************#
def export_facture_pdf(request, id):
    facture = Facture.objects.get(pk=id, owner=request.user)
    produits = facture.produit_set.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attatchment: filename=Facture'+str(facture.name)+'.pdf'
    response['Content-Transfer-Encoding'] = 'binary'


    html_string = render_to_string('facture/pdf-output.html',{'facture':facture, 'produits':produits})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output=open(output.name,'rb')
        response.write(output.read())
    
    return response