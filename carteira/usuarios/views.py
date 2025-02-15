from ativos.models import Ativo
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("dashboard")
        else:
            messages.error(request, "Erro no formulário. Por favor, verifique os dados inseridos.")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "usuarios/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    ativos = Ativo.objects.all()
    return render(request, 'usuarios/dashboard.html', {'ativos': ativos})
