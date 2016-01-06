# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################
from ctypes import c_float
import wx
import wx.xrc
from decimal import Decimal
from satcfe import BibliotecaSAT
from satcfe import ClienteSATLocal
import os
import sys
from satcfe.entidades import CFeVenda, Emitente, Detalhamento, ProdutoServico, Imposto, PISSN, ICMSSN102, COFINSSN, \
    Destinatario, LocalEntrega, MeioPagamento
import satcomum
from satcomum import constantes
from satcomum import br


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

        self.funcao_teste()

    def __del__(self):
        pass

    def getScriptPath(self):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    """ passo a passo - SAT """
    """ Ativar SAT
        AssociarAssinatura (signAC)
    """

    def funcao_teste(self):
        codigo_ativacao = '12345678'
        eCNPJdesenvolvedorAC = '76861313000104'
        CNPJcanelaSanta = '16678899000136'
        CNPJtesteEmulador = '11111111111111'

        # Interface com a DLL
        cliente = ClienteSATLocal(BibliotecaSAT(self.getScriptPath() + '\SAT.dll'),
                                  codigo_ativacao)

        # Ativar SAT
        # o CNPJ '11111111111111' (CNPJtesteEmulador) só é usado com o emulador. No SAT real o CNPJ deve ser CNPJCanelaSanta
        # resp = cliente.ativar_sat(satcomum.constantes.CERTIFICADO_ACSAT_SEFAZ,
        #                         CNPJtesteEmulador,
        #                         br.codigo_ibge_uf('SP'))
        # print(resp.mensagem)

        # Associando assinatura
        # Essa constantes.ASSINATURA_AC_TESTE eu modifiquei por uma string de 344 caracteres
        # O CNPJtesteEmulador deve ser trocado pelo CNPJcanelaSanta quando parar de usar o emulador
        # resp = cliente.associar_assinatura((eCNPJdesenvolvedorAC + CNPJtesteEmulador), constantes.ASSINATURA_AC_TESTE)
        # print(resp.mensagem)


        # Realiza uma venda
        cfe = CFeVenda(
             CNPJ=eCNPJdesenvolvedorAC,
             signAC=constantes.ASSINATURA_AC_TESTE,
             numeroCaixa=2,
             emitente=Emitente(
                 CNPJ=CNPJtesteEmulador,
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

        resp = cliente.enviar_dados_venda(cfe)
