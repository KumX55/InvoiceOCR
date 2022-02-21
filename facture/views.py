import imp
from unicodedata import name
from django.shortcuts import render
from .models import Facture
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
        incomes = Facture.objects.filter(files__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          date__icontains=search_str,owner=request.user) | Facture.objects.filter(
                                          name__icontains=search_str,owner=request.user)
        data = incomes.values()
        return JsonResponse(list(data),safe=False)

@login_required(login_url='/authentication/login')
def upload(request):
    if request.method == 'POST':
        factures = request.FILES.getlist('factures')
        for f in factures:
            Facture.objects.create(files=f,name=f.name,owner=request.user)
    factures = Facture.objects.filter(owner=request.user)
    paginator = Paginator(factures,4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    return render(request,'facture/upload.html',{'factures':factures, 'page_obj': page_obj})