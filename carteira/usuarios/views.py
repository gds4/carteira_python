from ativos.models import Ativo
from ativos.views import calcular_dividendos
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect, render
import plotly.express as px
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


from .forms import RegistroForm


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("dashboard")
        else:
            messages.error(request, "Erro no formulário.")
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


# @login_required
# def dashboard(request):
#     ativos = Ativo.objects.all()
#     ticker_selecionado = request.GET.get('ticker')
#     graph = None

#     if ticker_selecionado:
#         ativo = yf.Ticker(ticker_selecionado)
#         historico = ativo.history(period="1y")  # Obtém o histórico de 1 ano
#         historico.reset_index(inplace=True)
#         fig = px.line(historico, x='Date', y='Close', title=f'Valorização de {ticker_selecionado} ao longo do tempo')
#         graph = fig.to_html(full_html=False)

#     return render(request, 'usuarios/dashboard.html', {'ativos': ativos, 'graph': graph, 'ticker_selecionado': ticker_selecionado})



@login_required
def dashboard(request):
    ativos = Ativo.objects.all()
    ticker_selecionado = request.GET.get('ticker')
    graph = None

    if ticker_selecionado:
        ativo = yf.Ticker(ticker_selecionado)
        historico = ativo.history(period="1y")  # Obtém o histórico de 1 ano
        historico.reset_index(inplace=True)

        # Dados do usuário
        ativos_usuario = Ativo.objects.filter(ticker=ticker_selecionado)
        data_compra = ativos_usuario[0].data_compra
        preco_medio = float(ativos_usuario[0].preco_medio)

        # Criar o gráfico
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=historico['Date'], y=historico['Close'], mode='lines', name='Valorização'))

        fig.add_trace(go.Scatter(x=[data_compra], y=[preco_medio], mode='markers', name='Valor da compra do ativo pelo Usuário', marker=dict(color='green', size=10)))

        fig.update_layout(title=f'Valorização de {ticker_selecionado} ao longo do tempo', xaxis_title='Data', yaxis_title='Preço de Fechamento')

        graph = fig.to_html(full_html=False)

    return render(request, 'usuarios/dashboard.html', {'ativos': ativos, 'graph': graph, 'ticker_selecionado': ticker_selecionado})