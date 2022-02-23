from unicodedata import name
from django.urls import path
from .views import HomeView
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path('',csrf_exempt(HomeView.as_view()),name="index"),
]