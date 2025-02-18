from django.urls import path

from .views import dashboard, login_view, logout_view, registro, resumo_carteira

urlpatterns = [
    path("registro/", registro, name="registro"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("resumo-carteira/", resumo_carteira, name="resumo_carteira"),
    
]
