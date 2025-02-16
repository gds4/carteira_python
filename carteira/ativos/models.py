from django.db import models


class Ativo(models.Model):
    TIPO_ATIVO_CHOICES = [
        ('acao', 'Ação'),
        ('fii', 'FII'),
        ('etf', 'ETF'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_ATIVO_CHOICES)
    ticker = models.CharField(max_length=10)
    quantidade = models.PositiveIntegerField()
    data_compra = models.DateField()
    preco_medio = models.DecimalField(max_digits=10, decimal_places=2)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def valor_investido(self):
        """Calcula o valor total investido no ativo"""
        return self.quantidade * self.preco_medio
    
    def valor_total(self):
        """Calcula o valor total do ativo com base na quantidade e no preço atual"""
        if self.preco_atual:
            return self.quantidade * self.preco_atual
        return 0

    def __str__(self):
        return f"{self.ticker} - {self.tipo}"

