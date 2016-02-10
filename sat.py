#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import satcomum
from database import InventoryDB
from satcfe import BibliotecaSAT
from satcfe import ClienteSATLocal
from satcfe.entidades import CFeVenda, Emitente, CFeCancelamento
from satcfe.rede import ConfiguracaoRede
from satcomum import br
from decimal import Decimal
from satcfe.entidades import Detalhamento, Imposto, ICMSSN102, COFINSSN, PISSN, ProdutoServico, DescAcrEntr, \
    MeioPagamento, Destinatario
from satcomum import constantes

#####################################################
#                    CONSTANTES                     #
#####################################################


ASSINATURA_AC = '1111111111111222222222222221111111111111122222222222222111111111111112222222' \
                '2222222111111111111112222222222222211111111111111222222222222221111111111111' \
                '1222222222222221111111111111122222222222222111111111111112222222222222211111' \
                '1111111112222222222222211111111111111222222222222221111111111111122222222222' \
                '2221111111111111122222222222222111111111'
CODIGO_ATIVACAO = '12345678'
CNPJ_DESENVOLVEDOR_AC = '76861313000104'
CNPJ_CANELA_SANTA = '11111111111111'  # tem que permanecer "11111..." ou o emulador não funciona
NUMERO_CAIXA_PADRAO = 1


#####################################################
#                MÉTODOS AUXILIARES                 #
#####################################################


# Retorna o caminho da pasta onde está o script .py
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


# Cria um cupom fiscal de venda
def criar_cupom_fiscal_venda(detalhamentos, pagamentos, destinatario=None, entrega=None,
                             descontos_acrescimos_subtotal=None, informacoes_adicionais=None):
    # Emitente
    emitente = Emitente(
        CNPJ=CNPJ_CANELA_SANTA,
        IE='111111111111',
        indRatISSQN='S')
    """ DEBUG - não é necessário o indRatISSQN, mas o emulador buga sem isso aqui.
                Tirar quanto tiver o SAT real. """

    # Preenche cupom fiscal de venda, composto pelas entidades
    cfe = CFeVenda(
        # campos simples
        CNPJ=CNPJ_DESENVOLVEDOR_AC,
        signAC=ASSINATURA_AC,
        numeroCaixa=NUMERO_CAIXA_PADRAO,

        # entidades
        emitente=emitente,
        destinatario=destinatario,
        entrega=entrega,
        detalhamentos=detalhamentos,
        descontos_acrescimos_subtotal=descontos_acrescimos_subtotal,
        pagamentos=pagamentos,
        informacoes_adicionais=informacoes_adicionais,
    )

    return cfe


# Cria um cupom fiscal de cancelamento de venda
def criar_cupom_fiscal_cancelamento(chave_consulta, numero_caixa, destinatario=None, ):
    cfe_cancelamento = CFeCancelamento(destinatario=destinatario, chCanc=chave_consulta,
                                       CNPJ=CNPJ_CANELA_SANTA, signAC=ASSINATURA_AC,
                                       numeroCaixa=numero_caixa)
    return cfe_cancelamento


