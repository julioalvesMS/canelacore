# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from satcfe import BibliotecaSAT
from satcfe import ClienteSATLocal
import os
import sys
import ctypes

###########################################################################
## Class MyFrame2
###########################################################################

class Teste ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        gbSizer3 = wx.GridBagSizer( 0, 0 )
        gbSizer3.SetFlexibleDirection( wx.BOTH )
        gbSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_button1, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_button2 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer3.Add( self.m_button2, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_bpButton1 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
        gbSizer3.Add( self.m_bpButton1, wx.GBPosition( 0, 23 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


        self.SetSizer( gbSizer3 )
        self.Layout()

        self.Centre( wx.BOTH )

        self.Show()

        self.funcao_teste()

    def __del__( self ):
        pass


    def getScriptPath(self):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    def funcao_teste(self):

        print("BEFORE\n")

        cliente = ClienteSATLocal(BibliotecaSAT(self.getScriptPath() + '\SAT.dll'),
                                  codigo_ativacao='12345678')

        resposta = cliente.consultar_sat()

        print('OI BR')
        #print(resposta.mensagem)

        #resposta = cliente.consultar_sat()


        #print(resposta.mensagem)
