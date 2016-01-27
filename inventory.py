#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import threading
from datetime import datetime
from string import strip

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import categories
import database
import data_types
import sale

__author__ = 'Julio'


class InventoryManager(wx.Frame):

    dict_products = None

    list_products = None
    textbox_filter = None

    def __init__(self, parent, title=u'Estoque'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(100, 100))
        self.SetSize(wx.Size(1200, 550))
        self.SetIcon((wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.default_background_color)
        panel_top = wx.Panel(self, pos=(10, 10), size=(1180, 100))

        button_categories = GenBitmapTextButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'Tools.png',
                                                wx.BITMAP_TYPE_PNG), u'Categorias', pos=(10, 40), size=(100, 40),
                                                style=wx.SIMPLE_BORDER)
        button_categories.SetBackgroundColour(core.default_background_color)
        button_categories.Bind(wx.EVT_BUTTON, self.open_category_manager)
        panel_buttons_left = wx.Panel(panel_top, pos=(120, 40), size=(500, 40), style=wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Tools.png', wx.BITMAP_TYPE_PNG),
                                  u'Ver Mais', pos=(0, 0), size=(100, 40))
        see.SetBackgroundColour(core.default_background_color)
        see.Bind(wx.EVT_BUTTON, self.data_open)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(100, 0), size=(100, 40))
        plus.SetBackgroundColour(core.default_background_color)
        plus.Bind(wx.EVT_BUTTON, self.open_new_product)
        mplus = GenBitmapTextButton(panel_buttons_left, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Box_download.png', wx.BITMAP_TYPE_PNG),
                                    u'Entrada', pos=(200, 0), size=(100, 40))
        mplus.SetBackgroundColour(core.default_background_color)
        mplus.Bind(wx.EVT_BUTTON, self.open_update_inventory)
        # Desabilitado por enquanto
        mplus.Disable()
        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(300, 0), size=(100, 40))
        edi.SetBackgroundColour(core.default_background_color)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(400, 0), size=(100, 40))
        era.SetBackgroundColour(core.default_background_color)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)
        self.textbox_filter = wx.SearchCtrl(panel_top, -1, pos=(650, 45), size=(200, 30), style=wx.TE_PROCESS_ENTER)
        self.textbox_filter.SetDescriptiveText(u'Busca por nome')
        self.textbox_filter.ShowCancelButton(True)
        self.textbox_filter.SetCancelBitmap(wx.Bitmap(core.directory_paths['icons'] + 'Erase2.png', wx.BITMAP_TYPE_PNG))
        fin = wx.BitmapButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'edit_find.png'),
                              pos=(855, 42), size=(35, 35), style=wx.NO_BORDER)
        fin.Bind(wx.EVT_BUTTON, self.database_search)
        fin.SetBackgroundColour(core.default_background_color)
        self.textbox_filter.Bind(wx.EVT_TEXT_ENTER, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.clean)
        panel_buttons_right = wx.Panel(panel_top, pos=(900, 40), size=(240, 40), style=wx.SIMPLE_BORDER)
        quir = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                   u'Sair',
                                   pos=(120, 0), size=(120, 40))
        quir.SetBackgroundColour(core.default_background_color)
        quir.Bind(wx.EVT_BUTTON, self.exit)
        rep = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                  u'Atualizar',
                                  pos=(0, 0), size=(120, 40))
        rep.SetBackgroundColour(core.default_background_color)
        rep.Bind(wx.EVT_BUTTON, self.setup)
        panel_center = wx.Panel(self, -1, pos=(10, 110), size=(1180, 410))
        self.list_products = wx.ListCtrl(panel_center, -1, pos=(5, 5), size=(1170, 390),
                                         style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
        self.list_products.InsertColumn(0, u'Descrição do produto', width=400)
        self.list_products.InsertColumn(1, u'ID', width=50)
        self.list_products.InsertColumn(2, u'Categoria', width=150)
        self.list_products.InsertColumn(3, u'Preço', width=200)
        self.list_products.InsertColumn(4, u'Estoque', width=100)
        self.list_products.InsertColumn(5, u'Vendidos', width=100)
        self.list_products.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_open)

    def setup(self, event):     # FIXME Fazer a thread fechar direito com o resto do app
        rest = threading.Thread(target=self.__setup__)
        rest.daemon = True
        rest.start()

    def __setup__(self):
        self.list_products.DeleteAllItems()
        self.textbox_filter.Clear()
        db = database.InventoryDB()
        inventory = db.product_list()
        for product in inventory:
            self.list_products.Append((product.description, product.ID,
                                       db.categories_search_id(product.category_ID).category,
                                       'R$ ' + core.good_show('money', product.price), product.amount, product.sold))
        db.close()

    def data_delete(self, event):   # TODO Fazer os dados não serem apagados permanentemente
        it = self.list_products.GetFocusedItem()
        if it == -1:
            return
        e_id = self.list_products.GetItem(it, 1).GetText()
        db = database.InventoryDB()
        db.delete_product(e_id)
        db.close()
        self.setup(None)

    def data_edit(self, event):
        po = self.list_products.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_products.GetItem(po, 1).GetText()
        ko = self.list_products.GetItemText(po)
        ProductData(self, ko, lo, True)

    def data_open(self, event):
        po = self.list_products.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_products.GetItem(po, 1).GetText()
        ko = self.list_products.GetItemText(po)
        ProductData(self, ko, lo, False)

    def database_search(self, event):
        self.list_products.DeleteAllItems()
        db = database.InventoryDB()
        info = self.textbox_filter.GetValue()
        inventory = db.inventory_search(info)
        for product in inventory:
            self.list_products.Append((product.description, product.ID,
                                       db.categories_search_id(product.category_ID).category,
                                       'R$ ' + core.good_show('money', product.price), product.amount, product.sold))
        db.close()

    def clean(self, event):
        self.textbox_filter.Clear()
        self.setup(event)

    def ask_delete(self, event):
        dialogs.Ask(self, u'Apagar Produto', 25)

    def open_category_manager(self, event):
        categories.CategoryManager(self)

    def open_new_product(self, event):
        ProductRegister(self)

    def open_update_inventory(self, event):
        UpdateInventory(self)

    def exit(self, event):
        self.Close()