# Envia uma venda ao sat. É essa função que deve ser chamada toda vez que uma venda for realizada pra
# enviar as informações pro SAT.
def enviar_venda_ao_sat(sale):
    """

    :param sale:
    :type sale: data_types.SaleData
    :return:
    """

    # DESTINATÁRIO
    destinatario = Destinatario(
        CPF=sale.client_cpf) if sale.client_cpf else None

    # PAGAMENTOS
    modo_pagamento = None
    if sale.payment == u"Dinheiro":
        modo_pagamento = constantes.WA03_DINHEIRO
    elif sale.payment == u"Cartão de Crédito":
        modo_pagamento = constantes.WA03_CARTAO_CREDITO
    elif sale.payment == u"Cartão de Débito":
        modo_pagamento = constantes.WA03_CARTAO_DEBITO
    elif sale.payment == u"Cheque":
        modo_pagamento = constantes.WA03_CHEQUE
    elif sale.payment == u"Outra":
        modo_pagamento = constantes.WA03_OUTROS
    pagamentos = [
        MeioPagamento(
            cMP=modo_pagamento,
            vMP=Decimal("%.2f" % sale.value))
    ]

    # DETALHAMENTOS
    detalhamentos = []
    vCFeLei12741 = Decimal("0.00")
    for i in range(len(sale.products_IDs)):
        product_id = sale.products_IDs[i]
        inventory_db = InventoryDB()
        product = inventory_db.inventory_search_id(product_id)
        categoria = inventory_db.categories_search_id(product.category_ID)
        vItem12741 = Decimal("%.2f" % ((categoria.imposto_total / 100) * product.price * sale.amounts[i]))

        print(product.amount)

        detalhamento = Detalhamento(
            produto=ProdutoServico(
                cProd=str(product.ID),
                xProd=product.description,
                CFOP=str(categoria.cfop),
                uCom=categoria.unit,
                qCom=Decimal("%.4f" % sale.amounts[i]),
                vUnCom=Decimal("%.2f" % product.price),
                indRegra='A'
            ),
            imposto=Imposto(
                icms=ICMSSN102(Orig='0', CSOSN='102'),
                pis=PISSN(CST='49'),
                cofins=COFINSSN(CST='49'),
                vItem12741=vItem12741
            )
        )
        vCFeLei12741 += vItem12741
        detalhamentos.append(detalhamento)

    # DESCONTOS_ACRESCIMOS_SUBTOTAL
    # DEBUG - mano, e o vCFeLei12741, onde vai ? Por que ta aqui ? E quando é None ????
    if sale.discount - sale.taxes > 0:
        descontos_acrescimos_subtotal = DescAcrEntr(
            vDescSubtot=Decimal(str(sale.discount - sale.taxes)),
            vCFeLei12741=vCFeLei12741)
    elif sale.discount - sale.taxes < 0:
        descontos_acrescimos_subtotal = DescAcrEntr(
            vAcresSubtot=Decimal(str(sale.taxes - sale.discount)),
            vCFeLei12741=vCFeLei12741)
    else:
        descontos_acrescimos_subtotal = None

    resp = enviar_dados_venda(detalhamentos=detalhamentos, pagamentos=pagamentos, destinatario=destinatario,
                              entrega=None, descontos_acrescimos_subtotal=descontos_acrescimos_subtotal)

    print(resp.mensagem)

    # Salva o xml, gerado pelo SAT depois da compra, no HD
    open("saida.xml", "w").write(resp.xml())


#####################################################
#          MÉTODOS DE COMUNICAÇÃO COM O SAT         #
#####################################################


# Cria componente de comunicação com a dll, que, por sua vez, se comunica com o SAT.
def cliente_sat_local():
    cliente_sat = ClienteSATLocal(BibliotecaSAT(get_script_path() + '\SAT.dll'),
                                  CODIGO_ATIVACAO)
    return cliente_sat


# Ativa o equipamento SAT com o certificado ACSAT SEFAZ.
#       Só é necessário chamar essa função 1 vez para configuração
def ativar_sat_acsat():
    resp = cliente.ativar_sat(satcomum.constantes.CERTIFICADO_ACSAT_SEFAZ,
                              CNPJ_CANELA_SANTA,
                              br.codigo_ibge_uf('SP'))
    return resp


# Ativa o equipamento SAT com certificado ICP BRASIL.
#       Só é necessário chamar essa função 1 vez para configuração
#       os certificado podem ser: CERTIFICADO_ICPBRASIL ou CERTIFICADO_ICPBRASIL ou CERTIFICADO_ICPBRASIL_RENOVACAO
#       DEBUG - função incompleta. Acho que precisa do SAT real pra testar ??
def ativar_sat_icpbrasil(certificado=satcomum.constantes.CERTIFICADO_ICPBRASIL):
    resp1 = cliente.ativar_sat(certificado,
                               CNPJ_CANELA_SANTA,
                               br.codigo_ibge_uf('SP'))

    # resp1.csr() - bugado. Por que ?
    print(resp1.csr())

    f = open('certificado.pem', 'r')
    conteudo_certificado = f.read()
    resp2 = cliente.comunicar_certificado_icpbrasil(conteudo_certificado)
    return resp1, resp2


