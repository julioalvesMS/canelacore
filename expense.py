#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import database
import data_types
import daily_report

__author__ = 'Julio'


class Expense(wx.Frame):

    textbox_description = None
    textbox_value = None

    def __init__(self, parent, title=u'Gastos', key=-1, data=None):
        wx.Frame.__init__(self, parent, -1, title, size=(500, 200),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.key = key
        self.data = data

        self.setup_gui()

        if self.key != -1 or self.data:
            self.setup()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        # first
        first = wx.Panel(self, -1, size=(480, 85), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        first.SetBackgroundColour(core.default_background_color)
        wx.StaticText(first, -1, u"Descrição:", pos=(10, 5))
        self.textbox_description = wx.TextCtrl(first, -1, pos=(10, 25), size=(300, 30))
        wx.StaticText(first, -1, u"Valor:", pos=(370, 5))
        wx.StaticText(first, -1, u"R$", pos=(355, 32))
        self.textbox_value = wx.TextCtrl(first, -1, pos=(370, 25), size=(80, 30))
        self.textbox_value.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_value.SetValue(u"0,00")
        # last
        last = wx.Panel(self, -1, size=(480, 60), pos=(10, 105), style=wx.SUNKEN_BORDER)
        last.SetBackgroundColour(core.default_background_color)
        last_ = wx.Panel(last, pos=(80, 10), size=(320, 40), style=wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                     u'Finalizar', pos=(0, 0), size=(100, 40))
        finish.Bind(wx.EVT_BUTTON, self.ask_end)
        restart = GenBitmapTextButton(last_, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Recomeçar', pos=(100, 0), size=(120, 40))
        restart.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u"sair", pos=(220, 0), size=(100, 40))
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)

    def setup(self):
        if not self.data:
            db = database.TransactionsDB()
            self.data = db.expenses_search_id(self.key)
            db.close()
            self.key = self.data.ID
        self.textbox_description.SetValue(self.data.description)
        self.textbox_value.SetValue(core.format_cash_user(self.data.value))

    def ask_clean(self, event):
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = str(self.textbox_description.GetValue())
        po = str(self.textbox_value.GetValue())
        if pl == u'' and po == u'0,00':
            self.Close()
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        dialogs.Ask(self, u"Registrar Gasto", 12)

    def clean(self):
        self.textbox_description.Clear()
        self.textbox_value.Clear()
        self.textbox_value.SetValue(u"0,00")

    def exit(self, event):
        self.Close()

    def end(self):
        description = self.textbox_description.GetValue().capitalize()
        val = core.money2float(self.textbox_value.GetValue())
        if len(description) == 0 or val == 0:
            return dialogs.launch_error(self, u'Dados insuficientes!', u'Error 404')

        date, finish_time = core.datetime_today()

        data = data_types.ExpenseData()
        data.ID = self.key
        data.description = description
        data.value = val
        data.record_date = date
        data.record_time = finish_time

        db = database.TransactionsDB()
        if self.key == -1:
            db.insert_expense(data)
        else:
            db.edit_expense(data)
        db.close()

        if self.key == -1:
            self.clean()
            dialogs.Confirmation(self, u"Sucesso", 2)
            return

        parent = self.GetParent()
        if isinstance(parent, daily_report.Report):
            parent.setup(None)
            self.exit(None)
