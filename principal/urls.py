from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('home_principal/', login_required(views.home_principal), name='home_principal')
    ]
