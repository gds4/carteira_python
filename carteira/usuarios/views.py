import json
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from ativos.models import Ativo
from ativos.views import calcular_dividendos
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from services.ai_report_service import AIReportService

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
            messages.success(request, "Login realizado com sucesso!")
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, "usuarios/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")





@login_required
def dashboard(request):
    ativos = Ativo.objects.filter(usuario=request.user)  # Filtrar ativos pelo usuário autenticado
    ticker_selecionado = request.GET.get('ticker')
    graph_valorizacao = None
    graph_dividendos = None

    # Atualizar dividendos recebidos para cada ativo
    for ativo in ativos:
        dividendos_recebidos = calcular_dividendos(ativo.ticker, ativo.data_compra) * ativo.quantidade
        print(f"Atualizando dividendos recebidos para {ativo.ticker}: {dividendos_recebidos}")
        ativo.dividendos_recebidos = dividendos_recebidos
        ativo.save()

    if ticker_selecionado:
        ativo = yf.Ticker(ticker_selecionado)
        ativos_usuario = Ativo.objects.filter(ticker=ticker_selecionado, usuario=request.user)
        data_compra = ativos_usuario[0].data_compra
        start_date = (data_compra - pd.DateOffset(months=6)).strftime('%Y-%m-%d')  # 6 meses antes da data de compra
        historico = ativo.history(start=start_date)  # Obtém o histórico a partir de 6 meses antes da data de compra
        historico.reset_index(inplace=True)

        # Dados do usuário
        ativos_usuario = Ativo.objects.filter(ticker=ticker_selecionado, usuario=request.user)
        data_compra = ativos_usuario[0].data_compra
        preco_medio = float(ativos_usuario[0].preco_medio)
        quantidade_total = sum(ativo.quantidade for ativo in ativos_usuario)

        # Criar o gráfico de valorização
        fig_valorizacao = go.Figure()
        fig_valorizacao.add_trace(go.Scatter(x=historico['Date'], y=historico['Close'], mode='lines', name='Valorização'))
        fig_valorizacao.add_trace(go.Scatter(x=[data_compra], y=[preco_medio], mode='markers', name='Preço Médio do Usuário', marker=dict(color='green', size=10)))
        fig_valorizacao.update_layout(title=f'Valorização de {ticker_selecionado} ao longo do tempo', xaxis_title='Data', yaxis_title='Preço de Fechamento')
        graph_valorizacao = fig_valorizacao.to_html(full_html=False)

        # Calcular dividendos recebidos
        dividendos = ativo.dividends
        dividendos = dividendos[dividendos.index >= str(data_compra)]
        print(f"Dividendos filtrados para {ticker_selecionado} desde {data_compra}: {dividendos}")
        if not dividendos.empty:
            dividendos = dividendos.to_frame(name='Dividends')
            dividendos['Total'] = dividendos['Dividends'] * quantidade_total
            dividendos.reset_index(inplace=True)

            # Criar o gráfico de dividendos
            fig_dividendos = go.Figure()
            fig_dividendos.add_trace(go.Scatter(
                x=dividendos['Date'], 
                y=dividendos['Total'], 
                mode='lines+markers', 
                name='Dividendos Recebidos', 
                line=dict(color='blue'),
                hovertemplate='Data: %{x}<br>R$ %{y:.4f}<extra></extra>'  # Formatação com data e duas casas decimais
            ))
            fig_dividendos.update_layout(title=f'Dividendos Recebidos de {ticker_selecionado} desde {data_compra}', xaxis_title='Data', yaxis_title='Dividendos (R$)')
            graph_dividendos = fig_dividendos.to_html(full_html=False)
        else:
            graph_dividendos = "<p>Nenhum dividendo recebido desde a data de compra.</p>"

    return render(request, 'usuarios/dashboard.html', {'ativos': ativos, 'graph_valorizacao': graph_valorizacao, 'graph_dividendos': graph_dividendos, 'ticker_selecionado': ticker_selecionado})


@login_required
def resumo_carteira(request):
    report_service = AIReportService(request.user)  
    relatorio = report_service.generate_report()  

    return render(request, 'usuarios/resumo_carteira.html', {
        'relatorio': relatorio
    })
