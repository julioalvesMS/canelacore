#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

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


class TransactionManager(wx.Frame):

    notebook_lists = None

    list_expenses = None
    list_incomes = None

    combobox_month_displayed = None

    def __init__(self, parent, title=u'Transaçoes'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        db = database.TransactionsDB()
        dates = db.list_transactions_dates()
        db.close()

        months = list()

        for date in dates:
            month = core.format_date_user(date[:-3])
            if month not in months:
                months.append(month)
        if months:
            self.combobox_month_displayed.SetItems(months)
            self.combobox_month_displayed.SetSelection(0)

        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(100, 100))
        self.SetSize(wx.Size(1140, 560))
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        panel_top = wx.Panel(self, pos=(10, 10), size=(1120, 100))

        button_categories = GenBitmapTextButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'Drawer.png',
                                                wx.BITMAP_TYPE_PNG), u'Categorias', pos=(5, 40), size=(115, 40),
                                                style=wx.SIMPLE_BORDER)
        button_categories.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        button_categories.Bind(wx.EVT_BUTTON, self.open_category_manager)

        button_payment = GenBitmapTextButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'Check.png',
                                             wx.BITMAP_TYPE_PNG), u'Pagamento Realizado', pos=(140, 40),
                                             size=(160, 40), style=wx.SIMPLE_BORDER)
        button_payment.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        button_payment.Bind(wx.EVT_BUTTON, self.data_edit_payment)

        panel_buttons_left = wx.Panel(panel_top, pos=(320, 40), size=(400, 40), style=wx.SIMPLE_BORDER)

        see = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Search.png', wx.BITMAP_TYPE_PNG),
                                  u'Ver Mais', pos=(0, 0), size=(100, 40))
        see.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        see.Bind(wx.EVT_BUTTON, self.data_open)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(100, 0), size=(100, 40))
        plus.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        plus.Bind(wx.EVT_BUTTON, self.open_new_transaction)

        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(200, 0), size=(100, 40))
        edi.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)

        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(300, 0), size=(100, 40))
        era.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)

        self.combobox_month_displayed = wx.ComboBox(panel_top, -1, pos=(745, 45), size=(100, 30), style=wx.CB_READONLY)

        self.combobox_month_displayed.Bind(wx.EVT_TEXT_ENTER, self.setup)

        panel_buttons_right = wx.Panel(panel_top, pos=(870, 40), size=(240, 40), style=wx.SIMPLE_BORDER)
        quir = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                   u'Sair',
                                   pos=(120, 0), size=(120, 40))
        quir.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        quir.Bind(wx.EVT_BUTTON, self.exit)
        rep = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                  u'Atualizar',
                                  pos=(0, 0), size=(120, 40))
        rep.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        rep.Bind(wx.EVT_BUTTON, self.setup)
        self.notebook_lists = wx.Notebook(self, -1, pos=(15, 110), size=(1110, 410))
        self.notebook_lists.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        for i in range(2):
            list_transactions = wx.ListCtrl(self.notebook_lists, -1,
                                            style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
            list_transactions.InsertColumn(0, u'Descrição', width=400)
            list_transactions.InsertColumn(1, u'ID', width=90)
            list_transactions.InsertColumn(2, u'Categoria', width=250)
            list_transactions.InsertColumn(3, u'Valor', width=110)
            list_transactions.InsertColumn(4, u'Data', width=120)
            list_transactions.InsertColumn(5, u'Pagamento', width=130)

            list_transactions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_open)

            if not i:
                self.list_expenses = list_transactions
                text = u'Contas e Gastos'
            else:
                self.list_incomes = list_transactions
                text = u'Ganhos e Entradas'

            self.notebook_lists.AddPage(list_transactions, text)

    def setup(self, event):     # FIXME Fazer a thread fechar direito com o resto do app
        rest = threading.Thread(target=self.__setup__)
        rest.start()

    def __setup__(self):
        self.setup_monthly_list(EXPENSE)
        self.setup_monthly_list(INCOME)

    def setup_monthly_list(self, data_type):

        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        date = core.datetime_today()[0]

        lists = {
            EXPENSE: self.list_expenses,
            INCOME: self.list_incomes
        }
        list_ctrl = lists[data_type]

        list_ctrl.DeleteAllItems()

        db = database.TransactionsDB()
        transaction_registered = db.monthly_transactions_list(month, data_type)
        for _transaction in transaction_registered:

            category = db.categories_search_id(_transaction.category)
            item = list_ctrl.Append((_transaction.description, core.format_id_user(_transaction.ID),
                                    category.category if category else u'',
                                    core.format_cash_user(_transaction.value, currency=True),
                                    core.format_date_user(_transaction.transaction_date),
                                    u'OK' if not _transaction.payment_pendant else u'Pendente'))

            # Atribui uma cor ao item caso o pagamento ainda não tenha sido realizado
            if _transaction.payment_pendant:
                self.setup_item_color(item, data_type)

        db.close()

    def setup_item_color(self, item, data_type):

        lists = {
            EXPENSE: self.list_expenses,
            INCOME: self.list_incomes
        }
        list_ctrl = lists[data_type]

        date = core.datetime_today()[0]
        transaction_date = core.format_date_internal(list_ctrl.GetItemText(item, 4))

        date_diference = core.date2int(transaction_date) - core.date2int(date)

        if date_diference < 0:
            color = '#FC1501'
        elif date_diference < 2:
            color = '#FF8600'
        else:
            color = '#1C86EE'
        list_ctrl.SetItemTextColour(item, color)

    def data_delete(self, event):

        if self.notebook_lists.GetSelection():
            data_list = self.list_incomes

        else:
            data_list = self.list_expenses

        it = data_list.GetFocusedItem()
        if it == -1:
            return
        e_id = data_list.GetItem(it, 1).GetText()

        db = database.TransactionsDB()
        db.delete_transaction(int(e_id))
        db.close()
        self.setup(None)

    def data_edit(self, event):
        if self.notebook_lists.GetSelection():
            data_list = self.list_incomes
            transaction_type = INCOME
        else:
            data_list = self.list_expenses
            transaction_type = EXPENSE

        it = data_list.GetFocusedItem()
        if it == -1:
            return

        key = data_list.GetItem(it, 1).GetText()

        Transaction(self, transaction_type=transaction_type, key=key)

    def data_edit_payment(self, event):
        if self.notebook_lists.GetSelection():
            data_list = self.list_incomes
            data_type = INCOME
        else:
            data_list = self.list_expenses
            data_type = EXPENSE

        it = data_list.GetFocusedItem()
        if it == -1:
            return

        key = data_list.GetItemText(it, 1)

        payment = data_list.GetItemText(it, 5)

        undo = True if payment == u'OK' else False

        db = database.TransactionsDB()
        db.edit_transaction_payment(key, undo=undo)
        db.close()

        data_list.SetStringItem(it, 5, u'OK' if not undo else u'Pendente')
        self.setup_item_color(it, data_type)

    def data_open(self, event):
        if self.notebook_lists.GetSelection():
            data_list = self.list_incomes
            transaction_type = INCOME
        else:
            data_list = self.list_expenses
            transaction_type = EXPENSE

        it = data_list.GetFocusedItem()
        if it == -1:
            return

        key = data_list.GetItem(it, 1).GetText()
        Transaction(self, transaction_type=transaction_type, key=key, editable=False)

    def ask_delete(self, event):
        if self.notebook_lists.GetSelection():
            dialogs.Ask(self, u'Apagar Transação', 26)
        else:
            dialogs.Ask(self, u'Apagar Transação', 22)

    def open_category_manager(self, event):
        categories.TransactionCategoryManager(self)

    def open_new_transaction(self, event):
        if self.notebook_lists.GetSelection():
            transaction_type = INCOME
        else:
            transaction_type = EXPENSE

        Transaction(self, transaction_type=transaction_type)

    def exit(self, event):
        self.Close()


class Transaction(wx.Frame):

    textbox_description = None
    textbox_value = None

    combobox_category = None

    checkbox_payed = None

    calendar_date = None

    categories_ids = [None]

    def __init__(self, parent, transaction_type, key=-1, data=None, editable=True):

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
        self.editable = editable

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

        if self.editable:

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

        else:
            self.textbox_description.Disable()
            self.textbox_value.Disable()
            self.combobox_category.Disable()
            self.calendar_date.Disable()
            self.checkbox_payed.Disable()

            last_ = wx.Panel(last, pos=(5, 85), size=(120, 80), style=wx.SIMPLE_BORDER)
            edit = GenBitmapTextButton(last_, 243,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                       u"Editar",
                                       pos=(0, 0), size=(120, 40))
            edit.Bind(wx.EVT_BUTTON, self.open_transaction_edit)
            cancel = GenBitmapTextButton(last_, 242,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(0, 40), size=(120, 40))
            cancel.Bind(wx.EVT_BUTTON, self.exit)

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
        self.checkbox_payed.SetValue(not self.data.payment_pendant)
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

    def open_transaction_edit(self, event):
        Transaction(parent=self.GetParent(), transaction_type=self.transaction_type, key=self.key, data=self.data)
        self.exit(None)

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
