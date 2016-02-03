# -*- coding: utf-8 -*-

import wx
import wx.xrc
from decimal import Decimal
import sat
from data_types import SaleData
from satcfe.entidades import Detalhamento, Imposto, ICMSSN102, COFINSSN, PISSN, ProdutoServico, DescAcrEntr, \
    MeioPagamento, InformacoesAdicionais, LocalEntrega, Destinatario
from satcomum import constantes
import sat_calc_imposto

REGRA_CALCULO = 'A'


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
        # sat.consultar_sat()
        sale_data = SaleData()
        sat_calc_imposto.calcular_total_imposto()


    def __del__(self):
        pass