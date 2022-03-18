from os import name
from django.urls import path
from . import views
from .views import editFac, editFournisseur, editClient, createFour , createCli
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('search-factures',csrf_exempt(views.search_factures),name="search-factures"),
    path('upload',csrf_exempt(views.upload),name="home"),
    path('historique',csrf_exempt(views.history),name="historique"),
    path('show/<id>',csrf_exempt(views.show),name="show"),
    path('delete/<id>',csrf_exempt(views.delete),name="deletefac"),
    path('deleteAll',csrf_exempt(views.deleteAll),name="deleteAll"),
    path('deleteToday',csrf_exempt(views.deleteToday),name="deleteToday"),
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
    path('deleteFacturesFournisseur/<id>',csrf_exempt(views.deleteFacturesFournisseur),name="deletefaccli"),
    path('modifier/<id>',csrf_exempt(editFac.as_view()),name="edit") 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

