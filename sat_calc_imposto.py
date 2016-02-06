#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ibptws import conf
from decimal import Decimal
from ibptws.calculadoras import DeOlhoNoImposto

conf.token = '797XZCfo2HY0TtThIPLPiMds9JzUrCDvUVhiPaJ_Jq7OFawH1OdSq3kJkOSsxPpI'
conf.cnpj = '16678899000136'
conf.estado = 'SP'

# DEBUG - incompleto. Modificar para que essa função receba um objeto e pegue o ncm e o valor
#                     a partir do objeto. O Júlio tem que fazer esse objeto.
def calcular_total_tributos(ncm, ncm_ex, valor):
    calc = DeOlhoNoImposto()
    calc.produto('02091021', 0, Decimal('5.75'))
    calc.servico('0101', Decimal('73.47'))

    print(calc.carga_federal_nacional())