#!/usr/bin/env python
# -*- coding: utf-8 -*-


import threading
import string

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import database
import data_types
import inventory


class CategoryManager(wx.Frame):

    list_categories = None
    textbox_filter = None

    def __init__(self, parent, title=u'Gerenciador de Categorias'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.Center()
        self.SetSize(wx.Size(810, 550))
        self.SetIcon((wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.default_background_color)

        panel_top = wx.Panel(self, pos=(10, 10), size=(790, 100))

        panel_buttons_left = wx.Panel(panel_top, pos=(10, 40), size=(300, 40), style=wx.SIMPLE_BORDER)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(0, 0), size=(100, 40))
        plus.SetBackgroundColour(core.default_background_color)
        plus.Bind(wx.EVT_BUTTON, self.open_new_category)
        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(100, 0), size=(100, 40))
        edi.SetBackgroundColour(core.default_background_color)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(200, 0), size=(100, 40))
        era.SetBackgroundColour(core.default_background_color)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)

        self.textbox_filter = wx.SearchCtrl(panel_top, -1, pos=(315, 45), size=(200, 30), style=wx.TE_PROCESS_ENTER)
        self.textbox_filter.SetDescriptiveText(u'Busca')
        self.textbox_filter.Bind(wx.EVT_TEXT_ENTER, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.database_search)

        panel_buttons_right = wx.Panel(panel_top, pos=(530, 40), size=(240, 40), style=wx.SIMPLE_BORDER)
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

        panel_center = wx.Panel(self, -1, pos=(10, 110), size=(790, 410))
        self.list_categories = wx.ListCtrl(panel_center, -1, pos=(5, 5), size=(780, 390),
                                           style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
        self.list_categories.InsertColumn(1, u'ID', width=100)
        self.list_categories.InsertColumn(2, u'Categoria', width=450)
        self.list_categories.InsertColumn(3, u'NCM', width=200)
        self.list_categories.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_edit)

    def setup(self, event):     # FIXME Fazer a thread fechar direito com o resto do app
        rest = threading.Thread(target=self.__setup__)
        rest.start()

    def __setup__(self):
        self.list_categories.DeleteAllItems()
        db = database.InventoryDB()
        categories = db.categories_list()
        for category in categories:
            self.list_categories.Append((category.ID, category.category, category.ncm))

    def database_search(self, event):
        db = database.InventoryDB()
        categories = db.categories_search(event.getEventObject().getValue())
        for category in categories:
            self.list_categories.Append((category.ID, category.category, category.ncm))
        db.close()
        
    def clean(self, event):
        self.textbox_filter.Clear()

    def open_new_category(self, event):
        CategoryData(self)

    def ask_delete(self, event):
        dialogs.Ask(self, u"Apagar Categoria", 27)

    def data_delete(self, event):
        category_index = self.list_categories.GetFocusedItem()
        if category_index == -1:
            return
        db = database.InventoryDB()
        category_id = self.list_categories.GetItemText(category_index, 0)
        db.delete_category(category_id)
        self.setup(None)

    def data_edit(self, event):
        category_index = self.list_categories.GetFocusedItem()
        if category_index == -1:
            return 
        category_id = self.list_categories.GetItemText(category_index, 0)
        category_name = self.list_categories.GetItemText(category_index, 1)
        CategoryData(self, category_name, category_id)

    def exit(self, event):
        self.Close()


class CategoryData(wx.Frame):

    textbox_description = None
    textbox_ncm = None
    combobox_cfop = None
    combobox_unit = None

    def __init__(self, parent, title='Nova Categoria', category_id=-1):
        wx.Frame.__init__(self, parent, -1, title, size=(590, 200),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        self.category_id = category_id
        self.parent = parent

        self.setup_gui()
        self.setup()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        # first
        first = wx.Panel(self, -1, size=(420, 150), pos=(10, 10), style=wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL)
        first.SetBackgroundColour(core.default_background_color)

        wx.StaticText(first, -1, u"Descrição:", pos=(10, 5))
        self.textbox_description = wx.TextCtrl(first, -1, pos=(10, 25), size=(400, 30))

        wx.StaticText(first, -1, u"NCM:", pos=(10, 70))
        self.textbox_ncm = wx.TextCtrl(first, -1, pos=(10, 90), size=(60, 30))
        self.textbox_ncm.Bind(wx.EVT_CHAR, core.check_ncm)

        wx.StaticText(first, -1, u"CFOP:", pos=(100, 70))
        self.combobox_cfop = wx.ComboBox(first, -1, pos=(100, 90), size=(150, 30), style=wx.CB_READONLY)
        self.combobox_cfop.SetItems(core.cfop_optins)
        self.combobox_cfop.SetSelection(1)

        wx.StaticText(first, -1, u"Unidade de medida:", pos=(280, 70))
        self.combobox_unit = wx.ComboBox(first, -1, pos=(280, 90), size=(120, 30), style=wx.CB_READONLY)
        self.combobox_unit.SetItems(core.unit_options)
        self.combobox_unit.SetSelection(0)

        # last
        last = wx.Panel(self, -1, size=(140, 150), pos=(440, 10), style=wx.SIMPLE_BORDER)
        last.SetBackgroundColour(core.default_background_color)
        last_ = wx.Panel(last, pos=(10, 15), size=(120, 120), style=wx.SIMPLE_BORDER)
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
        if self.category_id == -1:
            return
        db = database.InventoryDB()
        data = db.categories_search_id(self.category_id)
        self.textbox_description.SetValue(data.category)
        self.textbox_ncm.SetValue(data.ncm)
        self.combobox_cfop.SetSelection(core.cfop_values.index(data.cfop))
        self.combobox_unit.SetValue(data.unit)
        db.close()

    def ask_clean(self, event):
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = self.textbox_description.GetValue()
        po = self.textbox_ncm.GetValue()
        if not pl and not po:
            self.exit(None)
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        if not string.strip(self.textbox_description.GetValue()):
            dialogs.launch_error(self, u'Nome de categoria inválido')
            return
        if len(self.textbox_ncm.GetValue()) != 8:
            dialogs.launch_error(self, u'NCM inválido: O NCM deve ter 8 dígitos')
            return
        try:
            int(self.textbox_ncm.GetValue())
        except ValueError:
            dialogs.launch_error(self, u'NCM inválido: O NCM deve conter apenas números')
            return
        dialogs.Ask(self, u'Finalizar Cadastro', 17)

    def clean(self):

        if self.category_id == -1:
            self.textbox_description.Clear()
            self.textbox_ncm.Clear()
        else:
            db = database.InventoryDB()
            data = db.categories_search_id(self.category_id)
            self.textbox_description.SetValue(data.category)
            self.textbox_ncm.SetValue(data.ncm)

    def end(self):
        ncm = self.textbox_ncm.GetValue()
        category = self.textbox_description.GetValue()
        cfop = core.cfop_values[self.combobox_cfop.GetCurrentSelection()]
        unit = core.unit_options[self.combobox_unit.GetSelection()]

        db = database.InventoryDB()

        data = data_types.CategoryData()
        data.ncm = ncm
        data.cfop = cfop
        data.unit = unit
        data.category = category
        data.ID = self.category_id

        if self.category_id == -1:
            db.insert_category(data)
        else:
            db.edit_category(data)
        db.close()
        self.clean()

        if isinstance(self.parent, inventory.ProductRegister):
            self.parent.update_categories()

        dialogs.Confirmation(self, u'Nova Categoria Cadastrada', 8)

    def exit(self, event):
        self.Close()
