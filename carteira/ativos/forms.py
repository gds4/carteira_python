from django import forms

from .models import Ativo


class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['tipo', 'ticker', 'quantidade', 'data_compra', 'preco_medio']
        widgets = {
            'data_compra': forms.DateInput(attrs={'type': 'date'}),
            'ticker': forms.TextInput(attrs={'id': 'ticker-input', 'autocomplete': 'off'}),
        }
