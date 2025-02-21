import numpy as np
import pandas as pd
import requests
from ativos.models import Ativo
from django.conf import settings
from django.db.models import Sum


class AIReportService:
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",  # Defina sua chave no settings
        "Content-Type": "application/json"
    }

    def __init__(self, user):
        self.ativos = Ativo.objects.filter(usuario=user)

    def calcular_desempenho(self):
        valor_investido = sum(a.valor_investido() for a in self.ativos)
        valor_atual = sum(a.valor_total() for a in self.ativos)
        retorno = ((valor_atual - valor_investido) / valor_investido) * 100 if valor_investido > 0 else 0
        dividendos = sum(a.dividendos_recebidos for a in self.ativos)
        return {
            'valor_investido': valor_investido,
            'valor_atual': valor_atual,
            'retorno': retorno,
            'dividendos': dividendos
        }

    def calcular_volatilidade(self):
        historico = []
        for ativo in self.ativos:
            try:
                import yfinance as yf
                dados = pd.DataFrame(yf.Ticker(ativo.ticker).history(period="1y")['Close'])
                retornos = dados['Close'].pct_change().dropna()
                historico.append(retornos)
            except Exception:
                continue
        if historico:
            todos_retornos = pd.concat(historico)
            volatilidade = todos_retornos.std() * np.sqrt(252)
            return volatilidade
        return 0

    def gerar_recomendacoes(self):
        alocacao = self.ativos.values('tipo').annotate(total=Sum('quantidade'))
        alocacoes = {a['tipo']: a['total'] for a in alocacao}
        return f"Distribuição atual: {alocacoes}. Considere balancear para uma alocação diversificada de acordo com seu perfil de risco."

    def analisar_dividendos(self):
        if not self.ativos.exists():
            return 0
        yields = [a.dividendos_recebidos / a.valor_investido() for a in self.ativos if a.valor_investido() > 0]
        return np.mean(yields) if yields else 0

    def generate_report(self):
        desempenho = self.calcular_desempenho()
        volatilidade = self.calcular_volatilidade()
        recomendacoes = self.gerar_recomendacoes()
        yield_medio = self.analisar_dividendos()

        prompt = f"""
        Analise detalhada da carteira:
        - Valor investido: R$ {desempenho['valor_investido']:.2f}
        - Valor atual: R$ {desempenho['valor_atual']:.2f}
        - Retorno acumulado: {desempenho['retorno']:.2f}%
        - Dividendos recebidos: R$ {desempenho['dividendos']:.2f}
        - Volatilidade estimada: {volatilidade:.2f}
        - Recomendações: {recomendacoes}
        - Yield médio: {yield_medio:.2%}
        Gere uma análise textual detalhada para o investidor, explicando esses pontos com base nos ativos reais da carteira.
        """

        payload = {
            "model": "mistralai/mistral-7b-instruct",  
            "messages": [
                {"role": "system", "content": "Você é um especialista em mercado financerio, dedicado a assistir e, sobretudo, educar os seus clientes sobre seus investimentos."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }

        response = requests.post(self.API_URL, json=payload, headers=self.HEADERS)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Erro na API OpenRouter: {response.text}"
