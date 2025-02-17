import requests
import yfinance as yf
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AtivoForm
from .models import Ativo


def obter_preco_ativo(ticker):
    try:
        ativo = yf.Ticker(ticker)
        preco_atual = ativo.history(period="1d")['Close'].iloc[0]
        return preco_atual
    except Exception as e:
        return None  

def listar_ativos(request):
    ativos = Ativo.objects.all()

    for ativo in ativos:
        preco_atual = obter_preco_ativo(ativo.ticker)
        ativo.preco_atual = preco_atual  
        ativo.save() 

    return render(request, 'ativos/listar_ativos.html', {'ativos': ativos})


def cadastrar_ativo(request):
    if request.method == 'POST':
        form = AtivoForm(request.POST)
        if form.is_valid():
            novo_ativo = form.save()  
            preco_atual = obter_preco_ativo(novo_ativo.ticker)
            novo_ativo.preco_atual = preco_atual  
            novo_ativo.save()
            return redirect('listar_ativos')
    else:
        form = AtivoForm()
    return render(request, 'ativos/cadastrar_ativo.html', {'form': form})

def atualizar_ativo(request, pk):
    ativo = get_object_or_404(Ativo, pk=pk)
    if request.method == 'POST':
        form = AtivoForm(request.POST, instance=ativo)
        if form.is_valid():
            form.save()
            preco_atual = obter_preco_ativo(ativo.ticker)
            ativo.preco_atual = preco_atual
            ativo.save()  
            return redirect('listar_ativos')
    else:
        form = AtivoForm(instance=ativo)
    return render(request, 'ativos/atualizar_ativo.html', {'form': form, 'ativo': ativo})

def excluir_ativo(request, pk):
    ativo = get_object_or_404(Ativo, pk=pk)
    if request.method == 'POST':
        ativo.delete()
        return redirect('listar_ativos')
    return render(request, 'ativos/excluir_ativo.html', {'ativo': ativo})

import requests


def autocomplete_tickers(request):
    query = request.GET.get('query', '')
    tickers = []

    if query:
        url = f'https://finnhub.io/api/v1/stock/symbol?exchange=US&token=cuklslhr01qo08i8k2rgcuklslhr01qo08i8k2s0'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if query.upper() in item['symbol'].upper():
                    tickers.append(item['symbol'])

    return JsonResponse({'tickers': tickers})


def calcular_dividendos(ticker, data_compra):
    try:
        ativo = yf.Ticker(ticker)
        dividendos = ativo.dividends
        print(f"Dividendos para {ticker} desde {data_compra}: {dividendos[dividendos.index >= str(data_compra)]}")
        dividendos_recebidos = dividendos[dividendos.index >= str(data_compra)].sum()
        return dividendos_recebidos
    except Exception as e:
        print(f"Erro ao calcular dividendos para {ticker}: {e}")
        return 0
