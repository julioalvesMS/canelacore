# -*- coding: utf-8 -*-

from ibptws import conf
from decimal import Decimal
from ibptws.calculadoras import DeOlhoNoImposto

conf.token = '797XZCfo2HY0TtThIPLPiMds9JzUrCDvUVhiPaJ_Jq7OFawH1OdSq3kJkOSsxPpI'
conf.cnpj = '16678899000136'
conf.estado = 'SP'

# Calcula o valor total de impostos sobre um produto
def calcular_total_tributos(ncm, preco):

    calc = DeOlhoNoImposto()
    calc.produto(ncm, 0, preco)

    return Decimal("%.2f" % calc.total_tributos())