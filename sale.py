#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import shutil
from datetime import datetime
from string import lower

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import clients
import core
import daily_report
import dialogs

__author__ = 'Julio'


class Sale(wx.Frame):
    item = None
    delivery_enabled = False
    database_inventory = None
    database_filtered_inventory = None

    delivery = None

    radio_payment_card = None
    radio_payment_money = None
    radio_payment_other = None
    textbox_payment_other = None

    textbox_product_description = None
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

    def __init__(self, parent, title=u'Vendas', argv=None, editable=True):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        if not argv:
            argv = []

        self.argv = argv
        self.editable = editable

        self.setup_gui()
        self.setup()
        self.setup_delivery(None)

        self.update_sale_data()
        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(200, 25))
        self.SetSize(wx.Size(925, 700))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))

        self.SetBackgroundColour(core.default_background_color)
        # result
        result = wx.Panel(self, 21, pos=(5, 5), size=(450, 605), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        result.SetBackgroundColour(core.default_background_color)
        self.list_sold = wx.ListCtrl(result, 210, pos=(10, 10), size=(430, 400),
                                     style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.list_sold.InsertColumn(2100, u"Descrição", width=180)
        self.list_sold.InsertColumn(2101, u"Quantidade")
        self.list_sold.InsertColumn(2102, u"Preço Unit.")
        self.list_sold.InsertColumn(2103, u"Preço")
        wx.StaticText(result, -1, u"Total:  R$", (312, 417))
        self.textbox_sale_products_price = wx.TextCtrl(result, -1, '0,00', (370, 410), size=(60, 30),
                                                       style=wx.TE_READONLY)
        self.textbox_sale_products_price.SetBackgroundColour("#C0C0C0")
        self.textbox_sale_products_price.Refresh()
        wx.StaticText(result, -1, u"Forma de Pagamento:", (10, 420))
        self.radio_payment_money = wx.RadioButton(result, 211, u"Dinheiro", (15, 440))
        self.radio_payment_card = wx.RadioButton(result, 211, u"Cartão", (15, 470))
        self.radio_payment_other = wx.RadioButton(result, 211, u"Outra", (15, 500))
        self.textbox_payment_other = wx.TextCtrl(result, -1, pos=(80, 500), size=(120, 30))
        self.textbox_payment_other.SetBackgroundColour("#C0C0C0")
        self.textbox_payment_other.Refresh()
        self.update_payment_method(1)
        self.radio_payment_money.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_card.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_other.Bind(wx.EVT_RADIOBUTTON, self.update_payment_method)
        self.radio_payment_money.SetValue(True)
        wx.StaticText(result, -1, u"Desconto:  R$", (285, 450))
        self.textbox_sale_discount = wx.TextCtrl(result, 212, pos=(370, 443), size=(60, 30))
        self.textbox_sale_discount.SetValue(u"0,00")
        self.textbox_sale_discount.Bind(wx.EVT_CHAR, core.check_money)
        wx.StaticText(result, -1, u"Taxas:  R$", (310, 483))
        self.textbox_sale_taxes = wx.TextCtrl(result, 42, '0,00', (370, 476), size=(60, 30))
        self.textbox_sale_taxes.Bind(wx.EVT_CHAR, core.check_money, id=42)
        wx.StaticText(result, -1, u"Total da Venda:  R$", (255, 530))
        self.textbox_sale_value = wx.TextCtrl(result, 214, '0,00', (370, 523), size=(60, 30), style=wx.TE_READONLY)
        self.textbox_sale_value.SetBackgroundColour("#C0C0C0")
        self.textbox_sale_value.Refresh()
        wx.StaticLine(result, -1, (285, 515), (150, 1))
        if not self.editable:
            self.textbox_sale_taxes.SetBackgroundColour(core.default_disabled_color)
            self.textbox_sale_taxes.Disable()
            self.textbox_sale_discount.SetBackgroundColour(core.default_disabled_color)
            self.textbox_sale_discount.Disable()
            self.textbox_payment_other.SetBackgroundColour(core.default_disabled_color)
            self.textbox_payment_other.Disable()
            if not self.radio_payment_money.GetValue():
                self.radio_payment_money.Disable()
            if not self.radio_payment_card.GetValue():
                self.radio_payment_card.Disable()
            if not self.radio_payment_other.GetValue():
                self.radio_payment_other.Disable()
        # product
        self.panel_product_data = wx.Panel(self, 22, pos=(460, 5), size=(450, 275),
                                           style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.panel_product_data.SetBackgroundColour(core.default_background_color)
        wx.StaticText(self.panel_product_data, -1, u"Adicionar Produto", pos=(160, 8)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.textbox_product_description = wx.SearchCtrl(self.panel_product_data, 223, pos=(10, 25), size=(430, 30))
        self.textbox_product_description.Bind(wx.EVT_TEXT, self.database_search, id=223)
        self.textbox_product_description.ShowSearchButton(False)
        self.textbox_product_description.SetDescriptiveText(u'Descrição do produto')
        self.list_inventory = wx.ListCtrl(self.panel_product_data, -1, pos=(10, 60), size=(430, 115),
                                          style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.list_inventory.InsertColumn(0, u'Descrição', width=230)
        self.list_inventory.InsertColumn(1, u'Preço')
        self.list_inventory.InsertColumn(2, u'Estoque')
        self.list_inventory.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.database_select)
        self.setup_inventory()
        wx.StaticText(self.panel_product_data, -1, u"Preço Unitário: R$", pos=(10, 192))
        self.textbox_product_price = wx.TextCtrl(self.panel_product_data, 224, pos=(120, 185), size=(60, 30))
        self.textbox_product_price.Bind(wx.EVT_CHAR, core.check_money, id=224)
        self.textbox_product_price.SetValue("0,00")
        wx.StaticText(self.panel_product_data, -1, u"Quantidade:", pos=(225, 192))
        self.textbox_product_amount = wx.TextCtrl(self.panel_product_data, 225, pos=(300, 185), size=(40, 30))
        self.textbox_product_amount.Bind(wx.EVT_CHAR, core.check_number, id=225)
        if self.editable:
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

        else:
            self.textbox_product_description.SetBackgroundColour('#C6C6C6')
            self.list_inventory.SetBackgroundColour('#C6C6C6')
            self.textbox_product_description.Disable()
            self.list_inventory.DeleteAllItems()
            self.list_inventory.Disable()
            self.textbox_product_price.Disable()
            self.textbox_product_amount.Disable()

        # client
        client = wx.Panel(self, 23, pos=(460, 285), size=(450, 325), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        client.SetBackgroundColour(core.default_background_color)
        wx.StaticText(client, -1, u"Nome do cliente: ", pos=(10, 5))
        wx.StaticText(client, -1, u"CPF: ", pos=(350, 5))
        self.textbox_client_name = wx.TextCtrl(client, -1, pos=(5, 25), size=(300, 25))
        self.textbox_client_cpf = wx.TextCtrl(client, -1, pos=(345, 25), size=(70, 25))
        self.textbox_client_cpf.Bind(wx.EVT_CHAR, core.check_cpf)
        self.textbox_client_cpf.SetMaxLength(6)
        if self.editable:
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
            cnew.Bind(wx.EVT_BUTTON, self.open_new_client)
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
        self.textbox_delivery_date.Bind(wx.EVT_CHAR, core.check_date)
        self.textbox_delivery_hour.Bind(wx.wxEVT_CHAR, core.hour_check)

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
            edit.Bind(wx.EVT_BUTTON, self.open_edit_sale)

    def setup(self):
        if not self.argv:
            return

        day_data = shelve.open(self.argv[0])

        # Adiciona os dados do cliente
        self.textbox_client_name.SetValue(day_data['sales'][self.argv[1]]['client_name'])
        self.textbox_client_cpf.SetValue(day_data['sales'][self.argv[1]]['client_id'])

        # Caso haja, adiciona os dados da entrega
        if day_data["sales"][self.argv[1]]['delivery']:
            self.delivery.SetValue(True)
            self.setup_delivery(1)
            self.textbox_delivery_receiver.SetValue(day_data["sales"][self.argv[1]]['receiver'])
            self.textbox_delivery_address.SetValue(day_data["sales"][self.argv[1]]['adress'])
            self.textbox_delivery_telephone.SetValue(str(day_data["sales"][self.argv[1]]['tel1']))
            self.textbox_delivery_city.SetValue(day_data["sales"][self.argv[1]]['city'])
            self.textbox_delivery_date.SetValue(str(day_data["sales"][self.argv[1]]['date']))
            self.textbox_delivery_hour.SetValue(str(day_data["sales"][self.argv[1]]['hour']))

        # Adiciona os dados dos produtos comprados
        for i in day_data["sales"][self.argv[1]]['descriptions']:
            ps = day_data["sales"][self.argv[1]]['descriptions'].index(i)
            kill = "R$ " + core.good_show("money",
                                          str(day_data["sales"][self.argv[1]]['unit_prices'][ps]).replace(".", ","))
            hug = "R$ " + core.good_show("money", str(day_data["sales"][self.argv[1]]['prices'][ps]).replace(".", ","))
            self.list_sold.Append((i, day_data["sales"][self.argv[1]]['amounts'][ps], kill, hug))

        # Adiciona os dados finais da venda
        self.textbox_sale_taxes.SetValue(
            core.good_show("money", str(day_data["sales"][self.argv[1]]['tax']).replace(".", ",")))
        self.textbox_sale_discount.SetValue(
            core.good_show("money", str(day_data["sales"][self.argv[1]]['discount']).replace(".", ",")))
        boot = day_data["sales"][self.argv[1]]['payment']
        if boot == u"Dinheiro":
            self.radio_payment_money.SetValue(True)
        elif boot == u"Cartão":
            self.radio_payment_card.SetValue(True)
        else:
            self.radio_payment_other.SetValue(True)
            self.textbox_payment_other.Unbind(wx.EVT_CHAR)
            self.textbox_payment_other.Bind(wx.EVT_CHAR, core.all_char)
            self.textbox_payment_other.SetBackgroundColour(wx.NullColour)
            self.textbox_payment_other.SetValue(boot)

        day_data.close()
        # realiza as contas para obter os dados restantes
        self.update_sale_data()

    def open_client_manager(self, event):
        clients.ClientManager(self, client_selection_mode=True)

    def open_new_client(self, event):
        clients.ClientRegister(self)

    def open_edit_sale(self, event):
        Sale(self.GetParent(), argv=self.argv)
        self.exit(None)

    def clean_client(self, event):
        self.textbox_client_name.Clear()
        self.textbox_client_cpf.Clear()

    def data_insert(self, event):
        if not self.textbox_product_description.GetValue() or self.textbox_product_price.GetValue() == '0,00' or not \
                self.textbox_product_amount.GetValue():
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        else:
            a = self.textbox_product_price.GetValue().replace(",", ".")
            trem = int(self.textbox_product_amount.GetValue()) * float(a)
            hug = "R$ " + core.good_show('money', str(trem))
            kill = "R$ " + core.good_show('money', str(float(a)))
            self.list_sold.Append(((self.textbox_product_description.GetValue().capitalize()),
                                   self.textbox_product_amount.GetValue(), kill, hug))
            self.textbox_product_amount.Clear()
            self.textbox_product_price.Clear()
            self.textbox_product_description.Clear()
            self.update_sale_data()
            self.textbox_product_price.SetValue("0,00")

    def data_delete(self, event):
        if self.list_sold.GetFocusedItem() == -1:
            return
        self.list_sold.DeleteItem(self.list_sold.GetFocusedItem())
        self.update_sale_data()

    def data_editor_enable(self, event):
        self.item = self.list_sold.GetFocusedItem()
        if not self.item == -1:
            self.textbox_product_description.SetValue(self.list_sold.GetItemText(self.item, 0))
            self.textbox_product_price.SetValue(self.list_sold.GetItemText(self.item, 2).replace('R$ ', ''))
            self.textbox_product_amount.SetValue(self.list_sold.GetItemText(self.item, 1))
            self.__panel_product.Destroy()
            self.__panel_product = wx.Panel(self.panel_product_data, size=(200, 40), pos=(200, 225),
                                            style=wx.SIMPLE_BORDER)
            eplus = GenBitmapTextButton(self.__panel_product, 220,
                                             wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                             u"Salvar", pos=(0, 0), size=(100, 40))
            eplus.Bind(wx.EVT_BUTTON, self.data_edit)
            eremov = GenBitmapTextButton(self.__panel_product, 222,
                                              wx.Bitmap(core.directory_paths['icons'] + 'Cancel.png',
                                                        wx.BITMAP_TYPE_PNG),
                                              u'Cancelar', pos=(100, 0), size=(100, 40))
            eremov.Bind(wx.EVT_BUTTON, self.data_editor_disable)

    def data_edit(self, event):
        if not self.textbox_product_description.GetValue() or self.textbox_product_price.GetValue() == '0,00' or not self.textbox_product_amount.GetValue() or self.list_sold.GetFocusedItem() == -1:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        else:
            trem = int(self.textbox_product_amount.GetValue()) * float(
                self.textbox_product_price.GetValue().replace(',', '.'))
            hug = "R$ " + core.good_show('money', str(trem))
            kill = "R$ " + core.good_show('money', self.textbox_product_price.GetValue().replace(',', '.'))
            self.list_sold.SetStringItem(self.item, 0, self.textbox_product_description.GetValue())
            self.list_sold.SetStringItem(self.item, 1, self.textbox_product_amount.GetValue())
            self.list_sold.SetStringItem(self.item, 2, kill)
            self.list_sold.SetStringItem(self.item, 3, hug)
            self.textbox_product_amount.Clear()
            self.textbox_product_price.Clear()
            self.textbox_product_description.Clear()
            self.update_sale_data()
            self.data_editor_disable(event)

    def data_editor_disable(self, event):
        self.textbox_product_description.Clear()
        self.textbox_product_price.SetValue('0,00')
        self.textbox_product_amount.Clear()
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
        self.Close()

    def setup_inventory(self):
        self.database_inventory = {}
        for root, dirs, files in os.walk(core.directory_paths['inventory']):
            if root is not core.directory_paths['inventory']:
                try:
                    s = shelve.open(root + core.slash + '%s_infos.txt' % (root[-6:]))
                    self.database_inventory[root[9:]] = {}
                    x = 0
                    for i in s:
                        self.database_inventory[root[9:]][i] = s[i]
                        x += 1
                    s.close()
                    if not x:
                        shutil.rmtree(root)
                        del self.database_inventory[root[9:]]
                except ValueError or KeyError:
                    pass
        self.database_search(None)

    def database_search(self, event):
        self.list_inventory.DeleteAllItems()
        product_list = []
        self.database_filtered_inventory = {}
        tex = self.textbox_product_description.GetValue()
        num = len(tex)
        for o in self.database_inventory:
            try:
                fri = []
                for a in self.database_inventory[o]['description'].split():
                    fri.append(lower((a[:num])))
                fri.append(lower((self.database_inventory[o]['description'][:num])))
                if (lower(tex) in fri) or (tex == o):
                    self.database_filtered_inventory[self.database_inventory[o]['description']] = \
                        [o, core.good_show('money', str(self.database_inventory[o]['price'])).replace('.', ','),
                         self.database_inventory[o]['amount']]
                    product_list.append(self.database_inventory[o]['description'])
            except:
                pass
        product_list.sort()
        for g in product_list:
            self.list_inventory.Append(
                (g, self.database_filtered_inventory[g][1], self.database_filtered_inventory[g][2]))

    def database_select(self, event):
        j = self.list_inventory.GetFocusedItem()
        self.textbox_product_price.SetValue(self.list_inventory.GetItem(j, 1).GetText())
        self.textbox_product_description.SetValue(self.list_inventory.GetItemText(j))
        self.textbox_product_amount.SetFocus()

    def update_sale_data(self):
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
        final_value = float(total_price + additional_taxes - discount)
        self.textbox_sale_products_price.SetValue(core.good_show("money", str(total_price).replace(".", ",")))
        self.textbox_sale_value.SetValue(core.good_show("money", str(final_value).replace(".", ",")))

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

        else:
            self.textbox_delivery_receiver.Disable()
            self.textbox_delivery_address.Disable()
            self.textbox_delivery_telephone.Disable()
            self.textbox_delivery_city.Disable()
            self.textbox_delivery_date.Disable()
            self.textbox_delivery_hour.Disable()

    def update_payment_method(self, event):
        if self.radio_payment_other.GetValue():
            self.textbox_payment_other.Unbind(wx.EVT_CHAR)
            self.textbox_payment_other.Bind(wx.EVT_CHAR, core.all_char)
            self.textbox_payment_other.SetBackgroundColour(wx.NullColour)
            self.textbox_payment_other.ClearBackground()
        else:
            self.textbox_payment_other.Unbind(wx.EVT_CHAR)
            self.textbox_payment_other.Bind(wx.EVT_CHAR, core.no_char)
            self.textbox_payment_other.Clear()
            self.textbox_payment_other.SetBackgroundColour("#C0C0C0")
            self.textbox_payment_other.ClearBackground()

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
        self.setup_delivery(False)
        self.radio_payment_money.SetValue(True)
        self.update_payment_method(None)
        self.update_sale_data()
        self.database_search(1)

    def end(self):
        w = self.list_sold.GetItemCount()
        if w == 0:
            return dialogs.launch_error(self, u'Você não adicionou nenhum produto!')

        products_descriptions = []
        products_amounts = []
        products_unitary_prices = []
        products_total_price = []

        hour = ''

        # Armazena os dados dos produtos em vetores
        for i in range(0, w):
            products_descriptions.append(self.list_sold.GetItem(i, 0).GetText())
            products_amounts.append(int(self.list_sold.GetItem(i, 1).GetText()))
            aux = float(self.list_sold.GetItem(i, 2).GetText().replace(",", ".").replace("R$ ", ""))
            products_unitary_prices.append(aux)
            aux = float(self.list_sold.GetItem(i, 3).GetText().replace(",", ".").replace("R$ ", ""))
            products_total_price.append(aux)

        self.update_sale_data()

        total_price = float(self.textbox_sale_value.GetValue().replace(",", "."))
        final_value = float(self.textbox_sale_value.GetValue().replace(",", "."))

        additional_taxes = float(self.textbox_sale_taxes.GetValue().replace(",", "."))
        discount = float(self.textbox_sale_discount.GetValue().replace(",", "."))

        payment_method = u''
        if self.radio_payment_money.GetValue():
            payment_method = u"Dinheiro"
        if self.radio_payment_card.GetValue():
            payment_method = u"Cartão"
        if self.radio_payment_other.GetValue():
            payment_method = self.textbox_payment_other.GetValue()

        client_name = self.textbox_client_name.GetValue()
        client_id = self.textbox_client_cpf.GetValue()
        while len(client_id) < 6:
            client_id = '0' + client_id
        try:
            int(client_id)
        except ValueError:
            return dialogs.launch_error(self, u'ID do cliente inválida')

        delivery_receiver_name = self.textbox_delivery_receiver.GetValue()
        delivery_address = self.textbox_delivery_address.GetValue()
        delivery_city = self.textbox_delivery_city.GetValue()
        client_telephone = self.textbox_delivery_telephone.GetValue()
        delivery_date = self.textbox_delivery_date.GetValue()
        delivery_hour = self.textbox_delivery_hour.GetValue()

        finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(
                datetime.now().day))

        if self.delivery_enabled:
            for r in delivery_receiver_name, delivery_address, delivery_city, client_telephone, delivery_date, delivery_hour:
                if len(r) == 0 or r == '00:00':
                    return dialogs.launch_error(self, u'Dados insulficientes para registro de entrega!')

        file_path = core.directory_paths['saves'] + date + ".txt"
        day_data = shelve.open(file_path)

        if "sales" not in day_data:
            day_data["sales"] = {}
            day_data["secount"] = 0
            day_data["edit"] = {}
            day_data["spent"] = {}
            day_data["spcount"] = 0
            day_data["closure"] = []
            day_data["wastes"] = {}
            day_data["wcount"] = 0
        if not self.argv:
            key = day_data["secount"] + 1
            asn = day_data["sales"]
            asn[key] = {'time': finish_time,
                        'edit': 0,
                        'descriptions': products_descriptions,
                        'amounts': products_amounts,
                        'unit_prices': products_unitary_prices,
                        'prices': products_total_price,
                        'sold': total_price,
                        'discount': discount,
                        'tax': additional_taxes,
                        'value': final_value,
                        'payment': payment_method,
                        'client_name': client_name,
                        'client_id': client_id,
                        'delivery': self.delivery_enabled,
                        'receiver': delivery_receiver_name,
                        'adress': delivery_address,
                        'tel1': client_telephone,
                        'city': delivery_city,
                        'date': delivery_date,
                        'hour': delivery_hour}
            day_data["sales"] = asn
            day_data["secount"] = key
        else:
            day_data.close()
            day_data = shelve.open(self.argv[0])
            key = self.argv[1]
            hour = self.argv[2]
            asn = day_data["sales"]
            nsa = day_data["edit"]
            old = day_data["sales"][key]
            nsa[finish_time] = day_data["sales"][key]
            nsa[finish_time]['key'] = key
            nsa[finish_time]['argv'] = 1
            day_data["edit"] = nsa
            asn[key] = {'time': hour,
                        'edit': 1,
                        'descriptions': products_descriptions,
                        'amounts': products_amounts,
                        'unit_prices': products_unitary_prices,
                        'prices': products_total_price,
                        'sold': total_price,
                        'discount': discount,
                        'tax': additional_taxes,
                        'value': final_value,
                        'payment': payment_method,
                        'client_name': client_name,
                        'client_id': client_id,
                        'delivery': self.delivery_enabled,
                        'receiver': delivery_receiver_name,
                        'adress': delivery_address,
                        'tel1': client_telephone,
                        'city': delivery_city,
                        'date': delivery_date,
                        'hour': delivery_hour}
            day_data['sales'] = asn

            # Desfaz as alteracoes no estoque feitas pela venda original
            for f in old['descriptions']:
                g = 0
                k = old['descriptions'].index(f)
                l = old['unit_prices'][k]
                m = old['amounts'][k]
                for ids in self.database_inventory:
                    if lower(f) == lower(self.database_inventory[ids]['description']) and l == \
                            self.database_inventory[ids]['price']:
                        q = core.directory_paths['inventory'] + ids + '%s_infos.txt' % ids
                        s = shelve.open(q)
                        try:
                            v = int(s['amount'].replace(' ', ''))
                            if v < 0:
                                s['amount'] = 0
                            else:
                                s['amount'] = v + m
                        except ValueError:
                            pass
                        s.close()
                        g = 1
                        break
                if g == 1:
                    w = core.directory_paths['inventory'] + ids + core.slash + '%s_sales.txt' % ids
                    tu = self.argv[0].split(core.slash)
                    r = str('%s_%s' % (tu[-1][:-4], self.argv[2].replace(':', '-')))
                    d = shelve.open(w)
                    des = d
                    if r in des:
                        del des[r]
                    d = des
                    d.close()

            # Desfaz as alteracoes no registro do cliente feitas pela venda original
            if old['client_id']:
                if old['client_id'] in os.listdir(core.directory_paths['clients']):
                    try:
                        w = core.directory_paths['clients'] + old['client_id'] + core.slash + '%s_sales.txt' % old[
                            'client_id']
                        tu = self.argv[0].split(core.slash)
                        r = str('%s_%s' % (tu[1][:-4], self.argv[2].replace(':', '-')))
                        d = shelve.open(w)
                        qu = d
                        if r in qu:
                            del qu[r]
                        d = qu
                        d.close()
                    except KeyError:
                        pass
        for f in products_descriptions:
            g = 0
            k = products_descriptions.index(f)
            l = products_unitary_prices[k]
            m = products_amounts[k]
            for ids in self.database_inventory:
                if lower(f) == lower(self.database_inventory[ids]['description']) and l == self.database_inventory[ids][
                        'price']:
                    q = core.directory_paths['inventory'] + ids + core.slash + '%s_infos.txt' % ids
                    s = shelve.open(q)
                    try:
                        v = int(s['amount'].replace(' ', ''))
                        if v - m < 0:
                            s['amount'] = 0
                        else:
                            s['amount'] = v - m
                    except ValueError:
                        pass
                    s.close()
                    g = 1
                    break
            if g == 1:
                w = core.directory_paths['inventory'] + ids + core.slash + '%s_infos.txt' % ids
                r = '%s_%s' % (date, finish_time.replace(':', '-'))
                d = shelve.open(w)
                x = asn[key]
                x['key'] = key
                d[r] = x
                d.close()
        if client_id:
            if client_id in os.listdir('clients'):
                w = core.directory_paths['clients'] + str(client_id) + core.slash + '%s_deals.txt' % client_id
                r = '%s_%s' % (date, finish_time.replace(':', '-'))
                d = shelve.open(w)
                x = asn[key]
                x['key'] = key
                d[r] = x
                d.close()

        # Caso seja entrega, adiciona-a ao sistema                 
        delivery_database = shelve.open(core.directory_paths['saves'] + "deliverys.txt")
        if self.argv:
            delivery_key = self.argv[0].split(core.slash)[-1][:-4] + ' ' + str(hour)
        else:
            delivery_key = date + ' ' + finish_time
        if delivery_key in delivery_database:
            tf = delivery_database[delivery_key][1]
        else:
            tf = False
        delivery_database[delivery_key] = [key, tf, '']
        delivery_database.close()

        self.clean()
        day_data.close()
        if not self.argv:
            dialogs.Confirmation(self, u"Sucesso", 1)
        else:
            if type(self.GetParent()) is daily_report.Report:
                self.GetParent().setup(None)
            self.Close()