class ProductRegister(wx.Frame):
    panel_data = None
    panel_image = None

    textbox_description = None
    textbox_barcode = None
    textbox_amount = None
    textbox_price = None
    textbox_supplier = None
    textbox_observation = None

    combobox_category = None

    def __init__(self, parent, title=u'Cadastro de Produtos'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
                          wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)
        self.parent = parent

        self.setup_gui()

        self.Show()

    def setup_gui(self):

        self.Centre()
        self.SetSize(wx.Size(500, 410))
        self.SetIcon((wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.default_background_color)

        self.panel_data = wx.Panel(self, -1, pos=(0, 0), size=(500, 320), style=wx.TAB_TRAVERSAL)
        wx.StaticText(self.panel_data, -1, u'Descrição do produto:', pos=(190, 10))
        wx.StaticText(self.panel_data, -1, u'Código de Barras:', pos=(190, 70))
        wx.StaticText(self.panel_data, -1, u'Preço:', pos=(190, 130))
        wx.StaticText(self.panel_data, -1, u'Estoque:', pos=(350, 130))
        wx.StaticText(self.panel_data, -1, u'Categoria:', pos=(190, 190))
        wx.StaticText(self.panel_data, -1, u'Fornecedor:', pos=(350, 190))
        wx.StaticText(self.panel_data, -1, u'Observações:', pos=(10, 230))
        self.textbox_description = wx.TextCtrl(self.panel_data, -1, pos=(190, 30), size=(300, 30))
        self.textbox_barcode = wx.TextCtrl(self.panel_data, -1, pos=(190, 90), size=(300, 30))
        self.textbox_price = wx.TextCtrl(self.panel_data, -1, pos=(190, 150), size=(100, 30))
        self.textbox_amount = wx.TextCtrl(self.panel_data, -1, pos=(350, 150), size=(100, 30))
        self.combobox_category = wx.ComboBox(self.panel_data, -1, pos=(190, 210), size=(150, 30), style=wx.TE_READONLY)
        self.textbox_supplier = wx.TextCtrl(self.panel_data, -1, pos=(350, 210), size=(140, 30))
        self.textbox_observation = wx.TextCtrl(self.panel_data, -1, pos=(10, 250), size=(480, 65),
                                               style=wx.TE_MULTILINE)
        self.textbox_barcode.Bind(wx.EVT_CHAR, core.check_number)
        self.textbox_price.Bind(wx.EVT_CHAR, core.check_currency)

        button_category = wx.BitmapButton(self.panel_data, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                          pos=(150, 204), size=(32, 32), style=wx.NO_BORDER)
        button_category.Bind(wx.EVT_BUTTON, self.open_category_register)
        button_category.SetBackgroundColour(core.default_background_color)

        self.panel_image = wx.Panel(self.panel_data, -1, size=(150, 150), pos=(10, 45), style=wx.SIMPLE_BORDER)
        self.panel_image.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.panel_image, self.OnPaint)
        self.clean()

        panel_bottom = wx.Panel(self, -1, pos=(0, 325), size=(500, 50))
        panel_bottom_buttons = wx.Panel(panel_bottom, pos=(90, 5), size=(320, 40), style=wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(panel_bottom_buttons, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                     u"Finalizar", pos=(0, 0), size=(100, 40))
        finish.Bind(wx.EVT_BUTTON, self.ask_end)
        restart = GenBitmapTextButton(panel_bottom_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u"Recomeçar", pos=(100, 0), size=(120, 40))
        restart.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u"Sair", pos=(220, 0), size=(100, 40))
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)

    def ask_end(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 15)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        if self.textbox_description.GetValue():
            dialogs.Ask(self, u'Sair', 91)
        else:
            self.Close()

    def open_category_register(self, event):
        categories.CategoryData(self)

    def update_categories(self):
        db = database.InventoryDB()
        category_list = db.categories_list()
        category_options = [u'Selecione']
        for category in category_list:
            category_options.append(category.category)
        self.combobox_category.SetItems(category_options)
        self.combobox_category.SetSelection(0)
        db.close()

    def clean(self):
        self.textbox_description.SetValue('')
        self.textbox_price.SetValue('R$ 0,00')
        self.textbox_amount.SetValue('')
        self.textbox_supplier.SetValue('')
        self.textbox_observation.SetValue('')
        self.update_categories()

    def end(self):
        if not self.textbox_description.GetValue():
            return dialogs.launch_error(self, u'É necessária uma descrição!')
        if self.combobox_category.GetSelection() == 0:
            return dialogs.launch_error(self, u'Selecione uma categoria!')

        rtime = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(datetime.now().day))

        names = strip(self.textbox_description.GetValue()).split()
        for i in range(0, len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)

        db = database.InventoryDB()
        category = db.category_id(self.combobox_category.GetValue())

        barcode = self.textbox_barcode.GetValue()
        s = data_types.ProductData()
        if barcode:
            s.barcode = barcode
        s.description = namef
        s.price = float(self.textbox_price.GetValue().replace(',', '.').replace('R$ ', ''))
        s.amount = int(self.textbox_amount.GetValue())
        s.category_ID = category.ID
        s.supplier = self.textbox_supplier.GetValue()
        s.obs = self.textbox_observation.GetValue()
        s.record_time = rtime
        s.record_date = rdate
        db.insert_product(s)
        db.close()
        if isinstance(self.parent, sale.Sale):
            self.parent.database_inventory.insert_product(s)
            self.parent.database_search(None)
        self.clean()

        dialogs.Confirmation(self, u'Sucesso', 5)

    def OnPaint(self, event):
        wx.PaintDC(self.panel_image).DrawBitmap(
            core.resize_bitmap(wx.Bitmap(core.directory_paths['custom'] + 'logo-canela-santa.jpg'),
                               self.panel_image.GetSizeTuple()[0], self.panel_image.GetSizeTuple()[1]), 0, 0)
    
    def exit(self, event):
        self.Close()


