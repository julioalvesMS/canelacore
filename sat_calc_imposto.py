from ibptws import conf
from decimal import Decimal
from ibptws.calculadoras import DeOlhoNoImposto

import sat

conf.token = 'ZyW9z...' # cadastre-se no IBPT para obter seu token
conf.cnpj = sat.CNPJ_CANELA_SANTA
conf.estado = 'SP'

def calcular_total_imposto():
    calc = DeOlhoNoImposto()
    # DEBUG - INCOMPLETO. FALTA COMPLETAR