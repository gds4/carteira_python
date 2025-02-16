import yfinance as yf
import logging

def is_valid_ticker(ticker):
    try:
        dados = yf.download(ticker).empty
        return dados
    except:
        return False

def obter_preco_ativo(ticker):
    try:
        ativo = yf.Ticker(ticker)
        preco_atual = ativo.history(period="1d")['Close'].iloc[0]
        return preco_atual
    except Exception as e:
        return None  
