from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.listar_ativos, name='listar_ativos'),
    path('cadastrar/', views.cadastrar_ativo, name='cadastrar_ativo'),
    path('atualizar/<int:pk>/', views.atualizar_ativo, name='atualizar_ativo'),
    path('excluir/<int:pk>/', views.excluir_ativo, name='excluir_ativo'),
    path('autocomplete-tickers/', views.autocomplete_tickers, name='autocomplete_tickers'),
]
