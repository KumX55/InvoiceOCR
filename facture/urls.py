from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('search-factures',csrf_exempt(views.search_factures),name="search-factures"),
    path('upload',csrf_exempt(views.upload),name="home")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