class ProductData(wx.Frame):
    panel_data = None
    panel_image = None

    textbox_description = None
    textbox_barcode = None
    textbox_amount = None
    textbox_price = None
    textbox_supplier = None
    textbox_observation = None

    combobox_category = None

    def __init__(self, parent, title, product_id, editable=True):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
                          wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)
        self.product_id = product_id
        self.editable = editable
        self.parent = parent
        self.title = title

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.SetSize(wx.Size(500, 410))
        self.SetIcon((wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.default_background_color)
        self.Centre()
        self.panel_data = wx.Panel(self, -1, pos=(0, 0), size=(500, 320), style=wx.TAB_TRAVERSAL)
        wx.StaticText(self.panel_data, -1, u'Descrição do produto:', pos=(190, 10))
        wx.StaticText(self.panel_data, -1, u'Código de Barras:', pos=(190, 70))
        wx.StaticText(self.panel_data, -1, u'Preço:', pos=(190, 130))
        wx.StaticText(self.panel_data, -1, u'Estoque:', pos=(350, 130))
        wx.StaticText(self.panel_data, -1, u'Categoria:', pos=(190, 190))
        wx.StaticText(self.panel_data, -1, u'Fornecedor:', pos=(350, 190))
        wx.StaticText(self.panel_data, -1, u'Observações:', pos=(10, 230))
        self.textbox_description = wx.TextCtrl(self.panel_data, -1, pos=(190, 30), size=(300, 30))
        self.textbox_barcode = wx.TextCtrl(self.panel_data, -1, pos=(190, 90), size=(300, 30))
        self.textbox_price = wx.TextCtrl(self.panel_data, -1, pos=(190, 150), size=(100, 30))
        self.textbox_amount = wx.TextCtrl(self.panel_data, -1, pos=(350, 150), size=(100, 30))
        self.textbox_price.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_barcode.Bind(wx.EVT_CHAR, core.check_number)
        if not self.editable:
            self.combobox_category = wx.TextCtrl(self.panel_data, -1, pos=(190, 210), size=(150, 30))
        else:
            self.combobox_category = wx.ComboBox(self.panel_data, -1, pos=(190, 210), size=(150, 30),
                                                 style=wx.TE_READONLY)
        self.textbox_supplier = wx.TextCtrl(self.panel_data, -1, pos=(350, 210), size=(140, 30))
        self.textbox_observation = wx.TextCtrl(self.panel_data, -1, pos=(10, 250), size=(480, 65),
                                               style=wx.TE_MULTILINE)
        self.panel_image = wx.Panel(self.panel_data, -1, size=(150, 150), pos=(10, 45), style=wx.SIMPLE_BORDER)
        self.panel_image.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.panel_image, self.OnPaint)
        panel_bottom = wx.Panel(self, -1, pos=(0, 325), size=(500, 50))
        if not self.editable:
            panel_bottom_buttons = wx.Panel(panel_bottom, pos=(150, 5), size=(200, 40), style=wx.SIMPLE_BORDER)
            edipo = GenBitmapTextButton(panel_bottom_buttons, -1,
                                        wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                        u"Editar", pos=(0, 0), size=(100, 40))
            edipo.Bind(wx.EVT_BUTTON, self.set_editable)
            cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair", pos=(100, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
            self.combobox_category.Disable()
            self.textbox_description.Disable()
            self.textbox_barcode.Disable()
            self.textbox_price.Disable()
            self.textbox_amount.Disable()
            self.textbox_supplier.Disable()
            self.textbox_observation.Disable()
        else:
            panel_bottom_buttons = wx.Panel(panel_bottom, pos=(90, 5), size=(320, 40), style=wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                         u"Finalizar", pos=(0, 0), size=(100, 40))
            finish.Bind(wx.EVT_BUTTON, self.ask_end)
            restart = GenBitmapTextButton(panel_bottom_buttons, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                          u"Recomeçar", pos=(100, 0), size=(120, 40))
            restart.Bind(wx.EVT_BUTTON, self.ask_clean)
            cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair", pos=(220, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
        self.clean()

    def ask_end(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 15)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        if self.editable == 1:
            dialogs.Ask(self, u'Sair', 91)
        elif self.editable == 0:
            self.Close()

    def clean(self):
        db = database.InventoryDB()
        category_list = db.categories_list()
        category_options = []
        for category in category_list:
            category_options.append(category.category)
        product = db.inventory_search_id(self.product_id)
        self.textbox_description.SetValue(product.description)
        self.textbox_barcode.SetValue(product.barcode)
        self.textbox_price.SetValue('R$ ' + core.good_show('money', product.price))
        self.textbox_amount.SetValue(str(product.amount))
        self.textbox_supplier.SetValue(product.supplier)
        self.textbox_observation.SetValue(product.obs)

        if self.editable:
            self.combobox_category.SetItems(category_options)
        self.combobox_category.SetValue(db.categories_search_id(product.category_ID).category)

        db.close()

    def set_editable(self, event):
        ProductData(self.parent, self.title, self.product_id, True)
        self.Close()

    def end(self):
        if not self.textbox_description.GetValue():
            return dialogs.launch_error(self, u'É necessária uma descrição!')

        rtime = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(
                datetime.now().day))
        names = strip(self.textbox_description.GetValue()).split()
        for i in range(0, len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        db = database.InventoryDB()
        category = db.category_id(self.combobox_category.GetValue())
        barcode = self.textbox_barcode.GetValue()

        s = data_types.ProductData()
        if barcode:
            s.barcode = barcode

        s.ID = self.product_id
        s.description = namef
        s.price = float(self.textbox_price.GetValue().replace(',', '.').replace('R$ ', ''))
        s.amount = int(self.textbox_amount.GetValue())
        s.category_ID = category.ID
        s.supplier = self.textbox_supplier.GetValue()
        s.obs = self.textbox_observation.GetValue()
        s.record_time = rtime
        s.record_date = rdate
        db.edit_product(s)
        db.close()

        if isinstance(self.parent, InventoryManager):
            self.parent.setup(None)

        self.exit(None)

    def OnPaint(self, event):
        wx.PaintDC(self.panel_image).DrawBitmap(
            core.resize_bitmap(wx.Bitmap(core.directory_paths['custom'] + 'logo-canela-santa.jpg'),
                               self.panel_image.GetSizeTuple()[0], self.panel_image.GetSizeTuple()[1]), 0, 0)

    def exit(self, event):
        self.Close()


class UpdateInventory(wx.Frame):

    dict_products = None

    new_products = None

    def __init__(self, parent, title=u'Entrada de Produtos'):
        wx.Frame.__init__(self, parent, -1, title, size=(850, 650),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
                          wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)

        self.parent = parent
        self.setup_gui()
        self.Show()

    def setup_gui(self):
        self.SetIcon((wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.Centre()
        self.new_products = []
        for i in range(10):
            if i >= 5:
                x = 435
                y = (i - 5) * 110 + 10
            else:
                x = 15
                y = i * 110 + 10
            panel = wx.Panel(self, -1, size=(400, 100), pos=(x, y), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
            pnm = wx.TextCtrl(panel, -1, size=(300, 30), pos=(95, 5))
            pam = wx.TextCtrl(panel, -1, size=(100, 30), pos=(95, 60))
            pct = wx.TextCtrl(panel, -1, size=(100, 30), pos=(285, 60))
            pam.Bind(wx.EVT_CHAR, core.check_number)
            pct.Bind(wx.EVT_CHAR, core.check_currency)
            pct.SetValue('R$ 0,00')
            self.new_products.append([pnm, pam, pct])
            panel.SetBackgroundColour(core.default_background_color)
            wx.StaticText(panel, -1, u'Descrição:', pos=(21, 12))
            wx.StaticText(panel, -1, u'Quantidade:', pos=(25, 67))
            wx.StaticText(panel, -1, u'Preço:', pos=(240, 67))

        bottom = wx.Panel(self, -1, size=(390, 50), pos=(230, 560), style=wx.SIMPLE_BORDER)
        add = GenBitmapTextButton(bottom, -1, wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                  u'Registrar produtos', size=(150, 50), pos=(0, 0))
        reset = GenBitmapTextButton(bottom, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                    u'Recomeçar', size=(120, 50), pos=(150, 0))
        cancel = GenBitmapTextButton(bottom, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u'Sair', size=(120, 50), pos=(270, 0))
        add.Bind(wx.EVT_BUTTON, self.ask_end)
        reset.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
        self.SetBackgroundColour(core.default_background_color)

    def ask_end(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 15)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        dialogs.Ask(self, u'Sair', 91)

    def end(self, event):
        prods = []
        for i in self.new_products:
            a = i[0].GetValue()
            b = i[1].GetValue()
            if a and b:
                b = int(b)
                d = i[2].GetValue()
                c = float(d.replace('R$ ', '').replace(',', '.'))
                if a and b and c:
                    prods.append([a, b, c, d])
        if not prods:
            a = wx.MessageDialog(self, u'Nenhum produto adicionado!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        if not os.path.exists(core.directory_paths['inventory']):
            os.mkdir(core.directory_paths['inventory'])
        dirs = os.listdir(core.directory_paths['inventory'])
        if os.path.exists('#Trash/inventory/deleted'):
            dirs += os.listdir('#Trash/inventory/deleted')
        if os.path.exists('#Trash/inventory/edited'):
            dirs += os.listdir('#Trash/inventory/edited')
        last_id = 0
        for i in dirs:
            try:
                if int(i) > last_id:
                    last_id = int(i)
            except ValueError:
                pass
        if type(self.parent) is not InventoryManager:
            self.dict_products = {}
            for root, dirs, files in os.walk(core.directory_paths['inventory']):
                if root != core.directory_paths['inventory']:
                    try:
                        o = shelve.open(root + core.slash + root.split(core.slash)[-1] + '_infos.txt')
                        self.dict_products[o['description']] = [str(int(root.split(core.slash)[-1])), o['category'],
                                                                'R$ ' + core.good_show('money',
                                                                                       str(o['price'])).replace('.',
                                                                                                                ','),
                                                                o['amount']]
                        o.close()
                    except ValueError:
                        pass
        else:
            self.dict_products = self.parent.dict_products
        for k in prods:
            names = strip(k[0]).split()
            for i in range(0, len(names)):
                names[i] = names[i].capitalize()
            namef = ' '.join(names)
            if namef not in self.dict_products:
                new_id = last_id + 1
                idstr = str(new_id)
                while len(idstr) < 6:
                    idstr = '0' + idstr
                os.mkdir(core.directory_paths['inventory'] + idstr)
                rtime = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                    datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
                rdate = str(datetime.now().year) + "-" + core.good_show("o", str(
                    datetime.now().month)) + "-" + core.good_show(
                    "o", str(datetime.now().day))
                po = (core.directory_paths['inventory'] + idstr + core.slash + idstr + '_infos.txt')
                s = shelve.open(po)
                s['description'] = namef
                s['price'] = k[2]
                s['amount'] = k[1]
                s['category'] = ''
                s['supplier'] = ''
                s['obs'] = ''
                s['time'] = rtime
                s['date'] = rdate
                s.close()
                last_id = new_id
                self.dict_products[namef] = [new_id, '', k[3], k[2]]
            else:
                if self.dict_products[namef][2] == k[3]:
                    idstr = str(self.dict_products[namef][0])
                    while len(idstr) < 6:
                        idstr = '0' + idstr
                    po = (core.directory_paths['inventory'] + idstr + core.slash + idstr + '_infos.txt')
                    s = shelve.open(po)
                    s['amount'] += k[1]
                    s.close()
        dialogs.Confirmation(self, u'Sucesso', 6)
        self.clean(None)

    def clean(self, event):
        for a in self.new_products:
            for b in a:
                b.Clear()

    def exit(self, event):
        self.Close()

