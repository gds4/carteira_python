from django import forms
from django.core.exceptions import ValidationError
from .models import Ativo
from .api.yfinance_service import is_valid_ticker

class AtivoForm(forms.ModelForm):
    # Adicione esses campos personalizados
    quantidade = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'step': '1'
        })
    )
    
    preco_medio = forms.DecimalField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0.01',
            'step': '0.01'
        })
    )

    class Meta:
        model = Ativo
        fields = ['tipo', 'ticker', 'quantidade', 'data_compra', 'preco_medio']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'ticker': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'ticker-input',
                'autocomplete': 'off'
            }),
            'data_compra': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classe is-invalid para campos com erro
        for field in self.fields:
            if self.errors.get(field):
                self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})

    def clean_ticker(self):
        ticker = self.cleaned_data.get('ticker')
        if is_valid_ticker(ticker):
            raise ValidationError('Ticker inválido ou não encontrado.')
        return ticker