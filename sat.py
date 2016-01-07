# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import os
import sys
from decimal import Decimal

import wx
import wx.xrc

import satcomum
from satcfe import BibliotecaSAT
from satcfe import ClienteSATLocal
from satcfe.entidades import CFeVenda, Emitente, Detalhamento, ProdutoServico, Imposto, PISSN, ICMSSN102, COFINSSN, \
    Destinatario, LocalEntrega, MeioPagamento, CFeCancelamento
from satcfe.rede import ConfiguracaoRede
from satcomum import br
from satcomum import constantes

# CONSTANTES
codigo_ativacao = '12345678'
cnpj_desenvolvedor_ac = '76861313000104'
cnpj_canela_santa = '16678899000136'
cnpj_teste_emulador = '11111111111111'
numeroCaixaPadrao= 1

###########################################################################
## Class MyFrame2
###########################################################################

class Teste(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        gbSizer3 = wx.GridBagSizer(0, 0)
        gbSizer3.SetFlexibleDirection(wx.BOTH)
        gbSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"MyButton", wx.Point(-1, -1), wx.DefaultSize, 0)
        gbSizer3.Add(self.m_button1, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL | wx.EXPAND, 5)

        self.m_button2 = wx.Button(self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer3.Add(self.m_button2, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_bpButton1 = wx.BitmapButton(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize,
                                           wx.BU_AUTODRAW)
        gbSizer3.Add(self.m_bpButton1, wx.GBPosition(0, 23), wx.GBSpan(1, 1), wx.ALL, 5)

        self.SetSizer(gbSizer3)
        self.Layout()

        self.Centre(wx.BOTH)

        self.Show()

        funcao_teste()

    def __del__(self):
        pass

def funcao_teste():

    resp = enviar_dados_venda()
    print(resp.mensagem)

    # Salva o xml, gerado pelo SAT depois da compra, no HD
    open("saida.xml", "w").write(resp.xml())


#####################################################
#                MÉTODOS AUXILIARES                 #
#####################################################


# Retorna o caminho da pasta onde está o script .py
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


# Cria um cupom fiscal de venda
def criar_cupom_fiscal_venda():

    cfe = CFeVenda(
        CNPJ=cnpj_desenvolvedor_ac,
        signAC=constantes.ASSINATURA_AC_TESTE,
        numeroCaixa= numeroCaixaPadrao,
        emitente=Emitente(
            CNPJ=cnpj_teste_emulador,
            IE='111111111111',
            indRatISSQN='S'),
        destinatario=Destinatario(
            CPF='11122233396',
            xNome=u'João de Teste'),
        entrega=LocalEntrega(
            xLgr='Rua Armando Gulim',
            nro='65',
            xBairro=u'Parque Glória III',
            xMun='Catanduva',
            UF='SP'),
        detalhamentos=[
            Detalhamento(
                produto=ProdutoServico(
                    cProd='123456',
                    xProd='BORRACHA STAEDTLER pvc-free',
                    CFOP='5102',
                    uCom='UN',
                    qCom=Decimal('1.0000'),
                    vUnCom=Decimal('5.75'),
                    indRegra='A'),
                imposto=Imposto(
                    icms=ICMSSN102(Orig='2', CSOSN='500'),
                    pis=PISSN(CST='49'),
                    cofins=COFINSSN(CST='49'))),
        ],
        pagamentos=[
            MeioPagamento(
                cMP=constantes.WA03_DINHEIRO,
                vMP=Decimal('10.00')),
        ])

    return cfe

# Cria um cupom fiscal de cancelamento de venda
def criar_cupom_fiscal_cancelamento(destinatario, chaveConsulta, numeroCaixa):
    cfeCancelamento = CFeCancelamento( destinatario = destinatario, chCanc = chaveConsulta,
                                       CNPJ = cnpj_teste_emulador, signAC = constantes.ASSINATURA_AC_TESTE,
                                       numeroCaixa = numeroCaixa)
    return cfeCancelamento


#####################################################
#          MÉTODOS DE COMUNICAÇÃO COM O SAT         #
#####################################################


# Realiza a interface com a dll, retornando uma instância de ClienteSATLocal
def cliente_sat_local():
    cliente = ClienteSATLocal(BibliotecaSAT(get_script_path() + '\SAT.dll'),
                              codigo_ativacao)
    return cliente


# Ativa o equipamento SAT com o certificado ACSAT SEFAZ. Só é necessário chamar essa função 1 vez para configuração
def ativar_sat_acsat():
    """ o CNPJ '11111111111111' (CNPJtesteEmulador) só é usado com o emulador.
        No SAT real o CNPJ deve ser CNPJCanelaSanta """
    resp = cliente.ativar_sat(satcomum.constantes.CERTIFICADO_ACSAT_SEFAZ,
                              cnpj_teste_emulador,
                              br.codigo_ibge_uf('SP'))
    return resp


# Ativa o equipamento SAT com certificado ICP BRASIL. Só é necessário chamar essa função 1 vez para configuração
# os certificado podem ser: CERTIFICADO_ICPBRASIL ou CERTIFICADO_ICPBRASIL ou CERTIFICADO_ICPBRASIL_RENOVACAO
# DEBUG - função incompleta
def ativar_sat_icpbrasil(certificado=satcomum.constantes.CERTIFICADO_ICPBRASIL):
    """ o CNPJ '11111111111111' (CNPJtesteEmulador) só é usado com o emulador.
        No SAT real o CNPJ deve ser CNPJCanelaSanta """
    resp1 = cliente.ativar_sat(certificado,
                              cnpj_teste_emulador,
                              br.codigo_ibge_uf('SP'))

    # resp1.csr() - bugado. Por que ?
    print(resp1.CSR)

    file = open('certificado.pem', 'r')
    conteudo_certificado = file.read()
    resp2 = cliente.comunicar_certificado_icpbrasil(conteudo_certificado)
    return resp1, resp2


# Associa uma assinatura ao SAT. Só é necessário chamar essa função 1 vez para configuração
def associar_assinatura():
    """ Essa constantes.ASSINATURA_AC_TESTE eu modifiquei por uma string de 344 caracteres
        O CNPJtesteEmulador deve ser trocado pelo CNPJcanelaSanta quando parar de usar o emulador """
    resp = cliente.associar_assinatura((cnpj_desenvolvedor_ac + cnpj_teste_emulador),
                                       constantes.ASSINATURA_AC_TESTE)
    return resp


# Configura a conexão do SAT com a internet. DEBUG - não foi testado. Acho que o emulador ñ suporta.
def configurar_interface_de_rede():
    """ CONFIGURAR INTERFACE DE REDE
        permite a conexão do SAT com a internet """
    rede = ConfiguracaoRede(
        tipoInter=constantes.REDE_TIPOINTER_ETHE,
        tipoLan=constantes.REDE_TIPOLAN_DHCP)
    resp = cliente.configurar_interface_de_rede(rede)
    return resp


# Emite uma venda ao SAT
def enviar_dados_venda():
    cfe = criar_cupom_fiscal_venda()
    resp = cliente.enviar_dados_venda(cfe)
    return resp


# Cancela a última venda - DEBUG - emulador bugado. Só funciona com o emulador versão 2.7.10
# outro bug: o retorno do timeStamp (a data/hora) é bugada. Eu acho que é por causa do emulador que retorna data errada.
# Isso da erro na hora de converter formatar o dateTime dentro da função as_datetime() em satcfe\util.py
def cancelar_ultima_venda(chaveConsulta, destinatario = None):
    cfeCancelamento = criar_cupom_fiscal_cancelamento(destinatario, chaveConsulta, numeroCaixaPadrao)
    resp = cliente.cancelar_ultima_venda(chaveConsulta, cfeCancelamento)
    return resp


# Teste fim a fim. Envia dados para uma venda de teste.
def teste_fim_a_fim():
    cfe = criar_cupom_fiscal_venda()
    resp = cliente.teste_fim_a_fim(cfe)
    return resp


# Troca o código de ativação - DEBUG - o emulador está bugado e reclama de par de chaves corrompido.
#                                      Nem o ativador que o governo disponibilizou mudas as chaves -_-
def trocar_codigo_de_ativacao(novo_codigo):
    resp = cliente.trocar_codigo_de_ativacao(novo_codigo)
    return resp


# Bloqueia o equipamento SAT
def bloquear_sat():
    resp = cliente.bloquear_sat()
    return resp


# Desbloqueia o equipamento SAT
def desbloquear_sat():
    resp = cliente.desbloquear_sat()
    return resp


# Atualiza o software do equipamento SAT
def atualizar_software_sat():
    resp = cliente.atualizar_software_sat()
    return resp


# Consulta o SAT. Apenas para testes.
def consultar_sat():
    resp = cliente.consultar_sat()
    return resp


# Consulta o status operacional do SAT. Apenas para testes.
# Uma exception por ter 1 parâmetro a menos é esperada.
def consultar_status_operacional():
    resp = cliente.consultar_status_operacional()
    return resp


# Consulta um numero de sessão processado pelo SAT
def consultar_numero_sessao(numeroSessao):
    resp = cliente.consultar_numero_sessao(numeroSessao)
    return resp


# Extrai logs do SAT
def extrair_logs():
    resp = cliente.extrair_logs()
    return resp


#####################################################
#                VARIÁVEIS  BÁSICAS                 #
#####################################################


# Cria um ClienteSATLocal
cliente = cliente_sat_local()