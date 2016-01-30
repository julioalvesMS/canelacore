#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import data_types
import database

__author__ = 'Julio'


class EditionManager(wx.Frame):
    combobox_day_option = None
    combobox_month_option = None
    combobox_entry_type = None

    list_edited_data = None

    panel_control = None

    file_name = None
    dict_modified_entries = None

    days_files = None
    day_options = None

    def __init__(self, parent, title=u'Recuperação de Registros', record_date=''):
        wx.Frame.__init__(self, parent, -1, title, size=(1000, 430),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.record_date = record_date

        self.setup_gui()

        self.setup_options()
        self.data_update(None)
        self.Show()

    def setup_gui(self):
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.Centre()
        self.SetBackgroundColour(core.default_background_color)
        panel_original = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.list_edited_data = wx.gizmos.TreeListCtrl(panel_original, -1, pos=(10, 10), size=(710, 360),
                                                       style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                       wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_edited_data.AddColumn(u"Horário", width=120)
        self.list_edited_data.AddColumn(u"ID", width=95)
        self.list_edited_data.AddColumn(u"Descrição", width=210)
        self.list_edited_data.AddColumn(u"Quantidade", width=90)
        self.list_edited_data.AddColumn(u"Valor", width=100)
        self.list_edited_data.SetMainColumn(0)
        self.list_edited_data.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.process_click)

        self.panel_control = wx.Panel(self, -1, size=(240, 380), pos=(750, 10),
                                      style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        wx.StaticText(self.panel_control, -1, u"Registros de", pos=(5, 80))

        see = GenBitmapTextButton(self.panel_control, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                  u"Ver mais sobre o registro", pos=(5, 180), size=(230, 50), style=wx.SIMPLE_BORDER)
        see.Bind(wx.EVT_BUTTON, self.process_click)

        rec = GenBitmapTextButton(self.panel_control, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                  u"Recuperar registro", pos=(5, 230), size=(230, 50), style=wx.SIMPLE_BORDER)
        rec.Bind(wx.EVT_BUTTON, self.ask_remove)

    def setup(self, event):
        two = threading.Thread(target=self.__setup__)
        two.daemon = True
        two.start()

    def setup_options(self):
        db = database.TransactionsDB()
        record_dates = db.list_record_dates(deleted=True)
        transactions_dates = db.list_transactions_dates(deleted=True)
        db.close()

        day_options = core.convert_list(record_dates, core.format_date_user)
        month_options = list()
        for date in transactions_dates:
            month = core.format_date_user(date[:-3])
            if month not in month_options:
                month_options.append(month)

        entry_types = [u'Gastos, Vendas e Desperdícios', u'Clientes, Produtos e Categorias', u'Transações e Categorias']

        self.combobox_entry_type = wx.ComboBox(self.panel_control, choices=entry_types, size=(230, -1), pos=(5, 30),
                                               style=wx.CB_READONLY | wx.TE_MULTILINE)
        self.combobox_entry_type.Bind(wx.EVT_COMBOBOX, self.data_update)

        self.combobox_month_option = wx.ComboBox(self.panel_control, -1, choices=month_options, size=(130, -1),
                                                 pos=(5, 100), style=wx.CB_READONLY)
        self.combobox_month_option.Bind(wx.EVT_COMBOBOX, self.setup)

        self.combobox_day_option = wx.ComboBox(self.panel_control, -1, choices=day_options, size=(130, -1),
                                               pos=(5, 100), style=wx.CB_READONLY)
        self.combobox_day_option.Bind(wx.EVT_COMBOBOX, self.setup)

        self.combobox_entry_type.SetSelection(1)
        if len(month_options):
            self.combobox_month_option.SetSelection(0)
        if len(day_options):
            self.combobox_day_option.SetSelection(0)
            self.combobox_entry_type.SetSelection(0)

    def data_update(self, event):
        char = self.combobox_entry_type.GetSelection()
        if char == 0:
            self.combobox_day_option.Enable()
            self.combobox_month_option.Hide()
            self.combobox_day_option.Show()
        elif char == 1:
            self.combobox_day_option.Disable()
            self.combobox_month_option.Disable()
        elif char == 2:
            self.combobox_month_option.Enable()
            self.combobox_day_option.Hide()
            self.combobox_month_option.Show()
        self.setup(None)

    def __setup__(self):
        self.clean()
        entry_selection = self.combobox_entry_type.GetSelection()
        if entry_selection == 0 and self.combobox_day_option.GetValue():
            self.setup_selection_0()
        elif entry_selection == 1:
            self.setup_selection_1()
        elif entry_selection == 2 and self.combobox_month_option.GetValue():
            self.setup_selection_2()

    def setup_selection_0(self):
        date_user = self.combobox_day_option.GetValue()
        date = core.format_date_internal(date_user)
        main_root = self.list_edited_data.AddRoot(date_user)
        self.list_edited_data.SetItemText(main_root, u"Registros Apagados", 2)

        db = database.TransactionsDB()
        sales = db.daily_sales_list(date, deleted=True)
        expenses = db.daily_expenses_list(date, deleted=True)
        wastes = db.daily_wastes_list(date, deleted=True)
        db.close()

        sales_counter = len(sales)
        expenses_counter = len(expenses)
        wastes_counter = len(wastes)

        value = 0.0
        sales_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(sales_root, u"Vendas", 2)
        self.list_edited_data.SetItemText(sales_root, str(sales_counter), 3)
        self.list_edited_data.SetItemFont(sales_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in sales:
            value += data.value

            item = self.list_edited_data.AppendItem(sales_root, data.record_time)
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, str(len(data.products_IDs)), 3)
            self.list_edited_data.SetItemText(item, core.format_cash_user(data.value, currency=True), 4)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))
            for i in range(len(data.products_IDs)):
                price = data.amounts[i] * data.prices[i]
                product = self.list_edited_data.AppendItem(item, u"---------")
                self.list_edited_data.SetItemText(product, core.format_id_user(data.products_IDs[i]), 1)
                self.list_edited_data.SetItemText(product, core.format_amount_user(data.amounts[i]), 3)
                self.list_edited_data.SetItemText(product, core.format_cash_user(price, currency=True), 4)

            if data.discount != 0:
                extra = self.list_edited_data.AppendItem(item, u"---------")
                self.list_edited_data.SetItemText(extra, u'Desconto', 2)
                self.list_edited_data.SetItemText(extra, core.format_cash_user(data.discount, currency=True), 4)
            if data.taxes != 0:
                extra = self.list_edited_data.AppendItem(item, u"---------")
                self.list_edited_data.SetItemText(extra, u'Taixas adicionais', 2)
                self.list_edited_data.SetItemText(extra, core.format_cash_user(data.discount, currency=True), 4)

        self.list_edited_data.SetItemText(sales_root, core.format_cash_user(value, currency=True), 4)

        value = 0.0
        expenses_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(expenses_root, u"Gastos", 2)
        self.list_edited_data.SetItemText(expenses_root, str(expenses_counter), 3)
        self.list_edited_data.SetItemFont(expenses_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in expenses:
            value += data.value

            item = self.list_edited_data.AppendItem(expenses_root, data.record_time)
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, data.description, 2)
            self.list_edited_data.SetItemText(item, core.format_cash_user(data.value, currency=True), 4)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        self.list_edited_data.SetItemText(expenses_root, core.format_cash_user(value, currency=True), 4)

        wastes_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(wastes_root, u"Desperdícios", 2)
        self.list_edited_data.SetItemText(wastes_root, str(expenses_counter), 3)
        self.list_edited_data.SetItemFont(wastes_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in wastes:

            item = self.list_edited_data.AppendItem(wastes_root, data.record_time)
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, core.format_id_user(data.product_ID), 2)
            self.list_edited_data.SetItemText(item, core.format_amount_user(data.amount), 3)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        self.list_edited_data.SetItemText(main_root, str(sales_counter + wastes_counter + expenses_counter), 3)
        self.list_edited_data.Expand(main_root)
        self.list_edited_data.SetItemFont(main_root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

    def setup_selection_1(self):
        main_root = self.list_edited_data.AddRoot(u"---------")
        self.list_edited_data.SetItemText(main_root, u"Registros Apagados", 2)

        db = database.InventoryDB()
        products = db.product_list(deleted=True)
        categories = db.categories_list(deleted=True)
        db.close()

        db = database.ClientsDB()
        clients = db.clients_list(deleted=True)
        db.close()

        clients_counter = len(clients)
        products_counter = len(products)
        categories_counter = len(categories)

        clients_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(clients_root, u"Clientes", 2)
        self.list_edited_data.SetItemText(clients_root, str(clients_counter), 3)
        self.list_edited_data.SetItemFont(clients_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in clients:

            item = self.list_edited_data.AppendItem(clients_root, u"---------")
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, data.name, 2)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        products_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(products_root, u"Produtos", 2)
        self.list_edited_data.SetItemText(products_root, str(products_counter), 3)
        self.list_edited_data.SetItemFont(products_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in products:

            item = self.list_edited_data.AppendItem(products_root, u"---------")
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, data.description, 2)
            self.list_edited_data.SetItemText(item, core.format_amount_user(data.amount), 3)
            self.list_edited_data.SetItemText(item, core.format_cash_user(data.price, currency=True), 4)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        categories_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(categories_root, u"Categorias", 2)
        self.list_edited_data.SetItemText(categories_root, str(categories_counter), 3)
        self.list_edited_data.SetItemFont(categories_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in categories:

            item = self.list_edited_data.AppendItem(categories_root, u"---------")
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, data.category, 2)

            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        self.list_edited_data.SetItemFont(main_root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.list_edited_data.SetItemText(main_root, str(categories_counter + products_counter + clients_counter), 3)
        self.list_edited_data.Expand(main_root)

    def setup_selection_2(self):
        month_user = self.combobox_month_option.GetValue()
        date = core.format_date_internal(month_user)
        main_root = self.list_edited_data.AddRoot(month_user)
        self.list_edited_data.SetItemText(main_root, u"Registros Apagados", 2)

        db = database.TransactionsDB()
        transactions = db.monthly_transactions_list(date, deleted=True)
        db.close()

        incomes_counter = 0
        expenses_counter = 0

        expenses_value = 0.0
        expenses_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(expenses_root, u"Gastos", 2)
        self.list_edited_data.SetItemText(expenses_root, str(expenses_counter), 3)
        self.list_edited_data.SetItemFont(expenses_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))

        incomes_value = 0.0
        income_root = self.list_edited_data.AppendItem(main_root, u"---------")
        self.list_edited_data.SetItemText(income_root, u"Entrada", 2)
        self.list_edited_data.SetItemText(income_root, str(expenses_counter), 3)
        self.list_edited_data.SetItemFont(income_root, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        for data in transactions:
            if data.type == data_types.EXPENSE:
                parent = expenses_root
                expenses_counter += 1
                expenses_value += data.value
            elif data.type == data_types.INCOME:
                parent = income_root
                incomes_counter += 1
                incomes_value += data.value
            else:
                parent = main_root

            item = self.list_edited_data.AppendItem(parent, data.transaction_date)
            self.list_edited_data.SetItemFont(item, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.list_edited_data.SetItemText(item, core.format_id_user(data.ID), 1)
            self.list_edited_data.SetItemText(item, data.description, 2)
            self.list_edited_data.SetItemText(item, core.format_cash_user(data.value, currency=True), 4)
            self.list_edited_data.SetItemData(item, wx.TreeItemData(data))

        self.list_edited_data.SetItemText(income_root, core.format_cash_user(incomes_value, currency=True), 4)
        self.list_edited_data.SetItemText(expenses_root, core.format_cash_user(expenses_value, currency=True), 4)

        self.list_edited_data.SetItemText(main_root, str(incomes_counter + expenses_counter), 3)
        self.list_edited_data.Expand(main_root)
        self.list_edited_data.SetItemFont(main_root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

    def ask_remove(self, event):
        boom = self.list_edited_data.GetSelection()
        key2 = str(self.list_edited_data.GetItemText(boom, 0))
        if boom == self.list_edited_data.GetRootItem() or len(key2) == 10:
            return
        dialogs.Ask(self, u"Restauração", 30)

    def delete(self):
        item = self.list_edited_data.GetSelection()
        tree_data = self.list_edited_data.GetItemData(item)
        if not tree_data:
            return
        data = tree_data.GetData()

        _type_ = None

        if isinstance(data, data_types.SaleData):
            _type_ = data_types.SaleData
        elif isinstance(data, data_types.ExpenseData):
            _type_ = data_types.ExpenseData
        elif isinstance(data, data_types.WasteData):
            _type_ = data_types.WasteData
        elif isinstance(data, data_types.ClientData):
            _type_ = data_types.ClientData
        elif isinstance(data, data_types.ProductData):
            _type_ = data_types.ProductData
        elif isinstance(data, data_types.ProductCategoryData):
            _type_ = data_types.ProductCategoryData
        elif isinstance(data, data_types.TransactionData):
            _type_ = data_types.TransactionData

        db_functions = {
            data_types.SaleData: (database.TransactionsDB, database.TransactionsDB.delete_sale),
            data_types.ExpenseData: (database.TransactionsDB, database.TransactionsDB.delete_expense),
            data_types.WasteData: (database.TransactionsDB, database.TransactionsDB.delete_waste),
            data_types.ClientData: (database.ClientsDB, database.ClientsDB.delete_client),
            data_types.ProductData: (database.InventoryDB, database.InventoryDB.delete_product),
            data_types.ProductCategoryData: (database.InventoryDB, database.InventoryDB.delete_category)
        }

        general_database, delete_function = db_functions.get(_type_)

        db = general_database()
        delete_function(db, data.ID, undo=not data.active)
        db.close()
        self.setup(None)

    def process_click(self, event):
        selection = self.list_edited_data.GetSelection()
        tree_data = self.list_edited_data.GetItemData(selection)
        if not tree_data:
            event.Skip()
            return
        data = tree_data.GetData()

        if isinstance(data, data_types.SaleData):
            import sale
            sale.Sale(self, data=data, editable=False)
        elif isinstance(data, data_types.ProductData):
            import inventory
            inventory.ProductData(self, data.description, data=data, editable=False)
        elif isinstance(data, data_types.ProductCategoryData):
            import categories
            categories.ProductCategoryData(self, data=data)
        elif isinstance(data, data_types.WasteData):
            import waste
            waste.Waste(self, data=data)
        elif isinstance(data, data_types.ExpenseData):
            import expense
            expense.Expense(self, data=data)
        elif isinstance(data, data_types.TransactionData):
            import transaction
            transaction.Transaction(self, transaction_type=data.type, data=data)
        elif isinstance(data, data_types.ClientData):
            import clients
            clients.ClientData(self, data.name, data.ID, data=data, editable=False)

    def clean(self):
        self.list_edited_data.DeleteAllItems()

    def exit(self, event):
        self.Close()
