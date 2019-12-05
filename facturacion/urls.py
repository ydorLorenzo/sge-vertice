from django.urls import path, re_path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('facturacion/', views.start_template, name='Facturacion'),
    
]
