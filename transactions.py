#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import database
import data_types
import daily_report

__author__ = 'Julio'


class Transaction(wx.Frame):
    textbox_description = None
    textbox_value = None

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(500, 200),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

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
        pass

    def clean(self):
        self.textbox_description.Clear()
        self.textbox_value.Clear()
        self.textbox_value.SetValue(u"0,00")

    def exit(self, event):
        self.Close()


class Expense(Transaction):
    def __init__(self, parent, title=u'Gastos', key=-1):
        Transaction.__init__(self, parent, title)

        self.key = key

        if self.key != -1:
            self.setup()

    def setup(self):
        if self.key == -1:
            return
        db = database.TransactionsDB()
        data = db.expenses_search_id(self.key)
        self.textbox_description.SetValue(data.description)
        self.textbox_value.SetValue(core.good_show("money", data.value))

        db.close()

    def ask_end(self, event):
        dialogs.Ask(self, u"Registrar Gasto", 12)

    def end(self):
        description = self.textbox_description.GetValue().capitalize()
        val = float(self.textbox_value.GetValue().replace(",", "."))
        if len(description) == 0 or val == 0:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(datetime.now().day))

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

# class Income(Transaction):
#     def __init__(self, parent, month, title=u'Ganhos', argv=None):
#         Transaction.__init__(self, parent, title)
#
#         self.argv = argv
#         self.month = month
#
#     def setup(self):
#         if not self.argv:
#             return
#         data = shelve.open(self.argv[0])
#         self.textbox_description.SetValue(data["winning"][data[1]]['description'])
#         self.textbox_value.SetValue(
#             core.good_show("money", str(data["winning"][data[1]]['value'])).replace(".", ","))
#         data.close()
#
#     def ask_end(self, event):
#         dialogs.Ask(self, u"Registrar Ganho", 16)
#
#     def end(self):
#         description = self.textbox_description.GetValue().capitalize()
#         val = float(self.textbox_value.GetValue().replace(",", "."))
#         if len(description) == 0 or val == 0:
#             a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
#             a.ShowModal()
#             a.Destroy()
#             return
#         finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
#             datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
#         date = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
#             "o", str(datetime.now().day))
#
#         if not self.argv:
#             inf = core.directory_paths['saves'] + self.month + '.txt'
#             pao = shelve.open(inf)
#             if 'spent' not in pao:
#                 pao['spent'] = {}
#                 pao['spcount'] = 0
#                 pao['winning'] = {}
#                 pao['wicount'] = 0
#                 pao['edit'] = {}
#             key = 1 + pao['wicount']
#             aw = pao['winning']
#             aw[key] = {'time': finish_time,
#                        'date': date,
#                        'edit': 0,
#                        'description': description,
#                        'value': val}
#             pao['winning'] = aw
#             pao['wicount'] = key
#             pao.close()
#         else:
#             pao = shelve.open(self.argv[0])
#             key = self.argv[1]
#             hour = self.argv[2]
#             asw = pao["edit"]
#             asw[finish_time] = pao["winning"][key]
#             asw[finish_time]['key'] = key
#             asw[finish_time]['mode'] = 1
#             pao["edit"] = asw
#             adw = pao["winning"]
#             adw[key] = {'time': hour,
#                         'date': adw[key]['date'],
#                         'edit': 1,
#                         'description': description,
#                         'value': val}
#             pao["winning"] = adw
#             pao.close()
#         self.clean()
#         if not self.argv:
#             dialogs.Confirmation(self, u"Sucesso", 7)
#         else:
#             self.GetParent().fill_31(1)
#             self.Close()
