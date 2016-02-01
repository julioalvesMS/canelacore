#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.gizmos
import wx.calendar
from wx.lib.buttons import GenBitmapTextButton

import categories
import core
import dialogs
import database
import data_types
import monthly_report

__author__ = 'Julio'

INCOME = 1
EXPENSE = 2


class Transaction(wx.Frame):

    textbox_description = None
    textbox_value = None

    combobox_category = None

    checkbox_payed = None

    calendar_date = None

    categories_ids = [None]

    def __init__(self, parent, transaction_type, key=-1, data=None):

        title_options = {
            EXPENSE: u'Despesa',
            INCOME: u'Entrada'
        }
        title = title_options.get(transaction_type, u'Transação')

        wx.Frame.__init__(self, parent, -1, title, size=(660, 300),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.key = key
        self.data = data
        self.transaction_type = transaction_type

        self.setup_gui()

        self.setup()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        # first
        first = wx.Panel(self, -1, size=(495, 250), pos=(10, 10), style=wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL)
        first.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        wx.StaticText(first, -1, u"Descrição: *", pos=(20, 20))
        self.textbox_description = wx.TextCtrl(first, -1, pos=(20, 40), size=(200, 30))

        wx.StaticText(first, -1, u"Categoria:", pos=(20, 90))
        self.combobox_category = wx.ComboBox(first, -1, pos=(20, 110), size=(165, 30), style=wx.CB_READONLY)
        self.update_categories()

        button_category = wx.BitmapButton(first, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                          pos=(185, 105), size=(32, 32), style=wx.NO_BORDER)
        button_category.Bind(wx.EVT_BUTTON, self.open_category_register)
        button_category.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        wx.StaticText(first, -1, u"Valor: *", pos=(20, 160))
        self.textbox_value = wx.TextCtrl(first, -1, pos=(20, 180), size=(200, 30))
        self.textbox_value.Bind(wx.EVT_CHAR, core.check_currency)
        self.textbox_value.SetValue(u'R$ 0,00')

        wx.StaticText(first, -1, u"Data da Transação: *", pos=(240, 35))
        self.calendar_date = wx.calendar.CalendarCtrl(first, -1, wx.DateTime_Now(), pos=(240, 55),
                                                      style=wx.calendar.CAL_SHOW_HOLIDAYS |
                                                      wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION |
                                                      wx.calendar.CAL_BORDER_ROUND | wx.SIMPLE_BORDER)

        self.checkbox_payed = wx.CheckBox(first, -1, u'Pagamento Realizado? ', pos=(200, 220), size=(-1, -1),
                                          style=wx.ALIGN_LEFT)
        self.checkbox_payed.SetFont(wx.Font(-1, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Bind(wx.EVT_CHECKBOX, self.checkbox_change, self.checkbox_payed)
        self.checkbox_payed.SetForegroundColour(wx.BLUE)
        self.checkbox_payed.SetValue(True)
        self.checkbox_payed.SetSize((160, -1))

        # last
        last = wx.Panel(self, -1, size=(130, 250), pos=(515, 10), style=wx.SIMPLE_BORDER)
        last.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        last_ = wx.Panel(last, pos=(5, 65), size=(120, 120), style=wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                     u'Finalizar', pos=(0, 0), size=(120, 40))
        finish.Bind(wx.EVT_BUTTON, self.ask_end)
        restart = GenBitmapTextButton(last_, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Recomeçar', pos=(0, 40), size=(120, 40))
        restart.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u"sair", pos=(0, 80), size=(120, 40))
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)

    def setup(self):
        if self.data:
            self.key = self.data.ID
        elif self.key != -1:
            db = database.TransactionsDB()
            self.data = db.transactions_search_id(self.key)
            db.close()
        else:
            return
        self.textbox_description.SetValue(self.data.description)
        self.textbox_value.SetValue(core.format_cash_user(self.data.value, currency=True))
        date = self.data.transaction_date.split('-')
        wx_date = wx.DateTime()
        wx_date.Set(int(date[2]), int(date[1]) - 1, int(date[0]))
        self.calendar_date.SetDate(wx_date)
        try:
            self.combobox_category.SetSelection(self.categories_ids.index(self.data.category))
        except ValueError:
            pass

    def ask_clean(self, event):
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = str(self.textbox_description.GetValue())
        po = str(self.textbox_value.GetValue())
        if pl == u'' and po == u'R$ 0,00':
            self.exit(None)
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):

        ask_option = -1
        if self.transaction_type is EXPENSE:
            ask_option = 12
        elif self.transaction_type is INCOME:
            ask_option = 16

        dialogs.Ask(self, u"Registrar Transação", ask_option)

    def checkbox_change(self, event):
        if self.checkbox_payed.GetValue():
            self.checkbox_payed.SetForegroundColour(wx.BLUE)
        else:
            self.checkbox_payed.SetForegroundColour(wx.RED)

    def open_category_register(self, event):
        categories.TransactionCategoryData(self)

    def update_categories(self):
        db = database.TransactionsDB()
        category_list = db.categories_list()
        category_options = [u'Selecione']
        self.categories_ids = [None]
        for category in category_list:
            category_options.append(category.category)
            self.categories_ids.append(category.ID)
        self.combobox_category.SetItems(category_options)
        self.combobox_category.SetSelection(0)
        db.close()

    def clean(self):
        self.textbox_description.Clear()
        self.textbox_value.SetValue(u"R$ 0,00")
        self.calendar_date.SetDate(wx.DateTime_Now())
        self.update_categories()

    def exit(self, event):
        self.Close()

    def end(self):
        description = self.textbox_description.GetValue().capitalize()
        val = core.money2float(self.textbox_value.GetValue())
        if len(description) == 0 or val == 0:
            return dialogs.launch_error(self, u'Dados insulficientes')
        date, finish_time = core.datetime_today()

        wx_date = self.calendar_date.GetDate()
        transaction_date = u'%i-%s-%i' % (wx_date.GetYear(), core.good_show('o', str(wx_date.GetMonth() + 1)),
                                          wx_date.GetDay())

        data = data_types.TransactionData()
        data.ID = self.key
        data.description = description
        data.category = self.categories_ids[self.combobox_category.GetSelection()]
        data.value = val
        data.record_date = date
        data.record_time = finish_time
        data.transaction_date = transaction_date
        data.type = self.transaction_type
        data.payment_pendant = not self.checkbox_payed.GetValue()

        db = database.TransactionsDB()
        if self.key == -1:
            db.insert_transaction(data)
        else:
            db.edit_transaction(data)
        db.close()

        parent = self.GetParent()
        if isinstance(parent, monthly_report.Report):
            funcs = {
                EXPENSE: parent.setup_monthly_expenses,
                INCOME: parent.setup_monthly_incomes
            }
            setup = funcs[self.transaction_type]
            setup(None)

        if self.key == -1:
            self.clean()
            confirmation_option = -1
            if self.transaction_type is EXPENSE:
                confirmation_option = 2
            elif self.transaction_type is INCOME:
                confirmation_option = 7
            dialogs.Confirmation(self, u"Sucesso", confirmation_option)

        else:
            self.exit(None)
