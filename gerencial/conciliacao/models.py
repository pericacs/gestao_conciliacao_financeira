# flake8: noqa
from django.db import models


# Create your models here.
class webhook_arbi_francesinha(models.Model):
        id = models.AutoField(primary_key=True)	
        sacado = models.CharField(max_length=200)
        nossonumero = models.CharField(max_length=20)
        historico = models.CharField(max_length=200)
        data_referencia = models.DateTimeField()
        data_emissao = models.DateTimeField()
        data_vcto = models.DateTimeField()
        valor_titulo = models.DecimalField(max_digits=12, decimal_places=2)
        valor_desconto = models.DecimalField(max_digits=12, decimal_places=2)
        valor_abatimento = models.DecimalField(max_digits=12, decimal_places=2)
        valor_encargo = models.DecimalField(max_digits=12, decimal_places=2)
        valor_mora = models.DecimalField(max_digits=12, decimal_places=2)
        valor_multa = models.DecimalField(max_digits=12, decimal_places=2)
        valor_atu = models.DecimalField(max_digits=12, decimal_places=2)
        valor_iof = models.DecimalField(max_digits=12, decimal_places=2)
        valor_tarifa = models.DecimalField(max_digits=12, decimal_places=2)
        valor_lancamento_conta = models.DecimalField(max_digits=12, decimal_places=2)
        data_lancamento_contabil = models.DateTimeField()
        agencia_lancamento = models.CharField(max_length=20)
        conta_lancamento = models.CharField(max_length=30)
        nro_movimento = models.CharField(max_length=50)
        historico_lancado_cc = models.CharField(max_length=200)
        valor_lancado_cc = models.DecimalField(max_digits=12, decimal_places=2)
        data_bx_operacional = models.DateTimeField()
        valor_bx_operacional = models.DecimalField(max_digits=12, decimal_places=2)

        class Meta:
            managed = False
            db_table = 'webhook_arbi_francesinha'

