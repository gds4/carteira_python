from django import forms
from django.core.exceptions import ValidationError
from .models import Ativo
from .api.yfinance_service import is_valid_ticker

class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['tipo', 'ticker', 'quantidade', 'data_compra', 'preco_medio']
        widgets = {
            'data_compra': forms.DateInput(attrs={'type': 'date'}),
            'ticker': forms.TextInput(attrs={'id': 'ticker-input', 'autocomplete': 'off'}),
        }

    def clean_ticker(self):
        ticker = self.cleaned_data.get('ticker')
        if is_valid_ticker(ticker):
            raise ValidationError('Ticker inválido ou não encontrado.')
        return ticker