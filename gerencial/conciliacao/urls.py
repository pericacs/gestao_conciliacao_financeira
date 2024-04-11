from django.contrib import admin
from django.urls import path
from conciliacao.views import carregar_csv

app_name = 'conciliacao'

urlpatterns = [
    # path('', index, name='index'),
    # path('', views.DashBoardLista.as_view(), name='index'),
    path('carregar_csv/', carregar_csv, name='carregar_csv'),
    
]