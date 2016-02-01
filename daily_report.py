#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import record_editor
import sale
import expense
import waste
import database
import data_types

__author__ = 'Julio'


class Report(wx.Frame):

    panel_top = None
    combobox_day_option = None

    textbox_day_total = None
    textbox_sales_value = None
    textbox_sales_amount = None
    textbox_money_value = None
    textbox_money_amount = None
    textbox_card_value = None
    textbox_card_amount = None
    textbox_spent_value = None
    textbox_spent_amount = None
    textbox_cash_previous = None
    textbox_cash_ideal = None
    textbox_cash_real = None
    textbox_cash_tomorrow = None
    textbox_cash_removed = None

    list_sales = None
    list_expenses = None
    list_wastes = None

    available_lists = None

    cash_register = None

    def __init__(self, parent, title=u'Fechamento de Caixa'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup(None)

        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(75, 0))
        self.SetSize(wx.Size(1240, 720))
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        # first
        self.panel_top = wx.Panel(self, -1, pos=(10, 5), size=(1220, 50), style=wx.TAB_TRAVERSAL)
        self.panel_top.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        static_text_fechamento = wx.StaticText(self.panel_top, -1, u"Fechamento de:", pos=(300, 15))
        static_text_fechamento.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.setup_options()

        panel_top_buttons = wx.Panel(self.panel_top, -1, pos=(750, 5), size=(440, 40),
                                     style=wx.TAB_TRAVERSAL | wx.SIMPLE_BORDER)

        fupdate = GenBitmapTextButton(panel_top_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Atualizar janela', pos=(0, 0), size=(140, 40))
        fupdate.Bind(wx.EVT_BUTTON, self.reopen)
        pol = GenBitmapTextButton(panel_top_buttons, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Tools.png', wx.BITMAP_TYPE_PNG),
                                  u"Recuperação de registros", pos=(140, 0), size=(200, 40))
        pol.Bind(wx.EVT_BUTTON, self.open_record_editor)
        button_save = GenBitmapTextButton(panel_top_buttons, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Save.png', wx.BITMAP_TYPE_PNG),
                                          u"Salvar", pos=(340, 0), size=(100, 40))
        button_save.Bind(wx.EVT_BUTTON, self.save)

        # Painel das vendas
        panel1 = wx.Panel(self, -1, pos=(10, 65), size=(810, 260), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel1.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.list_sales = wx.gizmos.TreeListCtrl(panel1, -1, pos=(10, 5), size=(620, 250),
                                                 style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                 wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_sales.AddColumn(u"Descrição", width=250)
        self.list_sales.AddColumn(u"Quantidade", width=90)
        self.list_sales.AddColumn(u"Pagamento", width=150)
        self.list_sales.AddColumn(u"Valor", width=120)
        self.list_sales.SetMainColumn(0)
        panel1b = wx.Panel(panel1, pos=(650, 50), size=(145, 160), style=wx.SIMPLE_BORDER)
        plus = GenBitmapTextButton(panel1b, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                   u"Nova venda",
                                   pos=(0, 0), size=(145, 40))
        plus.Bind(wx.EVT_BUTTON, self.open_sale_register)
        edit = GenBitmapTextButton(panel1b, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                   u"Editar venda", pos=(0, 40), size=(145, 40))
        edit.Bind(wx.EVT_BUTTON, self.open_sale_edit)
        remove = GenBitmapTextButton(panel1b, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                     u'Apagar venda', pos=(0, 80), size=(145, 40))
        remove.Bind(wx.EVT_BUTTON, self.ask_delete_sale)
        update = GenBitmapTextButton(panel1b, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                     u'Atualizar', pos=(0, 120), size=(145, 40))
        update.Bind(wx.EVT_BUTTON, self.setup)

        # Painel dos gastos
        panel2 = wx.Panel(self, 53, pos=(10, 335), size=(810, 170), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel2.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.list_expenses = wx.gizmos.TreeListCtrl(panel2, -1, pos=(10, 5), size=(620, 160),
                                                    style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                    wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_expenses.AddColumn(u"Data/Horário", width=130)
        self.list_expenses.AddColumn(u"Descrição", width=280)
        self.list_expenses.AddColumn(u"Quantidade", width=90)
        self.list_expenses.AddColumn(u"Valor", width=110)
        self.list_expenses.SetMainColumn(0)
        panel2b = wx.Panel(panel2, pos=(650, 5), size=(145, 160), style=wx.SIMPLE_BORDER)
        splus = GenBitmapTextButton(panel2b, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                    u'Adicionar gasto', pos=(0, 0), size=(145, 40))
        splus.Bind(wx.EVT_BUTTON, self.open_expense_register)
        sedit = GenBitmapTextButton(panel2b, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                    u'Editar gasto', pos=(0, 40), size=(145, 40))
        sedit.Bind(wx.EVT_BUTTON, self.open_expense_edit)
        sremove = GenBitmapTextButton(panel2b, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                      u'Apagar gasto', pos=(0, 80), size=(145, 40))
        sremove.Bind(wx.EVT_BUTTON, self.ask_delete_expense)
        supdate = GenBitmapTextButton(panel2b, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Atualizar', pos=(0, 120), size=(145, 40))
        supdate.Bind(wx.EVT_BUTTON, self.setup)

        # Painel dos desperdicios
        panel_last = wx.Panel(self, 56, pos=(10, 515), size=(810, 170), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel_last.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.list_wastes = wx.gizmos.TreeListCtrl(panel_last, -1, pos=(10, 5), size=(620, 160),
                                                  style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                  wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_wastes.AddColumn(u"Descrição", width=280)
        self.list_wastes.AddColumn(u"Quantidade", width=90)
        self.list_wastes.AddColumn(u"Valor", width=110)
        self.list_wastes.SetMainColumn(0)
        panel_last_buttons = wx.Panel(panel_last, pos=(650, 5), size=(145, 160), style=wx.SIMPLE_BORDER)
        wplus = GenBitmapTextButton(panel_last_buttons, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                    u'Adicionar registro', pos=(0, 0), size=(145, 40))
        wplus.Bind(wx.EVT_BUTTON, self.open_waste_register)
        wedit = GenBitmapTextButton(panel_last_buttons, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                    u'Editar registro', pos=(0, 40), size=(145, 40))
        wedit.Bind(wx.EVT_BUTTON, self.open_waste_edit)
        wremove = GenBitmapTextButton(panel_last_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                      u'Apagar registro', pos=(0, 80), size=(145, 40))
        wremove.Bind(wx.EVT_BUTTON, self.ask_delete_waste)
        wupdate = GenBitmapTextButton(panel_last_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      'Atualizar', pos=(0, 120), size=(145, 40))
        wupdate.Bind(wx.EVT_BUTTON, self.setup, wupdate)

        self.available_lists = [self.list_sales, self.list_expenses, self.list_wastes]

        # Painel com o resulmo do dia
        panel3 = wx.Panel(self, -1, pos=(830, 65), size=(400, 620), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel3.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        part1 = wx.Panel(panel3, -1, pos=(5, 50), size=(390, 265), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        part2 = wx.Panel(panel3, -1, pos=(5, 320), size=(390, 85), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        part3 = wx.Panel(panel3, -1, pos=(5, 410), size=(390, 200), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)

        static_money_texts = []
        static_number_texts = []

        self.textbox_day_total = wx.TextCtrl(panel3, -1, "0,00", pos=(315, 10), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_sales_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 5), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_sales_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 50), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_money_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 95), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_money_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 140), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_card_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 185), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_card_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 230), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_spent_value = wx.TextCtrl(part2, -1, "0,00", pos=(310, 5), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_spent_amount = wx.TextCtrl(part2, -1, "0", pos=(310, 50), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_previous = wx.TextCtrl(part3, -1, "0,00", pos=(310, 5), size=(70, 30))
        self.textbox_cash_ideal = wx.TextCtrl(part3, -1, "0,00", pos=(310, 45), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_real = wx.TextCtrl(part3, -1, "0,00", pos=(310, 85), size=(70, 30))
        self.textbox_cash_tomorrow = wx.TextCtrl(part3, -1, "0,00", pos=(310, 125), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_removed = wx.TextCtrl(part3, -1, "0,00", pos=(310, 165), size=(70, 30))

        self.textbox_day_total.Disable()
        self.textbox_sales_value.Disable()
        self.textbox_sales_amount.Disable()
        self.textbox_money_value.Disable()
        self.textbox_money_amount.Disable()
        self.textbox_card_value.Disable()
        self.textbox_card_amount.Disable()
        self.textbox_spent_value.Disable()
        self.textbox_spent_amount.Disable()
        self.textbox_cash_ideal.Disable()
        self.textbox_cash_tomorrow.Disable()

        static_money_texts.append(wx.StaticText(panel3, -1, u"Total do dia", pos=(10, 17)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das Vendas", pos=(5, 12)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas", pos=(5, 57)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das vendas em dinheiro", pos=(5, 102)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas em dinheiro", pos=(5, 147)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das vendas no cartão", pos=(5, 192)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas no cartão", pos=(5, 237)))
        static_money_texts.append(wx.StaticText(part2, -1, u"Total de gastos", pos=(5, 12)))
        static_number_texts.append(wx.StaticText(part2, -1, u"Quantidade de gastos", pos=(5, 57)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa do dia anterior", pos=(5, 12)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa ideal", pos=(5, 52)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa real", pos=(5, 92)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa de amanhã", pos=(5, 132)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Dinheiro retirado", pos=(5, 172)))
        
        self.textbox_cash_previous.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_cash_real.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_cash_removed.Bind(wx.EVT_CHAR, core.check_money)

        self.textbox_cash_previous.Bind(wx.EVT_TEXT, self.update_cash)
        self.textbox_cash_real.Bind(wx.EVT_TEXT, self.update_cash)
        self.textbox_cash_removed.Bind(wx.EVT_TEXT, self.update_cash)

        # Adiciona os pontos em cada linha com os numeros a direita para facilitar a leitura
        mon = self.GetTextExtent('R$')[0]
        dot = self.GetTextExtent('.')[0]
        space = 302
        for box in static_money_texts:
            wid = box.GetSize()[0]
            post = box.GetPosition()[1]
            free = space - wid
            free = free - mon
            dots = free // dot
            if box is static_money_texts[0]:
                wx.StaticText(box.GetParent(), -1, '.' * dots + 'R$', pos=(10 + wid, post))
            else:
                wx.StaticText(box.GetParent(), -1, '.' * dots + 'R$', pos=(5 + wid, post))

        for box in static_number_texts:
            wid = box.GetSize()[0]
            post = box.GetPosition()[1]
            free = space - wid
            dots = free // dot
            wx.StaticText(box.GetParent(), -1, '.' * dots, pos=(5 + wid, post))

    def ask_delete_sale(self, event):
        boom = self.list_sales.GetSelection()
        if boom == self.list_sales.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Venda", 21)

    def ask_delete_expense(self, event):
        boom = self.list_expenses.GetSelection()
        if boom == self.list_expenses.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Gasto", 22)

    def ask_delete_waste(self, event):
        boom = self.list_wastes.GetSelection()
        if boom == self.list_wastes.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Registro", 23)

    def delete(self, box):
        """
        Apaga uma entrada em agum dos dados do dia
        :param box: TreeListCtrl da entrada
        :type box: wx.gizmos.TreeListCtrl
        :return:
        """
        boom = box.GetSelection()
        if boom == box.GetRootItem():
            return

        item_data = box.GetItemData(boom).GetData()

        if isinstance(item_data, data_types.ProductData):
            boom = box.GetItemParent(boom)
            item_data = box.GetItemData(boom).GetData()

        db = database.TransactionsDB()

        if box is self.list_sales:
            func = db.delete_sale
            sale.update_inventory(item_data, undo=True)
        elif box is self.list_expenses:
            func = db.delete_expense
        else:
            func = db.delete_waste
            waste.update_inventory(item_data, undo=True)

        func(item_data.ID)

        db.close()
        self.setup(None)

    def setup_options(self):
        db = database.TransactionsDB()

        month_options = list()

        for date in db.list_record_dates():
            month_options.append(core.format_date_user(date))

        db.close()

        self.combobox_day_option = wx.ComboBox(self.panel_top, -1, choices=month_options, size=(130, -1),
                                               pos=(420, 12), style=wx.CB_READONLY)
        self.combobox_day_option.Bind(wx.EVT_COMBOBOX, self.setup)
        if len(month_options) != 0:
            self.combobox_day_option.SetSelection(0)

    def setup(self, event):      # TODO Fazer a thread fechar direito com o resto do app
        self.combobox_day_option.Disable()
        self.__setup__()

    def __setup__(self):
        if self.combobox_day_option.GetValue() != u'':
            self.clean()
            transactions_db = database.TransactionsDB()
            inventory_db = database.InventoryDB()

            day = core.format_date_internal(self.combobox_day_option.GetValue())

            root = self.list_sales.AddRoot(u"Vendas de " + self.combobox_day_option.GetValue())
            self.list_sales.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            sales_value = 0.0
            sales_amount = 0
            money_value = 0.00
            money_amount = 0
            card_value = 0.00
            card_amount = 0

            day_sales = transactions_db.daily_sales_list(day)
            for sale_item in day_sales:
                sales_value += sale_item.value
                sold = self.list_sales.AppendItem(root, sale_item.record_time)
                self.list_sales.SetItemText(sold, sale_item.payment, 2)
                self.list_sales.SetItemText(sold, "R$ " + core.good_show("money", sale_item.value), 3)
                self.list_sales.SetItemFont(sold, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

                self.list_sales.SetItemData(sold, wx.TreeItemData(sale_item))

                for i in range(len(sale_item.products_IDs)):
                    product_id = sale_item.products_IDs[i]
                    product = inventory_db.inventory_search_id(int(product_id))

                    a = self.list_sales.AppendItem(sold, product.description)
                    self.list_sales.SetItemText(a, str(sale_item.amounts[i]), 1)
                    self.list_sales.SetItemText(a, core.format_cash_user(sale_item.prices[i], currency=True), 3)

                    self.list_sales.SetItemData(a, wx.TreeItemData(product))
                if sale_item.discount:
                    web = self.list_sales.AppendItem(sold, u"Desconto")
                    self.list_sales.SetItemText(web, "R$ " + core.good_show("money", sale_item.discount), 3)
                if sale_item.taxes:
                    bew = self.list_sales.AppendItem(sold, u"Taxas adicionais")
                    self.list_sales.SetItemText(bew, "R$ " + core.good_show("money", sale_item.taxes), 3)
                sales_amount += 1
                if sale_item.payment == u"Dinheiro":
                    money_amount += 1
                    money_value += float(sale_item.value)
                elif sale_item.payment.split()[0] == u"Cartão":
                    card_amount += 1
                    card_value += float(sale_item.value)

            self.list_sales.SetItemText(root, str(sales_amount), 2)
            self.list_sales.SetItemText(root, ("R$ " + core.good_show("money", sales_value)), 3)
            self.list_sales.Expand(root)

            raz = self.list_expenses.AddRoot(self.combobox_day_option.GetValue())
            expenses_value = 0.0
            expenses_amount = 0
            self.list_expenses.SetItemFont(raz, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

            day_expenses = transactions_db.daily_expenses_list(day)
            for expense_item in day_expenses:
                value = expense_item.value
                description = expense_item.description
                expenses_amount += 1
                expenses_value += value
                golf = self.list_expenses.AppendItem(raz, core.format_date_user(expense_item.record_time))
                self.list_expenses.SetItemText(golf, description, 1)
                self.list_expenses.SetItemText(golf, ("R$ " + core.good_show("money", value)), 3)

                self.list_expenses.SetItemData(golf, wx.TreeItemData(expense_item))

            self.list_expenses.SetItemText(raz, "Gastos", 1)
            self.list_expenses.SetItemText(raz, str(expenses_amount), 2)
            self.list_expenses.SetItemText(raz, ("R$ " + core.good_show("money", expenses_value)), 3)
            self.list_expenses.Expand(raz)

            pain = self.list_wastes.AddRoot(u"Desperdícios de " + self.combobox_day_option.GetValue())
            wastes_value = 0.0
            wastes_amount = 0
            self.list_wastes.SetItemFont(pain, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

            day_wastes = transactions_db.daily_wastes_list(day)
            for wasted in day_wastes:
                amount = wasted.amount
                product = inventory_db.inventory_search_id(wasted.product_ID)
                value = product.price * amount
                wastes_amount += 1
                wastes_value += value

                king = self.list_wastes.AppendItem(pain, product.description)
                self.list_wastes.SetItemText(king, str(amount), 1)
                self.list_wastes.SetItemText(king, ("R$ " + core.good_show("money", value)), 2)

                self.list_wastes.SetItemData(king, wx.TreeItemData(wasted))

            self.list_wastes.SetItemText(pain, str(wastes_amount), 1)
            self.list_wastes.SetItemText(pain, ("R$ " + core.good_show("money", wastes_value)), 2)
            self.list_wastes.Expand(pain)

            self.textbox_day_total.SetValue(core.good_show("money", sales_value - expenses_value))
            self.textbox_sales_value.SetValue(core.good_show("money", sales_value))
            self.textbox_sales_amount.SetValue(str(sales_amount))
            self.textbox_money_value.SetValue(core.good_show("money", money_value))
            self.textbox_money_amount.SetValue(str(money_amount))
            self.textbox_card_value.SetValue(core.good_show("money", card_value))
            self.textbox_card_amount.SetValue(str(card_amount))
            self.textbox_spent_value.SetValue(core.good_show("money", expenses_value))
            self.textbox_spent_amount.SetValue(str(expenses_amount))

            self.cash_register = transactions_db.cash_search_date(day)

            if self.cash_register:
                self.textbox_cash_previous.SetValue(core.format_cash_user(self.cash_register.fund))
                self.textbox_cash_real.SetValue(core.format_cash_user(self.cash_register.cash))
                self.textbox_cash_removed.SetValue(core.format_cash_user(self.cash_register.withdrawal))
            else:
                months = self.combobox_day_option.GetItems()
                last_movement = months[self.combobox_day_option.GetSelection()-1]
                cash_register = transactions_db.cash_search_date(core.format_date_internal(last_movement))
                if cash_register:
                    self.textbox_cash_previous.SetValue(core.format_cash_user(cash_register.cash))
                else:
                    self.textbox_cash_previous.SetValue('0,00')
                self.textbox_cash_real.SetValue('0,00')
                self.textbox_cash_removed.SetValue('0,00')

            self.update_cash(None)

            transactions_db.close()
            inventory_db.close()

            self.save(None)

            self.combobox_day_option.Enable()

    def update_cash(self, event):

        previous = core.money2float(self.textbox_cash_previous.GetValue())
        money = core.money2float(self.textbox_money_value.GetValue())
        spent = core.money2float(self.textbox_spent_value.GetValue())
        removed = core.money2float(self.textbox_cash_removed.GetValue())
        cash_real = core.money2float(self.textbox_cash_real.GetValue())

        cash_ideal = previous + money - spent

        self.textbox_cash_ideal.SetValue(core.good_show("money", cash_ideal))

        if not cash_real:
            cash_tomorrow = cash_ideal - removed
        else:
            cash_tomorrow = cash_real - removed

        if cash_tomorrow < 0:
            cash_tomorrow = 0.0

        self.textbox_cash_tomorrow.SetValue(core.good_show("money", cash_tomorrow))

    def clean(self):
        self.list_sales.DeleteAllItems()
        self.list_expenses.DeleteAllItems()
        self.list_wastes.DeleteAllItems()
        self.textbox_day_total.SetValue("0,00")
        self.textbox_sales_value.SetValue("0,00")
        self.textbox_sales_amount.SetValue("0")
        self.textbox_money_value.SetValue("0,00")
        self.textbox_money_amount.SetValue("0")
        self.textbox_card_value.SetValue("0,00")
        self.textbox_card_amount.SetValue("0")
        self.textbox_spent_value.SetValue("0,00")
        self.textbox_spent_amount.SetValue("0")
        self.textbox_cash_previous.SetValue("0,00")
        self.textbox_cash_ideal.SetValue("0,00")
        self.textbox_cash_real.SetValue("0,00")
        self.textbox_cash_tomorrow.SetValue("0,00")
        self.textbox_cash_removed.SetValue("0,00")

    def reopen(self, event):
        self.combobox_day_option.Destroy()
        self.setup_options()
        self.setup(None)

    def save(self, event):
        fund = core.money2float(self.textbox_cash_previous.GetValue())
        cash_ideal = core.money2float(self.textbox_cash_ideal.GetValue())
        cash_real = core.money2float(self.textbox_cash_real.GetValue())
        withdrawal = core.money2float(self.textbox_cash_removed.GetValue())
        if cash_real:
            cash = cash_real - withdrawal
        else:
            cash = cash_ideal - withdrawal
        if cash < 0:
            cash = 0.0

        db = database.TransactionsDB()

        if self.cash_register:
            self.cash_register.withdrawal = withdrawal
            self.cash_register.cash = cash
            self.cash_register.fund = fund

            db.edit_cash(self.cash_register)
        else:
            date = core.format_date_internal(self.combobox_day_option.GetValue())

            self.cash_register = data_types.CashRegisterData()
            self.cash_register.record_date = date
            self.cash_register.withdrawal = withdrawal
            self.cash_register.cash = cash
            self.cash_register.fund = fund

            db.insert_cash(self.cash_register)

        db.close()

    def open_sale_register(self, event):
        sale.Sale(self)

    def open_sale_edit(self, event):
        red = self.list_sales.GetSelection()
        if self.list_sales.GetRootItem() == red:
            return

        data = self.list_sales.GetItemData(red).GetData()
        if isinstance(data, data_types.ProductData):
            red = self.list_sales.GetItemParent(red)
            data = self.list_sales.GetItemData(red).GetData()

        sale.Sale(self, key=data.ID)

    def open_expense_register(self, event):
        expense.Expense(self)

    def open_expense_edit(self, event):
        red = self.list_expenses.GetSelection()
        if self.list_expenses.GetRootItem() == red:
            return
        data = self.list_expenses.GetItemData(red).GetData()

        expense.Expense(self, key=data.ID)

    def open_record_editor(self, event):
        record_editor.EditionManager(self, record_date=self.combobox_day_option.GetValue())

    def open_waste_register(self, event):
        waste.Waste(self)

    def open_waste_edit(self, event):
        red = self.list_wastes.GetSelection()
        if self.list_wastes.GetRootItem() == red:
            return
        data = self.list_wastes.GetItemData(red).GetData()

        waste.Waste(self, key=data.ID)

    def exit(self, event):
        self.save(event)
        self.Close()
