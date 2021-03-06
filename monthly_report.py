#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import threading

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import categories
import core
import dialogs
import transaction
import database
import data_types
import sale
import inventory
import waste
import expense

__author__ = 'Julio'


class Report(wx.Frame):

    combobox_month_displayed = None
    list_incomes = None
    list_expenses = None
    list_left = None
    list_right = None

    text_profit = None
    text_spent = None
    text_income = None
    text_wasted = None
    text_income_pendant = None
    text_expense_pendant = None
    text_daily_income = None
    text_credit_card_income = None
    text_better_week_day = None
    text_money_income = None
    text_worst_week_day = None
    text_income_pendant_amount = None
    text_expense_pendant_amount = None

    def __init__(self, parent, title=u"Resumo Mensal"):
        wx.Frame.__init__(self, parent, -1, title, size=(1200, 680),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()
        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        part1 = wx.Panel(self, -1, pos=(10, 10), size=(1180, 290), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.text_profit = wx.TextCtrl(part1, -1, pos=(200, 50), size=(100, 30), style=wx.TE_READONLY)
        self.text_income = wx.TextCtrl(part1, -1, pos=(200, 90), size=(100, 30), style=wx.TE_READONLY)
        self.text_spent = wx.TextCtrl(part1, -1, pos=(200, 130), size=(100, 30), style=wx.TE_READONLY)
        self.text_wasted = wx.TextCtrl(part1, -1, pos=(200, 170), size=(100, 30), style=wx.TE_READONLY)
        self.text_income_pendant = wx.TextCtrl(part1, -1, pos=(200, 210), size=(100, 30), style=wx.TE_READONLY)
        self.text_expense_pendant = wx.TextCtrl(part1, -1, pos=(200, 250), size=(100, 30), style=wx.TE_READONLY)
        self.text_daily_income = wx.TextCtrl(part1, -1, pos=(500, 10), size=(100, 30), style=wx.TE_READONLY)
        self.text_credit_card_income = wx.TextCtrl(part1, -1, pos=(500, 50), size=(100, 30), style=wx.TE_READONLY)
        self.text_money_income = wx.TextCtrl(part1, -1, pos=(500, 90), size=(100, 30), style=wx.TE_READONLY)
        self.text_worst_week_day = wx.TextCtrl(part1, -1, pos=(500, 130), size=(100, 30), style=wx.TE_READONLY)
        self.text_better_week_day = wx.TextCtrl(part1, -1, pos=(500, 170), size=(100, 30), style=wx.TE_READONLY)
        self.text_income_pendant_amount = wx.TextCtrl(part1, -1, pos=(500, 210), size=(100, 30), style=wx.TE_READONLY)
        self.text_expense_pendant_amount = wx.TextCtrl(part1, -1, pos=(500, 250), size=(100, 30), style=wx.TE_READONLY)
        self.list_left = wx.ListCtrl(part1, -1, pos=(625, 30), size=(250, 240),
                                     style=wx.SIMPLE_BORDER | wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.list_right = wx.ListCtrl(part1, -1, pos=(900, 30), size=(250, 240),
                                      style=wx.SIMPLE_BORDER | wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.list_left.InsertColumn(0, u'Descrição')
        self.list_left.InsertColumn(1, u'Quantidade')
        self.list_left.InsertColumn(2, u'Valor')
        self.list_right.InsertColumn(3, u'Descrição')
        self.list_right.InsertColumn(4, u'Quantidade')
        self.list_right.InsertColumn(5, u'Valor')
        wx.StaticText(part1, -1, u'Mês/Ano', pos=(10, 17))
        wx.StaticText(part1, -1, u'Lucro', pos=(10, 57))
        wx.StaticText(part1, -1, u'Receita', pos=(10, 97))
        wx.StaticText(part1, -1, u'Custos', pos=(10, 137))
        wx.StaticText(part1, -1, u'Total Perdido', pos=(10, 177))
        wx.StaticText(part1, -1, u'Entradas Pendentes de Pagamento', pos=(10, 217))
        wx.StaticText(part1, -1, u'Gastos Pendentes de Pagamento', pos=(10, 257))
        wx.StaticText(part1, -1, u'Rendimento Médio por dia', pos=(310, 17))
        wx.StaticText(part1, -1, u'Total Vendido no Cartão', pos=(310, 57))
        wx.StaticText(part1, -1, u'Total Vendido em Dinheiro', pos=(310, 97))
        wx.StaticText(part1, -1, u'Dia da Semana menos Rentável', pos=(310, 137))
        wx.StaticText(part1, -1, u'Dia da Semana mais Rentável', pos=(310, 177))
        wx.StaticText(part1, -1, u'Quantidade de Entradas Pendentes', pos=(310, 217))
        wx.StaticText(part1, -1, u'Quantidade de Gastos Pendentes', pos=(310, 257))

        wx.StaticText(part1, -1, u'Produtos de Maior Redimento', pos=(625, 10)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        wx.StaticText(part1, -1, u'Produtos Mais Vendidos', pos=(900, 10)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        part2 = wx.Panel(self, -1, pos=(10, 305), size=(1180, 50), style=wx.TAB_TRAVERSAL)
        part21 = wx.Panel(part2, -1, pos=(10, 0), size=(620, 50), style=wx.SIMPLE_BORDER)
        part22 = wx.Panel(part2, -1, pos=(790, 0), size=(380, 50), style=wx.SIMPLE_BORDER)
        button1 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Vendas', pos=(0, 0), size=(150, 50))
        button2 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Gastos', pos=(150, 0), size=(150, 50))
        button3 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Produtos', pos=(300, 0), size=(150, 50))
        button7 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Desperdícios', pos=(450, 0), size=(170, 50))
        button8 = GenBitmapTextButton(part2, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Recalcular', pos=(645, 0), size=(130, 50), style=wx.SIMPLE_BORDER)
        button4 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Registar Gasto', pos=(0, 0), size=(130, 50))
        button5 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Registrar Ganho', pos=(130, 0), size=(130, 50))
        button6 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Observações', pos=(260, 0), size=(120, 50))
        button1.Bind(wx.EVT_BUTTON, self.open_sheets_sales)
        button2.Bind(wx.EVT_BUTTON, self.open_sheets_expenses)
        button3.Bind(wx.EVT_BUTTON, self.open_sheets_products)
        button7.Bind(wx.EVT_BUTTON, self.open_sheets_wastes)
        button8.Bind(wx.EVT_BUTTON, self.setup)
        button4.Bind(wx.EVT_BUTTON, self.open_new_monthly_expense)
        button5.Bind(wx.EVT_BUTTON, self.open_new_monthly_income)
        button6.Bind(wx.EVT_BUTTON, self.open_text_box)
        button1.SetBackgroundColour(core.COLOR_LIGHT_YELLOW)
        button2.SetBackgroundColour(core.COLOR_LIGHT_YELLOW)
        button3.SetBackgroundColour(core.COLOR_LIGHT_YELLOW)
        button7.SetBackgroundColour(core.COLOR_LIGHT_YELLOW)
        button4.SetBackgroundColour(core.COLOR_LIGHT_BLUE)
        button5.SetBackgroundColour(core.COLOR_LIGHT_BLUE)
        button6.SetBackgroundColour(core.COLOR_LIGHT_BLUE)

        part3 = wx.Panel(self, pos=(10, 360), size=(1180, 280), style=wx.SIMPLE_BORDER)

        part31 = wx.Panel(part3, 56, pos=(10, 5), size=(575, 260), style=wx.SUNKEN_BORDER)
        part31.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.list_incomes = wx.gizmos.TreeListCtrl(part31, -1, pos=(10, 10), size=(400, 240),
                                                   style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                   wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_incomes.AddColumn(u"Data", width=110)
        self.list_incomes.AddColumn(u"Descrição", width=180)
        self.list_incomes.AddColumn(u"Valor", width=100)
        self.list_incomes.SetMainColumn(0)
        dr = wx.StaticText(part31, -1, u'Ganhos\nMensais', pos=(420, 10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        last_panel = wx.Panel(part31, pos=(420, 80), size=(145, 160), style=wx.SIMPLE_BORDER)

        button31 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                       u'Adicionar', pos=(0, 0), size=(145, 40))
        button32 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                       u'Editar', pos=(0, 40), size=(145, 40))
        button33 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                       u'Apagar', pos=(0, 80), size=(145, 40))
        button34 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                       u'Atualizar', pos=(0, 120), size=(145, 40))
        button31.Bind(wx.EVT_BUTTON, self.open_new_monthly_income)
        button32.Bind(wx.EVT_BUTTON, self.open_edit_monthly_income)
        button33.Bind(wx.EVT_BUTTON, self.ask_delete_income)
        button34.Bind(wx.EVT_BUTTON, self.setup_monthly_incomes)

        part32 = wx.Panel(part3, 56, pos=(590, 5), size=(575, 260), style=wx.SUNKEN_BORDER)
        part32.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.list_expenses = wx.gizmos.TreeListCtrl(part32, -1, pos=(10, 10), size=(400, 240),
                                                    style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                    wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_expenses.AddColumn(u"Data", width=110)
        self.list_expenses.AddColumn(u"Descrição", width=180)
        self.list_expenses.AddColumn(u"Valor", width=100)
        self.list_expenses.SetMainColumn(0)
        dr = wx.StaticText(part32, -1, u'Gastos\nMensais', pos=(420, 10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        last_buttons = wx.Panel(part32, pos=(420, 80), size=(145, 160), style=wx.SIMPLE_BORDER)

        button41 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                       u'Adicionar', pos=(0, 0), size=(145, 40))
        button42 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                       u'Editar', pos=(0, 40), size=(145, 40))
        button43 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                       u'Apagar', pos=(0, 80), size=(145, 40))
        button44 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                       u'Atualizar', pos=(0, 120), size=(145, 40))
        button41.Bind(wx.EVT_BUTTON, self.open_new_monthly_expense)
        button42.Bind(wx.EVT_BUTTON, self.open_edit_monthly_expense)
        button43.Bind(wx.EVT_BUTTON, self.ask_delete_expense)
        button44.Bind(wx.EVT_BUTTON, self.setup_monthly_expenses)

        db = database.TransactionsDB()
        dates = db.list_record_dates(transactions=True)
        db.close()

        month_options = list()

        for date in dates:
            date_ = core.format_date_user(date[:7])
            if date_ not in month_options:
                month_options.append(date_)

        self.combobox_month_displayed = wx.ComboBox(part1, -1, choices=month_options, size=(100, 30), pos=(200, 15),
                                                    style=wx.CB_READONLY)
        self.combobox_month_displayed.Bind(wx.EVT_COMBOBOX, self.setup)
        if len(month_options) != 0:
            self.combobox_month_displayed.SetValue(month_options[0])

    def clean(self):
        self.list_left.DeleteAllItems()
        self.list_right.DeleteAllItems()

    def setup(self, event):
        rest = threading.Thread(target=self.__setup__)
        rest.daemon = True
        rest.start()

    def __setup__(self):
        self.clean()
        
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        
        db = database.TransactionsDB()
        sales = db.monthly_sales_list(month)
        expenses = db.monthly_expenses_list(month)
        wastes = db.monthly_wastes_list(month)
        transactions = db.monthly_transactions_list(month)
        db.close()

        inventory_db = database.InventoryDB()

        total_expense = 0.0
        total_income = 0.0
        total_waste = 0.0
        total_card_income = 0.0
        total_money_income = 0.0
        dict_products = {}
        week_sold = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        days = []
        pendant_income = 0.0
        pendant_expense = 0.0
        pendant_income_count = 0
        pendant_expense_count = 0

        for sale_ in sales:
            date_ = sale_.record_date.split('-')
            week_day = calendar.weekday(int(date_[0]), int(date_[1]), int(date_[2]))
            if date_[2] not in days:
                days.append(date_[2])
            if not sale_.payment_pendant:
                total_income += sale_.value
                if sale_.payment == u'Dinheiro':
                    total_money_income += sale_.value
                elif sale_.payment.split()[0] == u'Cartão':
                    total_card_income += sale_.value
                week_sold[week_day] += sale_.value
            else:
                pendant_income += sale_.value
                pendant_income_count += 1
            for i in range(len(sale_.products_IDs)):
                product_id = sale_.products_IDs[i]
                if product_id not in dict_products:
                    dict_products[product_id] = [0, 0.0]
                dict_products[product_id][0] += sale_.amounts[i]
                dict_products[product_id][1] += sale_.prices[i]

        for expense_ in expenses:
            total_expense += expense_.value

        for waste_ in wastes:
            product = inventory_db.inventory_search_id(waste_.product_ID)
            total_waste += product.price * waste_.amount

        for transaction_ in transactions:
            if not transaction_.payment_pendant:
                if transaction_.type is transaction.INCOME:
                    total_income += transaction_.value
                elif transaction_.type is transaction.EXPENSE:
                    total_expense += transaction_.value
            else:
                if transaction_.type is transaction.INCOME:
                    pendant_income += transaction_.value
                    pendant_income_count += 1
                elif transaction_.type is transaction.EXPENSE:
                    pendant_expense += transaction_.value
                    pendant_expense_count += 1

        lp1 = []
        lp2 = []

        for item in range(0, 11):

            product_item_left = [u'', 0, 0.0, -1]
            for product_id in dict_products:
                if dict_products[product_id][1] > product_item_left[2]:
                    product_item_left = [inventory_db.inventory_search_id(product_id).description,
                                         dict_products[product_id][0], dict_products[product_id][1], product_id]

            product_item_right = [u'', 0, 0.0, -1]
            for product_id in dict_products:
                if dict_products[product_id][0] > product_item_right[1]:
                    product_item_right = [inventory_db.inventory_search_id(product_id).description,
                                          dict_products[product_id][0], dict_products[product_id][1], product_id]
            if product_item_left[2] and product_item_left not in lp1:
                lp1.append(product_item_left)
            if product_item_right[1] and product_item_right not in lp2:
                lp2.append(product_item_right)

        inventory_db.close()

        for item in lp1:
            item_id = self.list_left.Append((item[0], item[1], core.format_cash_user(item[2], currency=True)))
            self.list_left.SetItemData(item_id, item[3])
        for item in lp2:
            item_id = self.list_right.Append((item[0], item[1], core.format_cash_user(item[2], currency=True)))
            self.list_right.SetItemData(item_id, item[3])

        total_balance = (total_income - total_expense)

        try:
            average_daily_balance = (total_income - total_expense) / len(days)
        except ZeroDivisionError:
            average_daily_balance = 0.0

        if max(week_sold):
            weekday_best = core.week_days[week_sold.index(max(week_sold))]
        else:
            weekday_best = '-------'

        if min(week_sold):
            weekday_worse = core.week_days[week_sold.index(min(week_sold))]
        else:
            try:
                while not min(week_sold):
                    week_sold.remove(0.0)
                weekday_worse = core.week_days[week_sold.index(min(week_sold))]
                if weekday_best == weekday_worse:
                    weekday_worse = '-------'
            except ValueError:
                weekday_worse = '-------'

        self.text_profit.SetValue(core.format_cash_user(total_balance, currency=True))
        self.text_spent.SetValue(core.format_cash_user(total_expense, currency=True))
        self.text_income.SetValue(core.format_cash_user(total_income, currency=True))
        self.text_wasted.SetValue(core.format_cash_user(total_waste, currency=True))
        self.text_income_pendant.SetValue(core.format_cash_user(pendant_income, currency=True))
        self.text_expense_pendant.SetValue(core.format_cash_user(pendant_expense, currency=True))
        self.text_income_pendant_amount.SetValue(str(pendant_income_count))
        self.text_expense_pendant_amount.SetValue(str(pendant_expense_count))
        self.text_daily_income.SetValue(core.format_cash_user(average_daily_balance, currency=True))
        self.text_credit_card_income.SetValue(core.format_cash_user(total_card_income, currency=True))
        self.text_money_income.SetValue(core.format_cash_user(total_money_income, currency=True))
        self.text_worst_week_day.SetValue(weekday_best)
        self.text_better_week_day.SetValue(weekday_worse)
        self.setup_monthly_incomes(None)
        self.setup_monthly_expenses(None)

    def setup_monthly_incomes(self, event):
        self.list_incomes.DeleteAllItems()
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())

        db = database.TransactionsDB()
        incomes = db.monthly_transactions_list(month, transaction.INCOME)
        db.close()

        root = self.list_incomes.AddRoot(self.combobox_month_displayed.GetValue() or u'-----')
        self.list_incomes.SetItemText(root, u'Ganhos Mensais', 1)
        self.list_incomes.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        total = 0.0
        for income in incomes:
            x = self.list_incomes.AppendItem(root, core.format_date_user(income.transaction_date))
            self.list_incomes.SetItemText(x, income.description, 1)
            self.list_incomes.SetItemText(x, core.format_cash_user(income.value, currency=True), 2)

            self.list_incomes.SetItemData(x, wx.TreeItemData(income))

            total += income.value
        self.list_incomes.SetItemText(root, core.format_cash_user(total, currency=True), 2)
        self.list_incomes.ExpandAll(root)

    def setup_monthly_expenses(self, event):
        self.list_expenses.DeleteAllItems()
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())

        db = database.TransactionsDB()
        expenses = db.monthly_transactions_list(month, transaction.EXPENSE)
        db.close()

        root = self.list_expenses.AddRoot(self.combobox_month_displayed.GetValue() or u'-----')
        self.list_expenses.SetItemText(root, u'Gastos Mensais', 1)
        self.list_expenses.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        total = 0.0
        for expense_ in expenses:
            x = self.list_expenses.AppendItem(root, core.format_date_user(expense_.transaction_date))
            self.list_expenses.SetItemText(x, expense_.description, 1)
            self.list_expenses.SetItemText(x, core.format_cash_user(expense_.value, currency=True), 2)

            self.list_expenses.SetItemData(x, wx.TreeItemData(expense_))

            total += expense_.value
        self.list_expenses.SetItemText(root, core.format_cash_user(total, currency=True), 2)
        self.list_expenses.ExpandAll(root)

    def open_text_box(self, event):
        month = None
        dialogs.TextBox(self, month)

    def open_sheets_sales(self, event):
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        DataSheets(self, sheet_to_focus=1, month=month)

    def open_sheets_expenses(self, event):
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        DataSheets(self, sheet_to_focus=2, month=month)

    def open_sheets_products(self, event):
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        DataSheets(self, sheet_to_focus=3, month=month)

    def open_sheets_wastes(self, event):
        month = core.format_date_internal(self.combobox_month_displayed.GetValue())
        DataSheets(self, sheet_to_focus=4, month=month)

    def open_new_monthly_expense(self, event):
        transaction.Transaction(self, transaction_type=transaction.EXPENSE)

    def open_edit_monthly_expense(self, event):
        red = self.list_expenses.GetSelection()
        tree_data = self.list_expenses.GetItemData(red)
        if not tree_data:
            return
        data = tree_data.GetData()
        transaction.Transaction(self, transaction_type=transaction.EXPENSE, data=data)

    def open_new_monthly_income(self, event):
        transaction.Transaction(self, transaction_type=transaction.INCOME)

    def open_edit_monthly_income(self, event):
        red = self.list_incomes.GetSelection()
        tree_data = self.list_incomes.GetItemData(red)
        if not tree_data:
            return
        data = tree_data.GetData()
        transaction.Transaction(self, transaction_type=transaction.INCOME, data=data)

    def ask_delete_income(self, event):
        boom = self.list_incomes.GetSelection()
        if boom == self.list_incomes.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Ganho", 26)

    def ask_delete_expense(self, event):
        boom = self.list_expenses.GetSelection()
        if boom == self.list_expenses.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Gasto", 22)

    def data_delete(self, box):
        db = database.TransactionsDB()
        item = box.GetSelection()
        data = box.GetItemData(item).GetData()
        db.delete_transaction(data.ID)
        db.close()

        func = {
            self.list_incomes: self.setup_monthly_incomes,
            self.list_expenses: self.setup_monthly_expenses
        }

        func.get(box)(None)

    def exit(self, event):
        self.Close()


class DataSheets(wx.Frame):
    def __init__(self, parent, month, title=u'Tabelas', sheet_to_focus=1):
        wx.Frame.__init__(self, parent, -1, title, size=(970, 600))
        self.month = month
        self.parent = parent
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        box = wx.BoxSizer(wx.VERTICAL)
        note = wx.Notebook(self, style=wx.LEFT)
        if sheet_to_focus == 1:
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
        elif sheet_to_focus == 2:
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
        elif sheet_to_focus == 3:
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
        elif sheet_to_focus == 4:
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
        note.AddPage(self.main1, u'Vendas')
        note.AddPage(self.main2, u'Gastos')
        note.AddPage(self.main3, u'Produtos')
        note.AddPage(self.main4, u'Desperdícios')
        button_exit = GenBitmapTextButton(self, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png',
                                          wx.BITMAP_TYPE_PNG), u'Sair', pos=(600, -1), style=wx.SIMPLE_BORDER)
        button_exit.Bind(wx.EVT_BUTTON, self.exit)
        box.Add(note, 1, wx.EXPAND | wx.ALL, 5)
        box.Add(button_exit, 0, wx.ALL | wx.ALIGN_RIGHT, 15)
        self.SetSizer(box)
        note.SetSelection(sheet_to_focus - 1)

        self.Centre()
        self.Show()

    def exit(self, event):
        self.Close()


class Sheet(wx.gizmos.TreeListCtrl):
    def __init__(self, parent, content):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.content = content
        self.parent = parent.GetParent()
        self.month = self.parent.month
        setup_thead = threading.Thread(target=self.setup)
        setup_thead.daemon = True
        setup_thead.start()
        
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.process_click)
        
        self.Show()

    def setup(self):

        _setup_ = {
            'prod': self.setup_products,
            'won': self.setup_incomes,
            'loss': self.setup_expenses,
            'was': self.setup_wastes
        }

        _setup_[self.content]()

    def setup_products(self):
        inventory_db = database.InventoryDB()

        sales_db = database.TransactionsDB()
        sale_list = sales_db.monthly_sales_list(self.month)
        sales_db.close()

        plist = {}
        categories_dict = {}
        for sale_ in sale_list:
            for i in range(len(sale_.products_IDs)):
                key = sale_.products_IDs[i]
                if key in plist:
                    plist[key][0] += sale_.amounts[i]
                    plist[key][1] += sale_.prices[i]
                    plist[key][2] += 1
                else:
                    product = inventory_db.inventory_search_id(key)
                    plist[key] = [sale_.amounts[i], sale_.prices[i], 1, product.description, product.price, product]

                category_id = plist[key][5].category_ID

                if category_id in categories_dict:
                    categories_dict[category_id][0] += sale_.amounts[i]
                    categories_dict[category_id][1] += sale_.prices[i]
                    categories_dict[category_id][2] += 1
                else:
                    category = inventory_db.categories_search_id(category_id)
                    categories_dict[category_id] = [sale_.amounts[i], sale_.prices[i], 1,
                                                    category.category, category, None]
            
        inventory_db.close()
        self.AddColumn(u'ID', 100)
        self.AddColumn(u'Descrição', 300)
        self.AddColumn(u'Preço Unitário', 100)
        self.AddColumn(u'Quantidade vendida', 135)
        self.AddColumn(u'Quantidade de vezes vendido', 180)
        self.AddColumn(u'Valor', 115)
        root = self.AddRoot(u'------')
        self.SetItemText(root, u'Produtos Vendidos em %s' % core.format_date_user(self.month), 1)
        self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        a = 0.0
        b = 0.0
        counter = 0
        for product_id in plist:
            data = plist[product_id]
            category_id = data[5].category_ID
            data_category = categories_dict[category_id]

            if not data_category[5]:
                aux = self.AppendItem(root, core.format_id_user(category_id))
                self.SetItemText(aux, data_category[3], 1)
                self.SetItemText(aux, core.format_amount_user(data[0], unit=data_category[4].unit), 3)
                self.SetItemText(aux, str(data_category[2]), 4)
                self.SetItemText(aux, core.format_cash_user(data_category[1], currency=True), 5)
                self.SetItemData(aux, wx.TreeItemData(data_category[4]))
                self.SetItemFont(aux, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                data_category[5] = aux

            parent = data_category[5]
            item = self.AppendItem(parent, core.format_id_user(product_id))
            self.SetItemText(item, data[3], 1)
            self.SetItemText(item, core.format_cash_user(data[4], currency=True), 2)
            self.SetItemText(item, core.format_amount_user(data[0], unit=data_category[4].unit), 3)
            self.SetItemText(item, str(data[2]), 4)
            self.SetItemText(item, core.format_cash_user(data[1], currency=True), 5)

            self.SetItemData(item, wx.TreeItemData(data[5]))

            a += plist[product_id][1]
            b += plist[product_id][0]
            counter += 1
        self.SetItemText(root, core.format_amount_user(b), 3)
        self.SetItemText(root, str(counter), 4)
        self.SetItemText(root, core.format_cash_user(a, currency=True), 5)
        self.Expand(root)
        self.SortChildren(root)

    def setup_incomes(self):
        sales_db = database.TransactionsDB()
        sales = sales_db.monthly_sales_list(self.month)
        incomes = sales_db.monthly_transactions_list(self.month, transaction.INCOME)
        sales_db.close()

        self.AddColumn(u'Data/Horário', 250)
        self.AddColumn(u'Pagamento', 150)
        self.AddColumn(u'Descrição', 250)
        self.AddColumn(u'Quantidade', 100)
        self.AddColumn(u'Valor', 150)
        root = self.AddRoot(u'Ganhos de %s' % core.date_reverse(self.month).replace('-', '/'))
        self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        a = 0.0
        b = 0
        days = {}
        saturdays = core.week_end(self.month)
        weeks = {}

        for sale_ in sales:
            for day in saturdays:
                if day >= int(sale_.record_date.split('-')[2]):
                    week = saturdays.index(day) + 1
                    break
            if week not in weeks:
                we = self.AppendItem(root, u'%iª Semana' % week)
                self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                weeks[week] = [we, 0.0, 0]
            if sale_.record_date not in days:
                item = self.AppendItem(weeks[week][0], core.format_date_user(sale_.record_date))
                self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                days[sale_.record_date] = [item, 0.0, 0]

            b += 1
            a += sale_.value
            weeks[week][1] += sale_.value
            weeks[week][2] += 1
            days[sale_.record_date][1] += sale_.value
            days[sale_.record_date][2] += 1

            father = self.AppendItem(days[sale_.record_date][0], sale_.record_time)
            self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.SetItemText(father, sale_.payment, 1)
            self.SetItemText(father, u'-----------', 2)
            self.SetItemText(father, str(len(sale_.products_IDs)), 3)
            self.SetItemText(father, core.format_cash_user(sale_.value, currency=True), 4)

            self.SetItemData(father, wx.TreeItemData(sale_))

            for i in range(len(sale_.products_IDs)):
                kid = self.AppendItem(father, u'-----------')
                self.SetItemText(kid, u'-----------', 1)
                self.SetItemText(kid, core.format_id_user(sale_.products_IDs[i]), 2)
                self.SetItemText(kid, core.format_amount_user(sale_.amounts[i]), 3)
                self.SetItemText(kid, core.format_cash_user(sale_.prices[i], currency=True), 4)

                self.SetItemData(kid, wx.TreeItemData(str(sale_.products_IDs[i])))

        for j in weeks:
            self.SetItemText(weeks[j][0], str(weeks[j][2]), 3)
            self.SetItemText(weeks[j][0], core.format_cash_user(weeks[j][1], currency=True), 4)
        for j in days:
            self.SetItemText(days[j][0], str(days[j][2]), 3)
            self.SetItemText(days[j][0], core.format_cash_user(days[j][1], currency=True), 4)
            self.SortChildren(days[j][0])

        if len(incomes):
            parent = self.AppendItem(root, u'Outras entradas de dinheiro')
            self.SetItemFont(parent, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            for income in incomes:
                b += 1
                a += income.value

                payment = u'RECEBIDO'
                payment = payment if not income.payment_pendant else u'AINDA NÃO ' + payment

                father = self.AppendItem(parent, core.format_date_user(income.transaction_date))
                self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.SetItemText(father, payment, 1)
                self.SetItemText(father, income.description, 2)
                self.SetItemText(father, core.format_cash_user(income.value, currency=True), 4)

                self.SetItemData(father, wx.TreeItemData(income))

        self.SetItemText(root, str(b), 3)
        self.SetItemText(root, core.format_cash_user(a, currency=True), 4)
        self.Expand(root)
        self.SortChildren(root)

    def setup_expenses(self):
        expenses_db = database.TransactionsDB()
        expenses = expenses_db.monthly_expenses_list(self.month)
        money_exits = expenses_db.monthly_transactions_list(self.month, transaction.EXPENSE)
        expenses_db.close()

        self.AddColumn(u'Data/Horário', 250)
        self.AddColumn(u'Pagamento', 150)
        self.AddColumn(u'Descrição', 250)
        self.AddColumn(u'Quantidade', 100)
        self.AddColumn(u'Valor', 150)
        root = self.AddRoot(u'Gastos de %s' % core.date_reverse(self.month).replace('-', '/'))
        self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        a = 0.0
        b = 0
        days = {}
        saturdays = core.week_end(self.month)
        weeks = {}

        for expense_ in expenses:
            for day in saturdays:
                if day >= int(expense_.record_date.split('-')[2]):
                    week = saturdays.index(day) + 1
                    break
            if week not in weeks:
                we = self.AppendItem(root, u'%iª Semana' % week)
                self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                weeks[week] = [we, 0.0, 0]
            if expense_.record_date not in days:
                item = self.AppendItem(weeks[week][0], core.format_date_user(expense_.record_date))
                self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                days[expense_.record_date] = [item, 0.0, 0]

            b += 1
            a += expense_.value
            weeks[week][1] += expense_.value
            weeks[week][2] += 1
            days[expense_.record_date][1] += expense_.value
            days[expense_.record_date][2] += 1

            father = self.AppendItem(days[expense_.record_date][0], expense_.record_time)
            self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.SetItemText(father, expense_.description, 2)
            self.SetItemText(father, core.format_cash_user(expense_.value, currency=True), 4)

            self.SetItemData(father, wx.TreeItemData(expense_))

        for j in weeks:
            self.SetItemText(weeks[j][0], str(weeks[j][2]), 3)
            self.SetItemText(weeks[j][0], core.format_cash_user(weeks[j][1], currency=True), 4)
        for j in days:
            self.SetItemText(days[j][0], str(days[j][2]), 3)
            self.SetItemText(days[j][0], core.format_cash_user(days[j][1], currency=True), 4)
            self.SortChildren(days[j][0])

        if len(money_exits):
            parent = self.AppendItem(root, u'Outros Gastos')
            self.SetItemFont(parent, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            for money_exit in money_exits:
                b += 1
                a += money_exit.value

                payment = u'RECEBIDO'
                payment = payment if not money_exit.payment_pendant else u'AINDA NÃO ' + payment

                father = self.AppendItem(parent, core.format_date_user(money_exit.transaction_date))
                self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.SetItemText(father, payment, 1)
                self.SetItemText(father, money_exit.description, 2)
                self.SetItemText(father, core.format_cash_user(money_exit.value, currency=True), 4)

                self.SetItemData(father, wx.TreeItemData(money_exit))

        self.SetItemText(root, str(b), 3)
        self.SetItemText(root, core.format_cash_user(a, currency=True), 4)
        self.Expand(root)
        self.SortChildren(root)

    def setup_wastes(self):

        inventory_db = database.InventoryDB()

        wastes_db = database.TransactionsDB()
        waste_list = wastes_db.monthly_wastes_list(self.month)
        wastes_db.close()

        walist = {}
        for waste_ in waste_list:
            if waste_.product_ID in walist:
                walist[waste_.product_ID][0] += waste_.amount
                walist[waste_.product_ID][1] += 1
            else:
                product = inventory_db.inventory_search_id(waste_.product_ID)
                walist[waste_.product_ID] = [waste_.amount, 1, product.description, product.price, waste_]

        self.AddColumn(u'ID', 100)
        self.AddColumn(u'Descrição', 300)
        self.AddColumn(u'Preço Unitário', 100)
        self.AddColumn(u'Quantidade', 100)
        self.AddColumn(u'Quantidade de vezes', 150)
        self.AddColumn(u'Valor', 200)
        root = self.AddRoot(u'------')
        self.SetItemText(root, u'Desperdícios de %s' % core.format_date_user(self.month), 1)
        self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        a = 0.0
        b = 0.0
        counter = 0

        for product_id in walist:
            value = walist[product_id][3]*walist[product_id][0]
            item = self.AppendItem(root, str(product_id))
            self.SetItemText(item, walist[product_id][2], 1)
            self.SetItemText(item, core.format_cash_user(walist[product_id][3], currency=True), 2)
            self.SetItemText(item, core.format_amount_user(walist[product_id][0]), 3)
            self.SetItemText(item, str(walist[product_id][1]), 4)
            self.SetItemText(item, core.format_cash_user(value, currency=True), 5)

            self.SetItemData(item, wx.TreeItemData(walist[product_id][4]))

            a += value
            b += walist[product_id][0]
            counter += 1
        self.SetItemText(root, core.format_amount_user(b), 3)
        self.SetItemText(root, str(counter), 4)
        self.SetItemText(root, core.format_cash_user(a, currency=True), 5)
        self.Expand(root)
        self.SortChildren(root)

    def process_click(self, event):
        selection = self.GetSelection()
        tree_data = self.GetItemData(selection)
        if not tree_data:
            event.Skip()
            return 
        data = tree_data.GetData()

        if isinstance(data, data_types.SaleData):
            sale.Sale(self.parent, data=data, editable=False)
        elif isinstance(data, data_types.ProductData):
            inventory.ProductData(self.parent, data.description, data=data, editable=False)
        elif isinstance(data, str):
            inventory.ProductData(self.parent, core.format_id_user(data), product_id=int(data), editable=False)
        elif isinstance(data, data_types.ProductCategoryData):
            categories.ProductCategoryData(self.parent, data.category, data=data)
        elif isinstance(data, data_types.WasteData):
            waste.Waste(self.parent, data=data)
        elif isinstance(data, data_types.ExpenseData):
            expense.Expense(self.parent, data=data)
