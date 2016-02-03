#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
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
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        panel_top = wx.Panel(self, pos=(10, 10), size=(1180, 100))

        button_categories = GenBitmapTextButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'Drawer.png',
                                                wx.BITMAP_TYPE_PNG), u'Categorias', pos=(5, 40), size=(115, 40),
                                                style=wx.SIMPLE_BORDER)
        button_categories.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        button_categories.Bind(wx.EVT_BUTTON, self.open_category_manager)
        panel_buttons_left = wx.Panel(panel_top, pos=(140, 40), size=(500, 40), style=wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Search.png', wx.BITMAP_TYPE_PNG),
                                  u'Ver Mais', pos=(0, 0), size=(100, 40))
        see.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        see.Bind(wx.EVT_BUTTON, self.data_open)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(100, 0), size=(100, 40))
        plus.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        plus.Bind(wx.EVT_BUTTON, self.open_new_product)

        mplus = GenBitmapTextButton(panel_buttons_left, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Box_download.png', wx.BITMAP_TYPE_PNG),
                                    u'Entrada', pos=(200, 0), size=(100, 40))
        mplus.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        mplus.Bind(wx.EVT_BUTTON, self.open_update_inventory)

        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(300, 0), size=(100, 40))
        edi.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(400, 0), size=(100, 40))
        era.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)
        self.textbox_filter = wx.SearchCtrl(panel_top, -1, pos=(665, 45), size=(200, 30), style=wx.TE_PROCESS_ENTER)
        self.textbox_filter.SetDescriptiveText(u'Busca por nome')
        self.textbox_filter.ShowCancelButton(True)
        fin = wx.BitmapButton(panel_top, -1, wx.Bitmap(core.directory_paths['icons'] + 'edit_find.png'),
                              pos=(870, 42), size=(35, 35), style=wx.NO_BORDER)
        fin.Bind(wx.EVT_BUTTON, self.database_search)
        fin.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        self.textbox_filter.Bind(wx.EVT_TEXT_ENTER, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.clean)
        panel_buttons_right = wx.Panel(panel_top, pos=(930, 40), size=(240, 40), style=wx.SIMPLE_BORDER)
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
        panel_center = wx.Panel(self, -1, pos=(10, 110), size=(1180, 410))
        self.list_products = wx.ListCtrl(panel_center, -1, pos=(5, 5), size=(1170, 390),
                                         style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
        self.list_products.InsertColumn(0, u'Descrição do produto', width=400)
        self.list_products.InsertColumn(1, u'ID', width=50)
        self.list_products.InsertColumn(2, u'Categoria', width=150)
        self.list_products.InsertColumn(3, u'Preço', width=200)
        self.list_products.InsertColumn(4, u'Estoque', width=180)
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
            category = db.categories_search_id(product.category_ID)
            self.list_products.Append((product.description, product.ID,
                                       category.category,
                                       core.format_cash_user(product.price, currency=True),
                                       core.format_amount_user(product.amount, unit=category.unit),
                                       core.format_amount_user(product.sold, unit=category.unit)))
        db.close()

    def data_delete(self, event):
        it = self.list_products.GetFocusedItem()
        if it == -1:
            return
        e_id = self.list_products.GetItem(it, 1).GetText()
        db = database.InventoryDB()
        db.delete_product(int(e_id))
        db.close()
        self.setup(None)

    def data_edit(self, event):
        po = self.list_products.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_products.GetItem(po, 1).GetText()
        ko = self.list_products.GetItemText(po)
        ProductData(self, title=ko, product_id=lo, editable=True)

    def data_open(self, event):
        po = self.list_products.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_products.GetItem(po, 1).GetText()
        ko = self.list_products.GetItemText(po)
        ProductData(self, title=ko, product_id=lo, editable=False)

    def database_search(self, event):
        self.list_products.DeleteAllItems()
        db = database.InventoryDB()
        info = self.textbox_filter.GetValue()
        inventory = db.inventory_search(info)
        for product in inventory:
            category = db.categories_search_id(product.category_ID)
            self.list_products.Append((product.description, product.ID,
                                       category.category,
                                       core.format_cash_user(product.price, currency=True),
                                       core.format_amount_user(product.amount, unit=category.unit),
                                       core.format_amount_user(product.sold, unit=category.unit)))
        db.close()

    def clean(self, event):
        self.textbox_filter.Clear()
        self.setup(event)

    def ask_delete(self, event):
        dialogs.Ask(self, u'Apagar Produto', 25)

    def open_category_manager(self, event):
        categories.ProductCategoryManager(self)

    def open_new_product(self, event):
        ProductData(self)

    def open_update_inventory(self, event):
        UpdateInventory(self)

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

    def __init__(self, parent, title='Cadastro de Produto', product_id=-1, data=None, editable=True):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
                          wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)
        self.product_id = product_id
        self.data = data
        self.editable = editable
        self.parent = parent
        self.title = title

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.SetSize(wx.Size(500, 410))
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
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

        if self.editable:
            self.update_categories()

        if self.data:
            self.product_id = self.data.ID
        elif self.product_id != -1:
            self.data = db.inventory_search_id(self.product_id)
        else:
            db.close()

            self.textbox_description.SetValue('')
            self.textbox_price.SetValue('R$ 0,00')
            self.textbox_amount.SetValue('')
            self.textbox_supplier.SetValue('')
            self.textbox_observation.SetValue('')
            self.update_categories()

            return
        category = db.categories_search_id(self.data.category_ID)

        self.textbox_description.SetValue(self.data.description)
        self.textbox_barcode.SetValue(self.data.barcode)
        self.textbox_price.SetValue(core.format_cash_user(self.data.price, currency=True))
        self.textbox_amount.SetValue(core.format_amount_user(self.data.amount, unit=category.unit))
        self.textbox_supplier.SetValue(self.data.supplier)
        self.textbox_observation.SetValue(self.data.obs)

        self.combobox_category.SetValue(category.category)

        db.close()

    def update_categories(self):
        db = database.InventoryDB()
        category_list = db.categories_list()
        category_options = [u'Selecione']
        for category in category_list:
            category_options.append(category.category)
        self.combobox_category.SetItems(category_options)
        self.combobox_category.SetSelection(0)
        db.close()

    def set_editable(self, event):
        ProductData(self.parent, self.title, self.product_id, self.data, True)
        self.Close()

    def end(self):

        if not self.textbox_description.GetValue():
            return dialogs.launch_error(self, u'É necessária uma descrição!')
        if self.combobox_category.GetSelection() == 0:
            return dialogs.launch_error(self, u'Selecione uma categoria!')

        amount_str = self.textbox_amount.GetValue()

        try:
            amount = core.amount2float(amount_str)
        except ValueError:
            self.textbox_amount.Clear()
            return dialogs.launch_error(self, u'Quantidade inválida!')

        rdate, rtime = core.datetime_today()
        names = strip(self.textbox_description.GetValue()).split()
        for i in range(0, len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        db = database.InventoryDB()
        category = db.category_search_name(self.combobox_category.GetValue())
        barcode = self.textbox_barcode.GetValue()

        s = data_types.ProductData()
        if barcode:
            s.barcode = barcode

        s.ID = self.product_id
        s.description = namef
        s.price = core.money2float(self.textbox_price.GetValue())
        s.amount = int(amount)
        s.category_ID = category.ID
        s.supplier = self.textbox_supplier.GetValue()
        s.obs = self.textbox_observation.GetValue()
        s.record_time = rtime
        s.record_date = rdate

        if self.data:
            db.edit_product(s)
        else:
            db.insert_product(s)
        db.close()

        if isinstance(self.parent, InventoryManager):
            self.parent.setup(None)

        elif isinstance(self.parent, sale.Sale):
            self.parent.database_inventory.insert_product(s)
            self.parent.database_search(None)

        if self.data:
            return self.exit(None)

        self.clean()
        dialogs.Confirmation(self, u'Sucesso', 5)

    def OnPaint(self, event):
        wx.PaintDC(self.panel_image).DrawBitmap(
            core.resize_bitmap(wx.Bitmap(core.directory_paths['custom'] + 'logo-canela-santa.jpg'),
                               self.panel_image.GetSizeTuple()[0], self.panel_image.GetSizeTuple()[1]), 0, 0)

    def exit(self, event):
        self.Close()


class UpdateInventory(wx.Frame):

    textbox_product_description = None
    textbox_product_id = None
    textbox_product_price = None
    textbox_product_amount = None
    textbox_product_unit = None

    list_inventory = None
    list_update = None

    radio_update = None
    radio_entry = None

    panel_product_data = None
    __panel_product = None

    item = None

    def __init__(self, parent, title=u'Entrada de Produtos'):
        wx.Frame.__init__(self, parent, -1, title, size=(470, 675),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |
                          wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)

        self.parent = parent
        self.setup_gui()

        self.database_inventory = database.InventoryDB(':memory:')
        self.database_search(None)

        self.Show()

    def setup_gui(self):
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.Centre()

        self.list_update = wx.ListCtrl(self, -1, pos=(10, 280), size=(450, 275),
                                       style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.list_update.InsertColumn(0, u"ID", width=50)
        self.list_update.InsertColumn(1, u"Descrição", width=180)
        self.list_update.InsertColumn(2, u"Quantidade")
        self.list_update.InsertColumn(3, u"Preço Unit.")

        self.radio_update = wx.RadioButton(self, -1, label=u'Atualizar estoque', pos=(10, 560), size=(225, 25),
                                           style=wx.SIMPLE_BORDER)
        self.radio_entry = wx.RadioButton(self, -1, label=u'Entrada de produtos', pos=(235, 560), size=(225, 25),
                                          style=wx.SIMPLE_BORDER)

        self.radio_update.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.radio_entry.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.radio_update.SetToolTip(wx.ToolTip(u'Dar uma nova quantidade em estoque para os produtos.'
                                                u'\nIgnora um estoque anterior.'))
        self.radio_entry.SetToolTip(wx.ToolTip(u'Atualiza o estoque de acordo com uma entrada de produtos.'
                                               u'\nApenas registra uma variação no estoque.'))

        self.radio_entry.SetValue(True)

        # product
        self.panel_product_data = wx.Panel(self, 22, pos=(10, 10), size=(450, 260),
                                           style=wx.DOUBLE_BORDER | wx.TAB_TRAVERSAL)
        self.panel_product_data.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        fin = wx.BitmapButton(self.panel_product_data, -1, wx.Bitmap(core.directory_paths['icons'] + 'Add.png'),
                              pos=(408, 10), size=(32, 32), style=wx.NO_BORDER)
        fin.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        fin.Bind(wx.EVT_BUTTON, self.open_product_register)

        self.textbox_product_description = wx.SearchCtrl(self.panel_product_data, 223, pos=(10, 10), size=(395, 32))
        self.textbox_product_description.Bind(wx.EVT_TEXT, self.database_search, id=223)
        self.textbox_product_description.ShowSearchButton(False)
        self.textbox_product_description.SetDescriptiveText(u'Descrição do produto')
        self.list_inventory = wx.ListCtrl(self.panel_product_data, -1, pos=(10, 45), size=(430, 115),
                                          style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.list_inventory.InsertColumn(0, u'Descrição', width=230)
        self.list_inventory.InsertColumn(1, u'Estoque')
        self.list_inventory.InsertColumn(2, u'Preço')
        self.list_inventory.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.database_select)

        self.textbox_product_id = wx.SearchCtrl(self.panel_product_data, -1, pos=(10, 170), size=(100, -1))
        self.textbox_product_id.ShowSearchButton(False)
        self.textbox_product_id.SetDescriptiveText(u'ID')

        self.textbox_product_price = wx.SearchCtrl(self.panel_product_data, -1, pos=(130, 170), size=(80, -1))
        self.textbox_product_price.ShowSearchButton(False)
        self.textbox_product_price.SetDescriptiveText(u'Preço')
        self.textbox_product_price.SetValue(u'R$ 0,00')
        self.textbox_product_price.Disable()

        self.textbox_product_amount = wx.SearchCtrl(self.panel_product_data, -1, pos=(230, 170), size=(100, -1))
        self.textbox_product_amount.ShowSearchButton(False)
        self.textbox_product_amount.SetDescriptiveText(u'Quantidade')

        self.textbox_product_unit = wx.TextCtrl(self.panel_product_data, -1, pos=(335, 175), size=(50, -1),
                                                style=wx.NO_BORDER | wx.TE_READONLY)
        self.textbox_product_unit.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        self.__panel_product = wx.Panel(self.panel_product_data, size=(300, 40), pos=(100, 210),
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

        bottom = wx.Panel(self, -1, size=(450, 50), pos=(10, 590), style=wx.SIMPLE_BORDER)
        add = GenBitmapTextButton(bottom, -1, wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                  u'Registrar produtos', size=(200, 50), pos=(0, 0))
        reset = GenBitmapTextButton(bottom, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                    u'Recomeçar', size=(125, 50), pos=(200, 0))
        cancel = GenBitmapTextButton(bottom, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u'Sair', size=(125, 50), pos=(325, 0))
        add.Bind(wx.EVT_BUTTON, self.ask_end)
        reset.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

    def ask_end(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 15)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        if self.list_update.GetItemCount() == 0:
            self.exit(None)
            return
        dialogs.Ask(self, u'Sair', 91)

    def clean(self):
        self.list_update.DeleteAllItems()
        self.data_editor_disable(None)
        self.database_search(None)

    def open_product_register(self, event):
        ProductData(self)

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

        unit = self.textbox_product_unit.GetValue()

        unit_price = core.format_cash_user(product.price, currency=True)
        item = self.list_update.Append((core.format_id_user(product.ID), product.description,
                                        core.format_amount_user(amount, unit=unit), unit_price))
        self.list_update.SetItemData(item, product_id)

        self.textbox_product_amount.Clear()
        self.textbox_product_id.Clear()
        self.textbox_product_description.Clear()
        self.textbox_product_price.SetValue(u"0,00")
        self.textbox_product_unit.Clear()

    def data_delete(self, event):
        if self.list_update.GetFocusedItem() == -1:
            return
        self.list_update.DeleteItem(self.list_update.GetFocusedItem())

    def data_editor_enable(self, event):
        self.item = self.list_update.GetFocusedItem()
        if not self.item == -1:
            amount, unit = self.list_update.GetItemText(self.item, 2).split()
            self.textbox_product_description.SetValue(self.list_update.GetItemText(self.item, 1))
            self.textbox_product_id.SetValue(str(self.list_update.GetItemData(self.item)))
            self.textbox_product_price.SetValue(self.list_update.GetItemText(self.item, 3))
            self.textbox_product_amount.SetValue(amount)
            self.textbox_product_unit.SetValue(unit)
            self.__panel_product.Destroy()
            self.__panel_product = wx.Panel(self.panel_product_data, size=(200, 40), pos=(200, 210),
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

        _amount = core.amount2float(self.textbox_product_amount.GetValue())
        try:
            amount = float(_amount)
        except ValueError:
            self.textbox_product_amount.Clear()
            return dialogs.launch_error(self, u'Quantidade inválida!')

        unit_price = core.format_cash_user(product.price, currency=True)
        unit = self.textbox_product_unit.GetValue()

        self.list_update.SetStringItem(self.item, 0, core.format_id_user(product.ID))
        self.list_update.SetStringItem(self.item, 1, product.description)
        self.list_update.SetStringItem(self.item, 2, core.format_amount_user(amount, unit=unit))
        self.list_update.SetStringItem(self.item, 3, unit_price)

        self.list_update.SetItemData(self.item, product_id)

        self.data_editor_disable(event)

    def data_editor_disable(self, event):
        self.textbox_product_unit.Clear()
        self.textbox_product_amount.Clear()
        self.textbox_product_price.Clear()
        self.textbox_product_id.Clear()
        self.textbox_product_description.Clear()
        self.__panel_product.Destroy()
        self.__panel_product = wx.Panel(self.panel_product_data, size=(300, 40), pos=(100, 210), style=wx.SIMPLE_BORDER)
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

    def end(self):

        w = self.list_update.GetItemCount()
        if w == 0:
            return dialogs.launch_error(self, u'Você não adicionou nenhum produto!')

        update = self.radio_update.GetValue()
        entry = self.radio_entry.GetValue()
        db = database.InventoryDB()
        for i in range(w):
            products_id = self.list_update.GetItemData(i)
            amount = core.amount2float(self.list_update.GetItemText(i, 2))
            if update:
                db.update_product_amount(products_id, amount)
            elif entry:
                db.update_product_stock(products_id, amount)

        db.close()

        self.clean()
        dialogs.Confirmation(self, u'Sucesso', 6)
