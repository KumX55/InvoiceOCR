# from tabnanny import verbose
# from tkinter import CASCADE
# from unicodedata import category
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# from django.contrib.auth.models import User
# Create your models here.

class Facture(models.Model):
    files = models.FileField()
    date = models.DateField(default=now)
    name = models.CharField(max_length=255,default='')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    
#     class Meta:
#         ordering = ['-date']

# class Category(models.Model):
#     name = models.CharField(max_length=255)

#     class Meta:
#         verbose_name_plural = 'Categories'

#     def __str__(self):
#         return self.name
    