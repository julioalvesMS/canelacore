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
    radio_payment_other = None
    textbox_payment_other = None

    textbox_product_description = None
    textbox_product_id = None
    textbox_product_price = None
    textbox_product_amount = None

    textbox_sale_discount = None
    textbox_sale_taxes = None
    textbox_sale_products_price = None
    textbox_sale_value = None

    textbox_client_name = None
    textbox_client_cpf = None

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
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))

        self.SetBackgroundColour(core.default_background_color)

        # result
        result = wx.Panel(self, -1, pos=(5, 5), size=(450, 605), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        result.SetBackgroundColour(core.default_background_color)

        self.list_sold = wx.ListCtrl(result, -1, pos=(10, 10), size=(430, 400),
                                     style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.list_sold.InsertColumn(1, u"Descrição", width=180)
        self.list_sold.InsertColumn(2, u"Quantidade")
        self.list_sold.InsertColumn(3, u"Preço Unit.")
        self.list_sold.InsertColumn(4, u"Preço")

        wx.StaticText(result, -1, u"Forma de Pagamento:", (10, 420))
        self.radio_payment_money = wx.RadioButton(result, -1, u"Dinheiro", (15, 440))
        self.radio_payment_credit_card = wx.RadioButton(result, -1, u"Cartão de Crédito", (15, 470))
        self.radio_payment_debit_card = wx.RadioButton(result, -1, u"Cartão de Débito", (15, 500))
        self.radio_payment_check = wx.RadioButton(result, -1, u"Cheque", (15, 530))
        self.radio_payment_other = wx.RadioButton(result, -1, u"Outra", (15, 560))
        self.textbox_payment_other = wx.TextCtrl(result, -1, pos=(80, 560), size=(120, 25))
        self.textbox_payment_other.Disable()
        self.update_payment_method(None)
        self.radio_payment_money.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_credit_card.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_debit_card.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_check.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_other.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
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
            self.radio_payment_other.Disable()

        # product
        self.panel_product_data = wx.Panel(self, 22, pos=(460, 5), size=(450, 275),
                                           style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.panel_product_data.SetBackgroundColour(core.default_background_color)
        wx.StaticText(self.panel_product_data, -1, u"Adicionar Produto", pos=(160, 8)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        fin = wx.BitmapButton(self.panel_product_data, -1, wx.Bitmap(core.directory_paths['icons'] + 'Add.png'),
                              pos=(408, 25), size=(32, 32), style=wx.NO_BORDER)
        fin.SetBackgroundColour(core.default_background_color)
        fin.Bind(wx.EVT_BUTTON, self.open_product_register)

        self.textbox_product_description = wx.SearchCtrl(self.panel_product_data, 223, pos=(10, 25), size=(395, 32))
        self.textbox_product_description.Bind(wx.EVT_TEXT, self.database_search, id=223)
        self.textbox_product_description.ShowSearchButton(False)
        self.textbox_product_description.SetDescriptiveText(u'Descrição do produto')
        self.list_inventory = wx.ListCtrl(self.panel_product_data, -1, pos=(10, 60), size=(430, 115),
                                          style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.list_inventory.InsertColumn(0, u'ID')
        self.list_inventory.InsertColumn(1, u'Descrição', width=230)
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
        client = wx.Panel(self, 23, pos=(460, 285), size=(450, 325), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        client.SetBackgroundColour(core.default_background_color)
        wx.StaticText(client, -1, u"Nome do cliente: ", pos=(25, 5))
        wx.StaticText(client, -1, u"CPF: ", pos=(325, 5))
        self.textbox_client_name = wx.TextCtrl(client, -1, pos=(25, 25), size=(250, 25))
        self.textbox_client_cpf = wx.TextCtrl(client, -1, pos=(325, 25), size=(100, 25))
        self.textbox_client_cpf.Bind(wx.EVT_CHAR, core.check_cpf)
        self.textbox_client_cpf.SetMaxLength(6)
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
        wx.StaticText(client, -1, u"Data:", pos=(10, 287))
        wx.StaticText(client, -1, u"Horário:", pos=(150, 287))
        self.textbox_delivery_receiver = wx.TextCtrl(client, -1, pos=(10, 150), size=(350, 25))
        self.textbox_delivery_address = wx.TextCtrl(client, -1, pos=(10, 200), size=(350, 25))
        self.textbox_delivery_telephone = wx.TextCtrl(client, -1, pos=(80, 240), size=(120, 25))
        self.textbox_delivery_city = wx.TextCtrl(client, -1, pos=(260, 240), size=(100, 25))
        self.textbox_delivery_date = wx.TextCtrl(client, -1, pos=(50, 280), size=(60, 25))
        self.textbox_delivery_hour = wx.TextCtrl(client, -1, pos=(200, 280), size=(60, 25))

        self.textbox_delivery_telephone.Bind(wx.EVT_CHAR, core.check_telephone)
        self.textbox_delivery_date.Bind(wx.EVT_CHAR, core.check_date_simple)
        self.textbox_delivery_hour.Bind(wx.EVT_CHAR, core.check_hour)

        self.textbox_delivery_receiver.Disable()
        self.textbox_delivery_address.Disable()
        self.textbox_delivery_telephone.Disable()
        self.textbox_delivery_city.Disable()
        self.textbox_delivery_date.Disable()
        self.textbox_delivery_hour.Disable()
        if not self.editable:
            self.textbox_client_name.Disable()
            self.textbox_client_cpf.Disable()
            self.delivery.Disable()
            cold.Disable()
            cnew.Disable()
            cno.Disable()

        # last
        last = wx.Panel(self, 24, pos=(5, 615), size=(905, 50), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        last.SetBackgroundColour(core.default_background_color)
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
            cancel = GenBitmapTextButton(last_, 242,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(0, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.exit)
            edit = GenBitmapTextButton(last_, 243,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                       u"Editar",
                                       pos=(100, 0), size=(100, 40))
            edit.Bind(wx.EVT_BUTTON, self.open_sale_edit)

    def setup(self):

        if self.key == -1:
            return

        if not self.data:
            db = database.TransactionsDB()
            self.data = db.sales_search_id(self.key)
            db.close()

        # Adiciona os dados do cliente
        self.textbox_client_cpf.SetValue(core.format_cpf(self.data.client_cpf))

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
            amount = self.data.amounts[i]
            unit_price = "R$ " + core.good_show("money", self.data.prices[i])
            price = self.data.amounts[i] * self.data.prices[i]
            item = self.list_sold.Append((description, amount, unit_price, price))
            self.list_sold.SetItemData(item, product_id)

        # Adiciona os dados finais da venda
        self.textbox_sale_taxes.SetValue(core.good_show("money", self.data.taxes))
        self.textbox_sale_discount.SetValue(core.good_show("money", self.data.discount))

        payment_options = {
            u'Dinheiro': self.radio_payment_money,
            u'Cartão de Crédito': self.radio_payment_credit_card,
            u'Cartão de Débito': self.radio_payment_debit_card,
            u'Cheque': self.radio_payment_check
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
        inventory.ProductRegister(self)

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

        _amount = self.textbox_product_amount.GetValue().replace(',', '.')
        try:
            amount = float(_amount)
        except ValueError:
            self.textbox_product_amount.Clear()
            return dialogs.launch_error(self, u'Quantidade inválida!')

        _price = float(amount) * float(product.price)
        unit_price = "R$ " + core.good_show('money', product.price)
        price = "R$ " + core.good_show('money', _price)
        item = self.list_sold.Append((product.description, str(amount).replace('.', ','), unit_price, price))
        self.list_sold.SetItemData(item, product_id)

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
            self.textbox_product_description.SetValue(self.list_sold.GetItemText(self.item, 0))
            self.textbox_product_id.SetValue(str(self.list_sold.GetItemData(self.item)))
            self.textbox_product_price.SetValue(self.list_sold.GetItemText(self.item, 2))
            self.textbox_product_amount.SetValue(self.list_sold.GetItemText(self.item, 1))
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
        product_id = int(self.textbox_product_id.GetValue())
        product = self.database_inventory.inventory_search_id(product_id)
        if not product:
            return dialogs.launch_error(self, u'Dados Insulficientes!')

        amount = self.textbox_product_amount.GetValue()
        _price = float(amount) * float(product.price)
        unit_price = "R$ " + core.good_show('money', product.price)
        price = "R$ " + core.good_show('money', _price)

        self.list_sold.SetStringItem(self.item, 0, product.description)
        self.list_sold.SetStringItem(self.item, 1, amount)
        self.list_sold.SetStringItem(self.item, 2, unit_price)
        self.list_sold.SetStringItem(self.item, 3, price)

        self.list_sold.SetItemData(self.item, product_id)

        self.update_sale_data(None)
        self.data_editor_disable(event)

    def data_editor_disable(self, event):
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
            self.list_inventory.Append((product.ID, product.description,
                                        'R$ ' + core.good_show('money', product.price)))

    def database_select(self, event):
        j = self.list_inventory.GetFocusedItem()
        self.textbox_product_price.SetValue(self.list_inventory.GetItemText(j, 2))
        self.textbox_product_id.SetValue(self.list_inventory.GetItemText(j, 0))
        self.textbox_product_description.SetValue(self.list_inventory.GetItemText(j, 1))
        self.textbox_product_amount.SetFocus()

    def update_sale_data(self, event):
        total_price = float(0)
        w = self.list_sold.GetItemCount()
        for i in range(0, w):
            product_price = self.list_sold.GetItem(i, 3).GetText()
            a = product_price.replace(",", ".").replace("R$ ", "")
            total_price += float(a)
        discount = self.textbox_sale_discount.GetValue().replace(",", ".")
        if discount == "":
            discount = float(0)
        else:
            discount = float(discount)
        additional_taxes = self.textbox_sale_taxes.GetValue().replace(",", ".")
        if additional_taxes == "":
            additional_taxes = float(0)
        else:
            additional_taxes = float(additional_taxes)
        final_value = max(float(total_price + additional_taxes - discount), 0.0)
        self.textbox_sale_products_price.SetValue(core.good_show("money", str(total_price).replace(".", ",")))
        self.textbox_sale_value.SetValue(core.good_show("money", str(final_value).replace(".", ",")))

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
        self.textbox_product_amount.Clear()
        self.textbox_product_price.Clear()
        self.textbox_sale_discount.Clear()
        self.textbox_sale_taxes.Clear()
        self.textbox_product_description.Clear()
        self.textbox_sale_taxes.SetValue("0,00")
        self.textbox_sale_discount.SetValue("0,00")
        self.textbox_product_price.SetValue("0,00")
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
            products_amounts.append(float(self.list_sold.GetItem(i, 1).GetText().replace(',', '.')))
            aux = float(self.list_sold.GetItem(i, 3).GetText().replace(",", ".").replace("R$ ", ""))
            products_unitary_prices.append(aux)

        self.update_sale_data(None)

        total_price = float(self.textbox_sale_value.GetValue().replace(",", "."))
        final_value = float(self.textbox_sale_value.GetValue().replace(",", "."))

        additional_taxes = float(self.textbox_sale_taxes.GetValue().replace(",", "."))
        discount = float(self.textbox_sale_discount.GetValue().replace(",", "."))

        if self.radio_payment_money.GetValue():
            payment_method = u'Dinheiro'
        elif self.radio_payment_credit_card.GetValue():
            payment_method = u'Cartão de Crédito'
        elif self.radio_payment_debit_card.GetValue():
            payment_method = u'Cartão de Débito'
        elif self.radio_payment_check.GetValue():
            payment_method = u'Cheque'
        else:
            payment_method = self.textbox_payment_other.GetValue()

        client_name = self.textbox_client_name.GetValue()
        client_cpf = self.textbox_client_cpf.GetValue().replace('.', '').replace('-', '')

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
        new_sale.client_name = client_name
        new_sale.client_cpf = client_cpf

        new_sale.ID = self.key

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
                deliveries_db.delete_delivery(delivery.ID)

        if self.delivery_enabled:

            delivery_receiver_name = self.textbox_delivery_receiver.GetValue()
            delivery_address = self.textbox_delivery_address.GetValue()
            delivery_city = self.textbox_delivery_city.GetValue()
            client_telephone = self.textbox_delivery_telephone.GetValue()
            delivery_date = self.textbox_delivery_date.GetValue() + u'/' + str(datetime.now().year)
            delivery_hour = self.textbox_delivery_hour.GetValue()

            delivery_date = core.format_date_internal(delivery_date)

            for r in (delivery_receiver_name, delivery_address, delivery_city,
                      client_telephone, delivery_date, delivery_hour):

                if len(r) == 0 or r == u'00:00' or r == u'__/__':
                    return dialogs.launch_error(self, u'Dados insulficientes para registro de entrega!')

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

        self.clean()
        if self.key == -1:
            dialogs.Confirmation(self, u"Sucesso", 1)
        else:
            if type(self.GetParent()) is daily_report.Report:
                self.GetParent().setup(None)
            self.Close()
