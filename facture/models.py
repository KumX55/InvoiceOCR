# from tabnanny import verbose
# from tkinter import CASCADE
# from unicodedata import category
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# from django.contrib.auth.models import User
# Create your models here.

# **************************************Fournisseur********************************************** #
class Fournisseur(models.Model):
    creation_date = models.DateField(default=now)
    name = models.CharField(max_length=255, null=True)
    adress = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-pk']

# **************************************Client********************************************** #
class Client(models.Model):
    creation_date = models.DateField(default=now)
    name = models.CharField(max_length=255, null=True)
    adress = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-pk']

# **************************************Facture********************************************** #
class Facture(models.Model):
    FACTURE_STATUS = (
        ('P', 'Payée'),
        ('N', 'Non-Payée'),
        ('A', 'Avance Donnée'),
    )
    files = models.FileField()
    creation_date = models.DateField(default=now)
    name = models.CharField(max_length=255,null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    ref_fac = models.CharField(max_length=255, null=True)
    date = models.CharField(max_length=255, null=True)
    total = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True, choices=FACTURE_STATUS, default='P')
    fournisseur = models.ForeignKey(to=Fournisseur, null=True, on_delete=models.CASCADE)
    client = models.ForeignKey(to=Client, null=True, on_delete=models.CASCADE)
    class Meta:
        ordering = ['-pk']

# **************************************Produit********************************************** #
class Produit(models.Model):
    creation_date = models.DateField(default=now)
    name = models.CharField(max_length=255, null=True)
    prix_u_ht = models.CharField(max_length=255, null=True)
    qty = models.CharField(max_length=255, null=True)
    tva = models.CharField(max_length=255, null=True)
    montant = models.CharField(max_length=255, null=True)
    facture = models.ManyToManyField(Facture)
    owner = models.ForeignKey(to=User, null=True,on_delete=models.CASCADE)
    def __str__(self):
        return self.name    
    class Meta:
        ordering = ['-pk']

#     class Meta:
#         ordering = ['-date']

# class Category(models.Model):
#     name = models.CharField(max_length=255)

#     class Meta:
#         verbose_name_plural = 'Categories'

#     def __str__(self):
#         return self.name
    