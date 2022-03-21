from os import name
from django.urls import path
from . import views
from .views import editFac, editFournisseur, editClient, createFour , createCli, createFacture, createProd, showFac, showProd
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('search-factures',csrf_exempt(views.search_factures),name="search-factures"),
    path('upload',csrf_exempt(views.upload),name="home"),
    path('historique',csrf_exempt(views.history),name="historique"),
    path('show/<id>',csrf_exempt(showFac.as_view()),name="show"),
    path('show_produits/<id>',csrf_exempt(views.listeProd),name="showLprod"),
    path('show_produit/<id>',csrf_exempt(showProd.as_view()),name="showProd"),
    path('créer_facture',csrf_exempt(createFacture.as_view()),name="createFacture"),
    path('créer_produit/<id>',csrf_exempt(createProd.as_view()),name="createProd"),
    path('delete/<id>',csrf_exempt(views.delete),name="deletefac"),
    path('deleteprod/<id>',csrf_exempt(views.deleteProd),name="deleteprod"),
    path('deleteAllprod/<id>',csrf_exempt(views.deleteAllProd),name="deleteAllprod"),
    path('deleteAll',csrf_exempt(views.deleteAll),name="deleteAll"),
    path('deleteToday',csrf_exempt(views.deleteToday),name="deleteToday"),
    path('contactez_fournisseur/<id>',csrf_exempt(views.contactFour),name="contactFour"),
    path('contactez_client/<id>',csrf_exempt(views.contactCli),name="contactCli"),
    path('liste_fournisseurs',csrf_exempt(views.listeFournisseurs),name="fourlist"),
    path('liste_clients',csrf_exempt(views.listeClients),name="clilist"),
    path('créer_fournisseur',csrf_exempt(createFour.as_view()),name="createFour"),
    path('créer_client',csrf_exempt(createCli.as_view()),name="createCli"),
    path('profile_fournisseur/<id>',csrf_exempt(views.profileFournisseur),name="fourprof"),
    path('profile_client/<id>',csrf_exempt(views.profileClient),name="cliprof"),
    path('modifier_fournisseur/<id>',csrf_exempt(editFournisseur.as_view()),name="editfourni"),
    path('modifier_client/<id>',csrf_exempt(editClient.as_view()),name="editclient"),
    path('deleteFournisseur/<id>',csrf_exempt(views.deleteFournisseur),name="deletefour"),
    path('deleteClient/<id>',csrf_exempt(views.deleteClient),name="deletecli"),
    path('deleteFacturesFournisseur/<id>',csrf_exempt(views.deleteFacturesFournisseur),name="deletefacfour"),
    path('deleteFacturesFournisseur/<id>',csrf_exempt(views.deleteFacturesClient),name="deletefaccli"),
    path('modifier/<id>',csrf_exempt(editFac.as_view()),name="edit") 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

