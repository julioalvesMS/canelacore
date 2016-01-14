# -*- coding: utf-8 -*-

import wx
import wx.xrc
from decimal import Decimal

import sat
from satcfe.entidades import Detalhamento, Imposto, ICMSSN102, COFINSSN, PISSN, ProdutoServico, DescAcrEntr, \
    MeioPagamento, InformacoesAdicionais, LocalEntrega, Destinatario
from satcomum import constantes


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

        # funcao_test()
        sat.consultar_sat()

    def __del__(self):
        pass


# Função que testa o sat.py
def funcao_test():
    # Preenche todas entidades da venda

    destinatario = Destinatario(
        CPF='11122233396',  # ou CNPJ, mas nunca os 2 ao mesmo tempo.
        xNome=u'João de Teste')

    entrega = LocalEntrega(
        xLgr='Rua Armando Gulim',
        nro='65',
        xBairro=u'Parque Glória III',
        xMun='Catanduva',
        UF='SP')

    detalhamentos = [
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
    ]

    descontos_acrescimos_subtotal = DescAcrEntr(
        vAcresSubtot=Decimal('0.02'),
        vCFeLei12741=Decimal('0.03'))

    pagamentos = [
        MeioPagamento(
            cMP=constantes.WA03_DINHEIRO,
            vMP=Decimal('10.00')),
    ]

    informacoes_adicionais = InformacoesAdicionais(infCpl='Teste')

    resp = sat.enviar_dados_venda(detalhamentos=detalhamentos, pagamentos=pagamentos, destinatario=destinatario,
                                  entrega=entrega, descontos_acrescimos_subtotal=descontos_acrescimos_subtotal,
                                  informacoes_adicionais=informacoes_adicionais)

    print(resp.mensagem)


    # Salva o xml, gerado pelo SAT depois da compra, no HD
    open("saida.xml", "w").write(resp.xml())
