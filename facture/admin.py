from django.contrib import admin
from .models import Facture, Fournisseur, Client, Produit
# Register your models here.
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('name','creation_date','adress','email','phone','owner')
    search_fields = ['name','creation_date','adress','email','phone']
    list_per_page = 12
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name','creation_date','adress','email','phone','owner')
    search_fields = ['name','creation_date','adress','email','phone']
    list_per_page = 12
class FactureAdmin(admin.ModelAdmin):
    list_display = ('name','creation_date','owner','ref_fac','date','total','status','fournisseur','client')
    search_fields = ['name','creation_date','owner','ref_fac','date','total','status','fournisseur','client']
    list_per_page = 12
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('name','creation_date','prix_u_ht','qty','tva','montant','owner')
    search_fields = ['name','creation_date','prix_u_ht','qty','tva','montant','owner']
    list_per_page = 12
admin.site.register(Facture,FactureAdmin)
admin.site.register(Fournisseur,FournisseurAdmin)
admin.site.register(Client,ClientAdmin)
admin.site.register(Produit,ProduitAdmin)