# Associa uma assinatura ao SAT.
#       Só é necessário chamar essa função 1 vez para configuração
def associar_assinatura():
    resp = cliente.associar_assinatura((CNPJ_DESENVOLVEDOR_AC + CNPJ_CANELA_SANTA),
                                       ASSINATURA_AC)
    return resp


# Configura a conexão do SAT com a internet.
#       DEBUG - não foi testado. Acho que o emulador ñ suporta.
def configurar_interface_de_rede():
    rede = ConfiguracaoRede(
        tipoInter=constantes.REDE_TIPOINTER_ETHE,
        tipoLan=constantes.REDE_TIPOLAN_DHCP)
    resp = cliente.configurar_interface_de_rede(rede)
    return resp


# Emite uma venda ao SAT.
def enviar_dados_venda(detalhamentos, pagamentos, destinatario=None, entrega=None,
                       descontos_acrescimos_subtotal=None, informacoes_adicionais=None):
    cfe = criar_cupom_fiscal_venda(detalhamentos=detalhamentos, pagamentos=pagamentos, destinatario=destinatario,
                                   entrega=entrega, descontos_acrescimos_subtotal=descontos_acrescimos_subtotal,
                                   informacoes_adicionais=informacoes_adicionais)
    resp = cliente.enviar_dados_venda(cfe)
    return resp


# Cancela a última venda.
#       DEBUG - bug1: emulador bugado. Só funciona com o emulador versão 2.7.10
#       bug2: o retorno do timeStamp (a data/hora) é bugada. Eu acho que o emulador retorna a data errada.
#       Isso da erro na hora de converter formatar o dateTime dentro da função as_datetime() em satcfe\util.py
def cancelar_ultima_venda(chave_consulta, destinatario=None):
    cfe_cancelamento = criar_cupom_fiscal_cancelamento(chave_consulta=chave_consulta, numero_caixa=NUMERO_CAIXA_PADRAO,
                                                       destinatario=destinatario)
    resp = cliente.cancelar_ultima_venda(chave_consulta, cfe_cancelamento)
    return resp


# Teste fim a fim. Envia dados para uma venda de teste.
def teste_fim_a_fim(detalhamentos, pagamentos, destinatario=None, entrega=None,
                    descontos_acrescimos_subtotal=None, informacoes_adicionais=None):
    cfe = criar_cupom_fiscal_venda(detalhamentos=detalhamentos, pagamentos=pagamentos, destinatario=destinatario,
                                   entrega=entrega, descontos_acrescimos_subtotal=descontos_acrescimos_subtotal,
                                   informacoes_adicionais=informacoes_adicionais)
    resp = cliente.teste_fim_a_fim(cfe)
    return resp


#  Troca o código de ativação.
#       DEBUG - o emulador está bugado e reclama de par de chaves corrompido.
#       Nem o ativador que o governo disponibilizou muda as chaves -_-
def trocar_codigo_de_ativacao(novo_codigo):
    resp = cliente.trocar_codigo_de_ativacao(novo_codigo)
    return resp


# Bloqueia o equipamento SAT.
def bloquear_sat():
    resp = cliente.bloquear_sat()
    return resp


# Desbloqueia o equipamento SAT.
def desbloquear_sat():
    resp = cliente.desbloquear_sat()
    return resp


# Atualiza o software do equipamento SAT.
def atualizar_software_sat():
    resp = cliente.atualizar_software_sat()
    return resp


# Consulta o SAT.
#       Apenas para testes.
def consultar_sat():
    resp = cliente.consultar_sat()
    return resp


# Consulta o status operacional do SAT.
#       Apenas para testes. Uma exception por ter 1 parâmetro a menos é esperada.
def consultar_status_operacional():
    resp = cliente.consultar_status_operacional()
    return resp


# Consulta um numero de sessão processado pelo SAT.
def consultar_numero_sessao(numero_sessao):
    resp = cliente.consultar_numero_sessao(numero_sessao)
    return resp


# Extrai logs do SAT.
def extrair_logs():
    resp = cliente.extrair_logs()
    return resp


#####################################################
#                VARIÁVEIS  BÁSICAS                 #
#####################################################


# Cria um ClienteSATLocal
cliente = cliente_sat_local()
