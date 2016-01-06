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
from satcomum import constantes


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

    def funcao_teste(self):
        codigo_ativacao = '12345678'
        cliente = ClienteSATLocal(BibliotecaSAT(self.getScriptPath() + '\SAT.dll'),
                                  codigo_ativacao)
        CNPJcanelaSanta = '16678899000136'
        cfe = CFeVenda(
            CNPJ='47012271000120',
            signAC=constantes.ASSINATURA_AC_TESTE,
            numeroCaixa=2,
            emitente=Emitente(
            CNPJ=CNPJcanelaSanta,
            IE='111222333444',
            IM='123456789012345',
            cRegTribISSQN='1',
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

        cliente.enviar_dados_venda(cfe)
