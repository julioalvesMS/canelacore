#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import inventory
import clients
import core
import daily_report
import dialogs
import database
import data_types
import sat

__author__ = 'Julio'


def update_inventory(data, undo=False):
    """
    Atualiza o estoque de acordo com uma venda
    :type data: data_types.SaleData
    :type undo: bool
    :param data: dados da venda
    :param undo: Caso True desfaz as mudanças causadas no BD pela venda
    :return: None
    :rtype: None
    """
    db = database.InventoryDB()
    for i in range(len(data.products_IDs)):
        prduct_id = data.products_IDs[i]
        amount = data.amounts[i] if undo else -data.amounts[i]

        db.update_product_stock(prduct_id, amount)
    db.close()


class Sale(wx.Frame):
    item = None
    delivery_enabled = False
    database_inventory = None
    database_filtered_inventory = None

    delivery = None

    radio_payment_check = None
    radio_payment_credit_card = None
    radio_payment_debit_card = None
    radio_payment_money = None
    radio_payment_pendant = None
    radio_payment_other = None
    textbox_payment_other = None

    textbox_product_description = None
    textbox_product_id = None
    textbox_product_price = None
    textbox_product_amount = None
    textbox_product_unit = None

    textbox_sale_discount = None
    textbox_sale_taxes = None
    textbox_sale_products_price = None
    textbox_sale_value = None

    textbox_client_name = None
    textbox_client_cpf = None
    textbox_client_id = None

    textbox_delivery_receiver = None
    textbox_delivery_address = None
    textbox_delivery_telephone = None
    textbox_delivery_city = None
    textbox_delivery_date = None
    textbox_delivery_hour = None

    list_inventory = None
    list_sold = None

    panel_product_data = None
    __panel_product = None

    def __init__(self, parent, title=u'Vendas', key=-1, data=None, delivery_id=-1, editable=True):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.key = key
        self.data = data
        self.editable = editable
        self.delivery_id = delivery_id

        self.database_inventory = database.InventoryDB(':memory:')

        self.setup_gui()
        self.setup()

        self.update_sale_data(None)

        if self.editable:
            self.database_search(None)

        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(200, 25))
        self.SetSize(wx.Size(925, 700))
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))

        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        # result
        result = wx.Panel(self, -1, pos=(5, 5), size=(450, 605), style=wx.DOUBLE_BORDER | wx.TAB_TRAVERSAL)
        result.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        self.list_sold = wx.ListCtrl(result, -1, pos=(10, 10), size=(430, 400),
                                     style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.list_sold.InsertColumn(1, u"Descrição", width=180)
        self.list_sold.InsertColumn(2, u"Quantidade")
        self.list_sold.InsertColumn(3, u"Preço Unit.")
        self.list_sold.InsertColumn(4, u"Preço")

        wx.StaticText(result, -1, u"Forma de Pagamento:", (10, 420))
        self.radio_payment_money = wx.RadioButton(result, -1, u"Dinheiro", (15, 440))
        self.radio_payment_credit_card = wx.RadioButton(result, -1, u"Cartão de Crédito", (15, 465))
        self.radio_payment_debit_card = wx.RadioButton(result, -1, u"Cartão de Débito", (15, 490))
        self.radio_payment_check = wx.RadioButton(result, -1, u"Cheque", (15, 515))
        self.radio_payment_pendant = wx.RadioButton(result, -1, u"Ainda não pagou", (15, 540))
        self.radio_payment_other = wx.RadioButton(result, -1, u"Outra", (15, 565))
        self.textbox_payment_other = wx.TextCtrl(result, -1, pos=(80, 560), size=(120, 25))
        self.textbox_payment_other.Disable()
        self.radio_payment_pendant.SetForegroundColour(wx.RED)
        self.update_payment_method(None)
        self.radio_payment_money.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_credit_card.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_debit_card.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_check.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_other.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_pendant.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_money.SetValue(True)

        wx.StaticText(result, -1, u"Total:  R$", (312, 427))
        self.textbox_sale_products_price = wx.TextCtrl(result, -1, u'0,00', (370, 420), size=(60, 30),
                                                       style=wx.TE_READONLY)
        self.textbox_sale_products_price.Disable()
        wx.StaticText(result, -1, u"Desconto:  R$", (285, 460))
        self.textbox_sale_discount = wx.TextCtrl(result, -1, u'0,00', pos=(370, 453), size=(60, 30))
        self.textbox_sale_discount.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_sale_discount.Bind(wx.EVT_TEXT, self.update_sale_data)
        wx.StaticText(result, -1, u"Taxas:  R$", (310, 493))
        self.textbox_sale_taxes = wx.TextCtrl(result, -1, u'0,00', (370, 486), size=(60, 30))
        self.textbox_sale_taxes.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_sale_taxes.Bind(wx.EVT_TEXT, self.update_sale_data)
        wx.StaticText(result, -1, u"Total da Venda:  R$", (255, 540))
        self.textbox_sale_value = wx.TextCtrl(result, -1, u'0,00', (370, 533), size=(60, 30), style=wx.TE_READONLY)
        self.textbox_sale_value.Disable()
        wx.StaticLine(result, -1, (285, 525), (150, 1))

        if not self.editable:
            self.textbox_sale_taxes.Disable()
            self.textbox_sale_discount.Disable()
            self.textbox_payment_other.Disable()
            self.radio_payment_money.Disable()
            self.radio_payment_credit_card.Disable()
            self.radio_payment_debit_card.Disable()
            self.radio_payment_check.Disable()
            self.radio_payment_pendant.Disable()
            self.radio_payment_other.Disable()

        # product
        self.panel_product_data = wx.Panel(self, 22, pos=(460, 5), size=(450, 275),
                                           style=wx.DOUBLE_BORDER | wx.TAB_TRAVERSAL)
        self.panel_product_data.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        wx.StaticText(self.panel_product_data, -1, u"Adicionar Produto", pos=(160, 8)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        fin = wx.BitmapButton(self.panel_product_data, -1, wx.Bitmap(core.directory_paths['icons'] + 'Add.png'),
                              pos=(408, 25), size=(32, 32), style=wx.NO_BORDER)
        fin.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        fin.Bind(wx.EVT_BUTTON, self.open_product_register)

        self.textbox_product_description = wx.SearchCtrl(self.panel_product_data, 223, pos=(10, 25), size=(395, 32))
        self.textbox_product_description.Bind(wx.EVT_TEXT, self.database_search, id=223)
        self.textbox_product_description.ShowSearchButton(False)
        self.textbox_product_description.SetDescriptiveText(u'Descrição do produto')
        self.list_inventory = wx.ListCtrl(self.panel_product_data, -1, pos=(10, 60), size=(430, 115),
                                          style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.list_inventory.InsertColumn(0, u'Descrição', width=230)
        self.list_inventory.InsertColumn(1, u'Estoque')
        self.list_inventory.InsertColumn(2, u'Preço')
        self.list_inventory.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.database_select)

        self.textbox_product_id = wx.SearchCtrl(self.panel_product_data, -1, pos=(10, 185), size=(100, -1))
        self.textbox_product_id.ShowSearchButton(False)
        self.textbox_product_id.SetDescriptiveText(u'ID')

        self.textbox_product_price = wx.SearchCtrl(self.panel_product_data, -1, pos=(130, 185), size=(80, -1))
        self.textbox_product_price.ShowSearchButton(False)
        self.textbox_product_price.SetDescriptiveText(u'Preço')
        self.textbox_product_price.SetValue(u'R$ 0,00')
        self.textbox_product_price.Disable()

        self.textbox_product_amount = wx.SearchCtrl(self.panel_product_data, -1, pos=(230, 185), size=(100, -1))
        self.textbox_product_amount.ShowSearchButton(False)
        self.textbox_product_amount.SetDescriptiveText(u'Quantidade')

        self.textbox_product_unit = wx.TextCtrl(self.panel_product_data, -1, pos=(335, 190), size=(50, -1),
                                                style=wx.NO_BORDER | wx.TE_READONLY)
        self.textbox_product_unit.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        self.__panel_product = wx.Panel(self.panel_product_data, size=(300, 40), pos=(100, 225),
                                        style=wx.SIMPLE_BORDER)
        button_add_product = GenBitmapTextButton(self.__panel_product, 220,
                                                 wx.Bitmap(core.directory_paths['icons'] + 'Add.png',
                                                           wx.BITMAP_TYPE_PNG),
                                                 u"Adicionar", pos=(0, 0), size=(100, 40))
        button_add_product.Bind(wx.EVT_BUTTON, self.data_insert, id=220)
        button_product_editor = GenBitmapTextButton(self.__panel_product, 221,
                                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png',
                                                              wx.BITMAP_TYPE_PNG),
                                                    u'Editar', pos=(100, 0), size=(100, 40))
        button_product_editor.Bind(wx.EVT_BUTTON, self.data_editor_enable, id=221)
        button_remove_product = GenBitmapTextButton(self.__panel_product, 222,
                                                    wx.Bitmap(core.directory_paths['icons'] + 'Trash.png',
                                                              wx.BITMAP_TYPE_PNG),
                                                    u'Apagar', pos=(200, 0), size=(100, 40))
        button_remove_product.Bind(wx.EVT_BUTTON, self.data_delete, id=222)

        if not self.editable:
            self.textbox_product_description.Disable()
            self.list_inventory.Disable()
            self.textbox_product_price.Disable()
            self.textbox_product_amount.Disable()
            button_add_product.Disable()
            button_product_editor.Disable()
            button_remove_product.Disable()

        # client
        client = wx.Panel(self, 23, pos=(460, 285), size=(450, 325), style=wx.DOUBLE_BORDER | wx.TAB_TRAVERSAL)
        client.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        wx.StaticText(client, -1, u"Nome do cliente: ", pos=(10, 5))
        wx.StaticText(client, -1, u"CPF: ", pos=(250, 5))
        wx.StaticText(client, -1, u"ID: ", pos=(375, 5))
        self.textbox_client_name = wx.TextCtrl(client, -1, pos=(10, 25), size=(215, 25))
        self.textbox_client_cpf = wx.TextCtrl(client, -1, pos=(250, 25), size=(100, 25))
        self.textbox_client_id = wx.TextCtrl(client, -1, pos=(375, 25), size=(50, 25))
        self.textbox_client_cpf.Bind(wx.EVT_CHAR, core.check_cpf)
        self.textbox_client_id.Bind(wx.EVT_CHAR, core.check_number)
        client_ = wx.Panel(client, -1, pos=(10, 60), size=(400, 40), style=wx.SIMPLE_BORDER)
        cold = GenBitmapTextButton(client_, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Book.png', wx.BITMAP_TYPE_PNG),
                                   u'Selecionar Cliente', pos=(0, 0), size=(150, 40))
        cnew = GenBitmapTextButton(client_, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo Cliente', pos=(150, 0), size=(150, 40))
        cno = GenBitmapTextButton(client_, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Cancel.png', wx.BITMAP_TYPE_PNG),
                                  u'Limpar', pos=(300, 0), size=(100, 40))
        cold.Bind(wx.EVT_BUTTON, self.open_client_manager)
        cnew.Bind(wx.EVT_BUTTON, self.open_client_register)
        cno.Bind(wx.EVT_BUTTON, self.clean_client)
        self.delivery = wx.CheckBox(client, 213, u"Entrega?", (10, 110))
        self.delivery.Bind(wx.EVT_CHECKBOX, self.setup_delivery)
        wx.StaticText(client, -1, u"Nome do recebente:", pos=(10, 130))
        wx.StaticText(client, -1, u"Endereço da entrega:", pos=(10, 180))
        wx.StaticText(client, -1, u"Telefone \ndo cliente:", pos=(10, 240))
        wx.StaticText(client, -1, u"Cidade:", pos=(215, 247))
        wx.StaticText(client, -1, u"        Data:", pos=(10, 287))
        wx.StaticText(client, -1, u"Horário:", pos=(210, 287))
        self.textbox_delivery_receiver = wx.TextCtrl(client, -1, pos=(10, 150), size=(415, 25))
        self.textbox_delivery_address = wx.TextCtrl(client, -1, pos=(10, 200), size=(415, 25))
        self.textbox_delivery_telephone = wx.TextCtrl(client, -1, pos=(80, 240), size=(120, 25))
        self.textbox_delivery_city = wx.TextCtrl(client, -1, pos=(260, 240), size=(120, 25))
        self.textbox_delivery_date = wx.TextCtrl(client, -1, pos=(80, 280), size=(120, 25))
        self.textbox_delivery_hour = wx.TextCtrl(client, -1, pos=(260, 280), size=(120, 25))

        self.textbox_delivery_telephone.Bind(wx.EVT_CHAR, core.check_telephone)
        self.textbox_delivery_date.Bind(wx.EVT_CHAR, core.check_date_simple)
        self.textbox_delivery_hour.Bind(wx.EVT_CHAR, core.check_hour)

        self.textbox_client_name.Disable()
        self.textbox_delivery_receiver.Disable()
        self.textbox_delivery_address.Disable()
        self.textbox_delivery_telephone.Disable()
        self.textbox_delivery_city.Disable()
        self.textbox_delivery_date.Disable()
        self.textbox_delivery_hour.Disable()
        if not self.editable:
            self.textbox_client_name.Disable()
            self.textbox_client_cpf.Disable()
            self.textbox_client_id.Disable()
            self.delivery.Disable()
            cold.Disable()
            cnew.Disable()
            cno.Disable()

        # last
        last = wx.Panel(self, 24, pos=(5, 615), size=(905, 50), style=wx.DOUBLE_BORDER | wx.TAB_TRAVERSAL)
        last.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        if self.editable:
            last_ = wx.Panel(last, pos=(292, 5), size=(320, 40), style=wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(last_, 240,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                         u"Finalizar", pos=(0, 0), size=(100, 40))
            finish.Bind(wx.EVT_BUTTON, self.ask_end, id=240)
            restart = GenBitmapTextButton(last_, 241,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                          u"Recomeçar", pos=(100, 0), size=(120, 40))
            restart.Bind(wx.EVT_BUTTON, self.ask_clean, id=241)
            cancel = GenBitmapTextButton(last_, 242,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(220, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.ask_exit, id=242)
        else:
            last_ = wx.Panel(last, pos=(352, 5), size=(200, 40), style=wx.SIMPLE_BORDER)
            edit = GenBitmapTextButton(last_, 243,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                       u"Editar",
                                       pos=(0, 0), size=(100, 40))
            edit.Bind(wx.EVT_BUTTON, self.open_sale_edit)
            cancel = GenBitmapTextButton(last_, 242,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(100, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.exit)

    def setup(self):

        if self.data:
            self.key = self.data.ID
        elif self.key != -1:
            db = database.TransactionsDB()
            self.data = db.sales_search_id(self.key)
            db.close()
        else:
            return

        # Adiciona os dados do cliente
        if self.data.client_cpf:
            self.textbox_client_cpf.SetValue(core.format_cpf(self.data.client_cpf))
        if self.data.client_id:
            self.textbox_client_id.SetValue(core.format_id_user(self.data.client_id))

        # Caso haja, adiciona os dados da entrega
        if self.delivery_id is not -1:
            db = database.DeliveriesDB()
            delivery_data = db.deliveries_search_id(self.delivery_id)
            db.close()

            self.delivery.SetValue(True)
            if self.editable:
                self.setup_delivery(None)

            self.textbox_client_name.SetValue(delivery_data.client)
            self.textbox_delivery_receiver.SetValue(delivery_data.receiver)
            self.textbox_delivery_address.SetValue(delivery_data.address)
            self.textbox_delivery_telephone.SetValue(delivery_data.telephone)
            self.textbox_delivery_city.SetValue(delivery_data.city)
            self.textbox_delivery_date.SetValue(core.format_date_user(delivery_data.date)[:5])
            self.textbox_delivery_hour.SetValue(delivery_data.hour)

        else:
            self.setup_delivery(None)

        # Adiciona os dados dos produtos comprados
        for i in range(len(self.data.products_IDs)):
            product_id = self.data.products_IDs[i]
            description = self.database_inventory.inventory_search_id(product_id).description
            amount = core.format_amount_user(self.data.amounts[i])
            price = core.format_cash_user(self.data.prices[i], currency=True)
            unit_price = core.format_cash_user(self.data.prices[i] / self.data.amounts[i], currency=True)
            item = self.list_sold.Append((description, amount, unit_price, price))
            self.list_sold.SetItemData(item, product_id)

        # Adiciona os dados finais da venda
        self.textbox_sale_taxes.SetValue(core.format_cash_user(self.data.taxes))
        self.textbox_sale_discount.SetValue(core.format_cash_user(self.data.discount))

        payment_options = {
            u'Dinheiro': self.radio_payment_money,
            u'Cartão de Crédito': self.radio_payment_credit_card,
            u'Cartão de Débito': self.radio_payment_debit_card,
            u'Cheque': self.radio_payment_check,
            u'Pendente': self.radio_payment_pendant
        }
        try:
            payment_options[self.data.payment].SetValue(True)
        except KeyError:
            self.radio_payment_other.SetValue(True)
            self.textbox_payment_other.Enable()
            self.textbox_payment_other.SetValue(self.data.payment)

        # realiza as contas para obter os dados restantes
        self.update_sale_data(None)

    def setup_delivery(self, event):
        self.delivery_enabled = self.delivery.GetValue()
        if self.delivery.GetValue():
            self.textbox_client_name.Enable()
            self.textbox_delivery_receiver.Enable()
            self.textbox_delivery_address.Enable()
            self.textbox_delivery_telephone.Enable()
            self.textbox_delivery_city.Enable()
            self.textbox_delivery_date.Enable()
            self.textbox_delivery_hour.Enable()
            self.textbox_delivery_city.SetValue(u"Itatiba")
            a = str(datetime.now().month)
            if len(a) == 1:
                a = '0' + a
            self.textbox_delivery_date.SetValue(core.good_show("date", ("%s/%s" % (datetime.now().day, a))))
            self.textbox_delivery_hour.SetValue('00:00')

        else:
            self.textbox_client_name.Disable()
            self.textbox_delivery_receiver.Disable()
            self.textbox_delivery_address.Disable()
            self.textbox_delivery_telephone.Disable()
            self.textbox_delivery_city.Disable()
            self.textbox_delivery_date.Disable()
            self.textbox_delivery_hour.Disable()

    def open_client_manager(self, event):
        clients.ClientManager(self, client_selection_mode=True)

    def open_client_register(self, event):
        clients.ClientRegister(self)

    def open_product_register(self, event):
        inventory.ProductData(self)

    def open_sale_edit(self, event):
        Sale(self.GetParent(), key=self.key, data=self.data, delivery_id=self.delivery_id)
        self.exit(None)

    def clean_client(self, event):
        self.textbox_client_name.Clear()
        self.textbox_client_cpf.Clear()

    def data_insert(self, event):
        _product_id = self.textbox_product_id.GetValue()
        if not _product_id:
            return dialogs.launch_error(self, u'Eh necessário especificar o ID do produto!')

        product_id = int(_product_id)
        product = self.database_inventory.inventory_search_id(product_id)
        if not product:
            return dialogs.launch_error(self, u'ID inválido!')

        _amount = self.textbox_product_amount.GetValue()
        try:
            amount = core.amount2float(_amount)
        except ValueError:
            self.textbox_product_amount.Clear()
            return dialogs.launch_error(self, u'Quantidade inválida!')

        _price = float(amount) * float(product.price)
        unit_price = core.format_cash_user(product.price, currency=True)
        price = core.format_cash_user(_price, currency=True)
        unit = self.textbox_product_unit.GetValue()

        item = self.list_sold.Append((product.description, core.format_amount_user(amount, unit=unit),
                                      unit_price, price))
        self.list_sold.SetItemData(item, product_id)

        self.textbox_product_unit.Clear()
        self.textbox_product_amount.Clear()
        self.textbox_product_id.Clear()
        self.textbox_product_description.Clear()
        self.textbox_product_price.SetValue(u"0,00")
        self.update_sale_data(None)

    def data_delete(self, event):
        if self.list_sold.GetFocusedItem() == -1:
            return
        self.list_sold.DeleteItem(self.list_sold.GetFocusedItem())
        self.update_sale_data(None)

    def data_editor_enable(self, event):
        self.item = self.list_sold.GetFocusedItem()
        if not self.item == -1:
            amount, unit = self.list_sold.GetItemText(self.item, 1).split()
            self.textbox_product_description.SetValue(self.list_sold.GetItemText(self.item, 0))
            self.textbox_product_id.SetValue(str(self.list_sold.GetItemData(self.item)))
            self.textbox_product_price.SetValue(self.list_sold.GetItemText(self.item, 2))
            self.textbox_product_amount.SetValue(amount)
            self.textbox_product_unit.SetValue(unit)
            self.__panel_product.Destroy()
            self.__panel_product = wx.Panel(self.panel_product_data, size=(200, 40), pos=(200, 225),
                                            style=wx.SIMPLE_BORDER)
            eplus = GenBitmapTextButton(self.__panel_product, 220,
                                        wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                        u"Salvar", pos=(0, 0), size=(100, 40))
            eplus.Bind(wx.EVT_BUTTON, self.data_edit)
            eremov = GenBitmapTextButton(self.__panel_product, 222,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Cancel.png', wx.BITMAP_TYPE_PNG),
                                         u'Cancelar', pos=(100, 0), size=(100, 40))
            eremov.Bind(wx.EVT_BUTTON, self.data_editor_disable)

    def data_edit(self, event):
        _product_id = self.textbox_product_id.GetValue()
        if not _product_id:
            return dialogs.launch_error(self, u'Eh necessário especificar o ID do produto!')

        product_id = int(_product_id)
        product = self.database_inventory.inventory_search_id(product_id)
        if not product:
            return dialogs.launch_error(self, u'ID inválido!')

        _amount = self.textbox_product_amount.GetValue()
        try:
            amount = core.amount2float(_amount)
        except ValueError:
            self.textbox_product_amount.Clear()
            return dialogs.launch_error(self, u'Quantidade inválida!')

        _price = float(amount) * float(product.price)
        unit_price = core.format_cash_user(product.price, currency=True)
        price = core.format_cash_user(_price, currency=True)

        unit = self.textbox_product_unit.GetValue()

        self.list_sold.SetStringItem(self.item, 0, product.description)
        self.list_sold.SetStringItem(self.item, 1, core.format_amount_user(amount, unit))
        self.list_sold.SetStringItem(self.item, 2, unit_price)
        self.list_sold.SetStringItem(self.item, 3, price)

        self.list_sold.SetItemData(self.item, product_id)

        self.update_sale_data(None)
        self.data_editor_disable(event)

    def data_editor_disable(self, event):
        self.textbox_product_unit.Clear()
        self.textbox_product_amount.Clear()
        self.textbox_product_price.SetValue(u'0,00')
        self.textbox_product_id.Clear()
        self.textbox_product_description.Clear()
        self.__panel_product.Destroy()
        self.__panel_product = wx.Panel(self.panel_product_data, size=(300, 40), pos=(100, 225), style=wx.SIMPLE_BORDER)
        button_add_product = GenBitmapTextButton(self.__panel_product, 220,
                                                 wx.Bitmap(core.directory_paths['icons'] + 'Add.png',
                                                           wx.BITMAP_TYPE_PNG),
                                                 u"Adicionar", pos=(0, 0), size=(100, 40))
        button_add_product.Bind(wx.EVT_BUTTON, self.data_insert, id=220)
        button_product_editor = GenBitmapTextButton(self.__panel_product, 221,
                                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png',
                                                              wx.BITMAP_TYPE_PNG),
                                                    u'Editar', pos=(100, 0), size=(100, 40))
        button_product_editor.Bind(wx.EVT_BUTTON, self.data_editor_enable, id=221)
        button_remove_product = GenBitmapTextButton(self.__panel_product, 222,
                                                    wx.Bitmap(core.directory_paths['icons'] + 'Trash.png',
                                                              wx.BITMAP_TYPE_PNG),
                                                    u'Apagar', pos=(200, 0), size=(100, 40))
        button_remove_product.Bind(wx.EVT_BUTTON, self.data_delete, id=222)

    def exit(self, event):
        self.database_inventory.close()
        self.Close()

    def database_search(self, event):
        self.list_inventory.DeleteAllItems()
        product_list = self.database_inventory.inventory_search_description(self.textbox_product_description.GetValue())
        for product in product_list:
            category = self.database_inventory.categories_search_id(product.category_ID)
            item = self.list_inventory.Append((product.description,
                                               core.format_amount_user(product.amount, category.unit),
                                               core.format_cash_user(product.price, currency=True)))
            self.list_inventory.SetItemData(item, product.ID)

    def database_select(self, event):
        j = self.list_inventory.GetFocusedItem()
        unit = self.list_inventory.GetItemText(j, 1).split()[-1]
        self.textbox_product_price.SetValue(self.list_inventory.GetItemText(j, 2))
        self.textbox_product_id.SetValue(str(self.list_inventory.GetItemData(j)))
        self.textbox_product_description.SetValue(self.list_inventory.GetItemText(j, 0))
        self.textbox_product_unit.SetValue(unit)
        self.textbox_product_amount.SetFocus()

    def update_sale_data(self, event):
        total_price = float(0)
        w = self.list_sold.GetItemCount()
        for i in range(0, w):
            amount = core.amount2float(self.list_sold.GetItemText(i, 1))
            price = core.money2float(self.list_sold.GetItemText(i, 2))
            total_price += amount * price
        discount = self.textbox_sale_discount.GetValue()
        if discount == "":
            discount = float(0)
        else:
            discount = core.money2float(discount)
        additional_taxes = self.textbox_sale_taxes.GetValue()
        if additional_taxes == "":
            additional_taxes = float(0)
        else:
            additional_taxes = core.money2float(additional_taxes)
        final_value = max(total_price + additional_taxes - discount, 0.0)
        self.textbox_sale_products_price.SetValue(core.format_cash_user(total_price))
        self.textbox_sale_value.SetValue(core.format_cash_user(final_value))

    def update_payment_method(self, event):
        if self.radio_payment_other.GetValue():
            self.textbox_payment_other.Enable()
        else:
            self.textbox_payment_other.Clear()
            self.textbox_payment_other.Disable()

    def ask_clean(self, event):
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        if self.list_sold.GetItemCount() == 0 and not self.delivery.GetValue():
            self.exit(None)
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        dialogs.Ask(self, u"Finalizar Venda", 11)

    def clean(self):
        self.list_sold.DeleteAllItems()
        self.data_editor_disable(None)
        self.textbox_sale_discount.Clear()
        self.textbox_sale_taxes.Clear()
        self.textbox_client_cpf.Clear()
        self.textbox_client_name.Clear()
        self.textbox_client_id.Clear()
        self.textbox_sale_taxes.SetValue("0,00")
        self.textbox_sale_discount.SetValue("0,00")
        self.delivery.SetValue(False)
        self.setup_delivery(None)
        self.radio_payment_money.SetValue(True)
        self.update_payment_method(None)
        self.update_sale_data(None)
        self.database_search(None)

    def end(self):
        w = self.list_sold.GetItemCount()
        if w == 0:
            return dialogs.launch_error(self, u'Você não adicionou nenhum produto!')

        products_id = []
        products_amounts = []
        products_unitary_prices = []

        # Armazena os dados dos produtos em vetores
        for i in range(w):
            products_id.append(self.list_sold.GetItemData(i))
            products_amounts.append(core.amount2float(self.list_sold.GetItem(i, 1).GetText()))
            aux = core.money2float(self.list_sold.GetItem(i, 3).GetText())
            products_unitary_prices.append(aux)

        self.update_sale_data(None)

        total_price = core.money2float(self.textbox_sale_value.GetValue())
        final_value = core.money2float(self.textbox_sale_value.GetValue())

        additional_taxes = core.money2float(self.textbox_sale_taxes.GetValue())
        discount = core.money2float(self.textbox_sale_discount.GetValue())

        payment_pendant = False

        if self.radio_payment_money.GetValue():
            payment_method = u'Dinheiro'
        elif self.radio_payment_credit_card.GetValue():
            payment_method = u'Cartão de Crédito'
        elif self.radio_payment_debit_card.GetValue():
            payment_method = u'Cartão de Débito'
        elif self.radio_payment_check.GetValue():
            payment_method = u'Cheque'
        elif self.radio_payment_pendant.GetValue():
            payment_method = u'Pendente'
            payment_pendant = True
        else:
            payment_method = self.textbox_payment_other.GetValue()

        if not payment_method:
            return dialogs.launch_error(self, u'Forma de pagamento inválida!')

        client_name = self.textbox_client_name.GetValue()
        client_cpf = self.textbox_client_cpf.GetValue().replace('.', '').replace('-', '')
        client_id_str = self.textbox_client_id.GetValue()
        client_id = 0
        if client_id_str:
            try:
                client_id = int(client_id_str)
                db = database.ClientsDB()
                client = db.clients_search_id(client_id)
                db.close()
                if not client:
                    raise ValueError
            except ValueError:
                return dialogs.launch_error(self, u'ID de cliente inválido')
            if not client_cpf:
                client_cpf = client.cpf
            if not client_name:
                client_name = client.name
        if payment_pendant and not client_id:
            return dialogs.launch_error(self, u'É necessário um cliente cadastrado para registrar pagamento pendente!')

        delivery_receiver_name = self.textbox_delivery_receiver.GetValue()
        delivery_address = self.textbox_delivery_address.GetValue()
        delivery_city = self.textbox_delivery_city.GetValue()
        client_telephone = self.textbox_delivery_telephone.GetValue()
        delivery_date = self.textbox_delivery_date.GetValue() + u'/' + str(datetime.now().year)
        delivery_hour = self.textbox_delivery_hour.GetValue()

        delivery_date = core.format_date_internal(delivery_date)
        if self.delivery_enabled:
            for r in (delivery_receiver_name, delivery_address, delivery_city,
                      client_telephone, delivery_date, delivery_hour):

                if len(r) == 0 or r == u'00:00' or r == u'__/__':
                    return dialogs.launch_error(self, u'Dados insulficientes para registro de entrega!')

        if client_cpf:
            try:
                int(client_cpf)
                if len(client_cpf) != 11:
                    raise ValueError
            except ValueError:
                return dialogs.launch_error(self, u'CPF do cliente inválido')

        date, finish_time = core.datetime_today()

        new_sale = data_types.SaleData()

        new_sale.record_time = finish_time
        new_sale.record_date = date
        new_sale.products_IDs = products_id
        new_sale.amounts = products_amounts
        new_sale.prices = products_unitary_prices
        new_sale.sold = total_price
        new_sale.discount = discount
        new_sale.taxes = additional_taxes
        new_sale.value = final_value
        new_sale.payment = payment_method
        new_sale.payment_pendant = payment_pendant
        new_sale.client_cpf = client_cpf if client_cpf else None
        new_sale.client_id = client_id if client_id else None

        new_sale.ID = self.key

        # Envia venda ao SAT
        sat.enviar_venda_ao_sat(new_sale)

        db = database.TransactionsDB()

        if self.key == -1:
            db.insert_sale(new_sale)
        else:
            db.edit_sale(new_sale)

        db.close()

        deliveries_db = database.DeliveriesDB()

        if self.key == -1:
            delivery = deliveries_db.deliveries_search_sale(new_sale.ID)
            if delivery:
                deliveries_db.delete_delivery_permanently(delivery.ID)

        if self.delivery_enabled:

            if core.date2int(date) < core.date2int(delivery_date):
                delivery_date = delivery_date[:-1] + str(int(delivery_date[-1:]) + 1)

            new_delivery = data_types.DeliveryData()
            new_delivery.client = client_name
            new_delivery.telephone = client_telephone
            new_delivery.address = delivery_address
            new_delivery.city = delivery_city
            new_delivery.date = delivery_date
            new_delivery.hour = delivery_hour
            new_delivery.receiver = delivery_receiver_name
            new_delivery.sale_ID = new_sale.ID

            deliveries_db.insert_delivery(new_delivery)

        deliveries_db.close()

        # Atualiza os dados da venda no estoque
        if self.data:
            update_inventory(self.data, True)
        update_inventory(new_sale)

        if self.data:
            if self.data.client_id:
                clients.disconnect_sale(self.data.ID)
        if client_id:
            clients.connect_sale(new_sale.ID, new_sale.client_id, new_sale.record_date)

        self.clean()
        if self.key == -1:
            dialogs.Confirmation(self, u"Sucesso", 1)
        else:
            if type(self.GetParent()) is daily_report.Report:
                self.GetParent().setup(None)
            self.exit(None)


class SaleManager(wx.Frame):

    list_sales = None

    def __init__(self, parent, title=u'Pagamentos Pendentes'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(100, 100))
        self.SetSize(wx.Size(810, 550))
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        panel_top = wx.Panel(self, pos=(10, 10), size=(790, 100))

        button_client = GenBitmapTextButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'user-info.png',
                                            wx.BITMAP_TYPE_PNG), u'Cliente', pos=(5, 40), size=(100, 40),
                                            style=wx.SIMPLE_BORDER)
        button_client.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        button_client.Bind(wx.EVT_BUTTON, self.data_open_client)

        panel_buttons_left = wx.Panel(panel_top, pos=(130, 40), size=(420, 40), style=wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Search.png', wx.BITMAP_TYPE_PNG),
                                  u'Ver Mais', pos=(0, 0), size=(100, 40))
        see.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        see.Bind(wx.EVT_BUTTON, self.data_open)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Sale.png', wx.BITMAP_TYPE_PNG),
                                   u'Nova Venda', pos=(100, 0), size=(120, 40))
        plus.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        plus.Bind(wx.EVT_BUTTON, self.open_new_sale)

        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(220, 0), size=(100, 40))
        edi.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(320, 0), size=(100, 40))
        era.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)

        panel_buttons_right = wx.Panel(panel_top, pos=(575, 40), size=(200, 40), style=wx.SIMPLE_BORDER)
        quir = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                   u'Sair',
                                   pos=(100, 0), size=(100, 40))
        quir.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        quir.Bind(wx.EVT_BUTTON, self.exit)
        rep = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                  u'Atualizar',
                                  pos=(0, 0), size=(100, 40))
        rep.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        rep.Bind(wx.EVT_BUTTON, self.setup)
        panel_center = wx.Panel(self, -1, pos=(10, 110), size=(820, 410))

        self.list_sales = wx.ListCtrl(panel_center, -1, pos=(5, 5), size=(770, 390),
                                      style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)

        self.list_sales.InsertColumn(0, u'ID', width=100)
        self.list_sales.InsertColumn(1, u'Data', width=100)
        self.list_sales.InsertColumn(2, u'Horário', width=100)
        self.list_sales.InsertColumn(3, u'Cliente', width=315)
        self.list_sales.InsertColumn(4, u'Valor', width=150)

        self.list_sales.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_open)

    def setup(self, event):     # FIXME Fazer a thread fechar direito com o resto do app
        import threading
        rest = threading.Thread(target=self.__setup__)
        rest.daemon = True
        rest.start()

    def __setup__(self):
        self.list_sales.DeleteAllItems()
        sales_db = database.TransactionsDB()
        sales = sales_db.sales_list_pendant()
        sales_db.close()

        clients_db = database.ClientsDB()

        for sale_ in sales:

            client = clients_db.clients_search_id(sale_.client_id)

            info = (core.format_id_user(sale_.ID), core.format_date_user(sale_.record_date),
                    sale_.record_time, client.name, core.format_cash_user(sale_.value, currency=True))

            item = self.list_sales.Append(info)
            self.list_sales.SetItemData(item, client.ID)

        clients_db.close()

    def data_delete(self, event):
        it = self.list_sales.GetFocusedItem()
        if it == -1:
            return
        e_id = self.list_sales.GetItem(it, 0).GetText()
        db = database.TransactionsDB()
        db.delete_sale(int(e_id))
        db.close()
        self.setup(None)

    def data_edit(self, event):
        po = self.list_sales.GetFocusedItem()
        if po == -1:
            return
        sale_id = self.list_sales.GetItem(po, 0).GetText()
        Sale(self, key=int(sale_id))

    def data_open(self, event):
        po = self.list_sales.GetFocusedItem()
        if po == -1:
            return
        sale_id = self.list_sales.GetItem(po, 0).GetText()
        Sale(self, key=int(sale_id), editable=False)

    def data_open_client(self, event):
        po = self.list_sales.GetFocusedItem()
        if po == -1:
            return
        client_id = self.list_sales.GetItemData(po)
        name = self.list_sales.GetItem(po, 3).GetText()

        clients.ClientData(self, title=name, client_id=client_id, editable=False)

    def ask_delete(self, event):
        dialogs.Ask(self, u'Apagar Venda', 28)

    def open_new_sale(self, event):
        Sale(self)

    def exit(self, event):
        self.Close()

