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
from internet import imposto_122741
import exception


class CategoryManager(wx.Frame):

    list_categories = None
    textbox_filter = None
    menu = None

    def __init__(self, parent, title=u'Gerenciador de Categorias'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()
        self.setup(None)

        self.Show()

    def setup_gui(self):
        self.SetSize(wx.Size(815, 570))
        self.SetIcon((wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO)))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        # Faz o menu
        files = wx.Menu()
        files.Append(759, u'&Sair\tCtrl+Q')

        self.menu = wx.MenuBar()
        self.menu.Append(files, u'&Arquivos')
        self.SetMenuBar(self.menu)

        self.Bind(wx.EVT_MENU, self.exit, id=759)

        panel_top = wx.Panel(self, pos=(10, 10), size=(790, 100))

        panel_buttons_left = wx.Panel(panel_top, pos=(5, 40), size=(300, 40), style=wx.SIMPLE_BORDER)
        plus = GenBitmapTextButton(panel_buttons_left, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(0, 0), size=(100, 40))
        plus.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        plus.Bind(wx.EVT_BUTTON, self.open_new_category)
        edi = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(100, 0), size=(100, 40))
        edi.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_buttons_left, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                  u'Apagar', pos=(200, 0), size=(100, 40))
        era.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)

        self.textbox_filter = wx.SearchCtrl(panel_top, -1, pos=(315, 45), size=(200, 30), style=wx.TE_PROCESS_ENTER)
        self.textbox_filter.SetDescriptiveText(u'Busca')
        self.textbox_filter.Bind(wx.EVT_TEXT_ENTER, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.database_search)

        panel_buttons_right = wx.Panel(panel_top, pos=(545, 40), size=(240, 40), style=wx.SIMPLE_BORDER)
        rep = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                  u'Atualizar', pos=(0, 0), size=(120, 40))
        rep.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        rep.Bind(wx.EVT_BUTTON, self.setup)
        quir = GenBitmapTextButton(panel_buttons_right, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                   u'Sair', pos=(120, 0), size=(120, 40))
        quir.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        quir.Bind(wx.EVT_BUTTON, self.exit)

        import base
        if isinstance(self.GetParent(), base.Base):

            panel_change_type = wx.Panel(panel_top, pos=(315, 0), size=(203, 33), style=wx.SIMPLE_BORDER)
            rep = wx.Button(panel_change_type, -1, label=u'Transações', pos=(0, 0), size=(100, 30))
            rep.Bind(wx.EVT_BUTTON, self.change_data_type)
            quir = wx.Button(panel_change_type, -1, label=u'Produtos', pos=(100, 0), size=(100, 30))
            quir.Bind(wx.EVT_BUTTON, self.change_data_type)
            if isinstance(self, TransactionCategoryManager):
                rep.Disable()
            elif isinstance(self, ProductCategoryManager):
                quir.Disable()

        panel_center = wx.Panel(self, -1, pos=(10, 110), size=(790, 410))
        self.list_categories = wx.ListCtrl(panel_center, -1, pos=(5, 5), size=(780, 390),
                                           style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
        self.list_categories.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_edit)

    def setup(self, event):     # FIXME Fazer a thread fechar direito com o resto do app
        rest = threading.Thread(target=self.__setup__)
        rest.start()

    def __setup__(self):
        pass

    def database_search(self, event):
        pass

    def clean(self, event):
        self.textbox_filter.Clear()

    def open_new_category(self, event):
        pass

    def ask_delete(self, event):
        dialogs.Ask(self, u"Apagar Categoria", 27)

    def data_delete(self, event):
        pass

    def data_edit(self, event):
        pass

    def change_data_type(self, event):
        if isinstance(self, TransactionCategoryManager):
            ProductCategoryManager(self.GetParent())
            self.exit(None)
        elif isinstance(self, ProductCategoryManager):
            TransactionCategoryManager(self.GetParent())
            self.exit(None)

    def exit(self, event):
        self.Close()


class ProductCategoryManager(CategoryManager):

    def __init__(self, parent, title=u'Gerenciador de Categorias'):
        CategoryManager.__init__(self, parent, title)

    def setup_gui(self):
        CategoryManager.setup_gui(self)

        tasks = wx.Menu()

        # tasks.Append(61, u'&Buscar atualizações')
        tasks.Append(762, u'&Atualizar Impostos')
        self.menu.Append(tasks, u'&Tarefas')

        self.Bind(wx.EVT_MENU, self.atualiza_imposto_122741, id=762)

        self.list_categories.InsertColumn(1, u'ID', width=50)
        self.list_categories.InsertColumn(2, u'Categoria', width=275)
        self.list_categories.InsertColumn(3, u'NCM', width=75)
        self.list_categories.InsertColumn(4, u'CFOP', width=150)
        self.list_categories.InsertColumn(5, u'Unidade', width=100)
        self.list_categories.InsertColumn(6, u'Imposto', width=100)

    def __setup__(self):
        self.list_categories.DeleteAllItems()
        db = database.InventoryDB()
        categories = db.categories_list()
        for category in categories:
            imposto = core.format_amount_user(category.imposto_total) + u' %' if category.imposto_total is not None \
                      else u''
            self.list_categories.Append((category.ID, category.category, category.ncm,
                                         core.cfop_optins[core.cfop_values.index(category.cfop)], category.unit,
                                         imposto))
        db.close()

    def database_search(self, event):
        self.list_categories.DeleteAllItems()
        db = database.InventoryDB()
        categories = db.categories_search(event.GetEventObject().GetValue())
        for category in categories:
            imposto = core.format_amount_user(category.imposto_total) + u' %' if category.imposto_total is not None \
                      else u''
            self.list_categories.Append((category.ID, category.category, category.ncm,
                                         core.cfop_optins[core.cfop_values.index(category.cfop)], category.unit,
                                         imposto))
        db.close()

    def open_new_category(self, event):
        ProductCategoryData(self)

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
        ProductCategoryData(self, category_name, category_id)

    def atualiza_imposto_122741(self, event):
        import threading
        thread = threading.Thread(target=self.__atualiza_imposto_122741)
        thread.setDaemon(True)
        thread.start()

    def __atualiza_imposto_122741(self):
        import database
        db = database.InventoryDB()
        line = db.categories_list()
        for data in line:
            try:
                imposto_122741(data=data)
                db.edit_category_impostos(data)
            except exception.ExceptionNCM:
                continue
            except exception.ExceptionInternet:
                continue

        self.setup(None)
        db.close()


class TransactionCategoryManager(CategoryManager):

    def __init__(self, parent, title=u'Gerenciador de Categorias'):
        CategoryManager.__init__(self, parent, title)

    def setup_gui(self):
        CategoryManager.setup_gui(self)
        self.list_categories.InsertColumn(1, u'ID', width=200)
        self.list_categories.InsertColumn(2, u'Categoria', width=550)

    def __setup__(self):
        self.list_categories.DeleteAllItems()
        db = database.TransactionsDB()
        categories = db.categories_list()
        for category in categories:
            self.list_categories.Append((category.ID, category.category))
        db.close()

    def database_search(self, event):
        self.list_categories.DeleteAllItems()
        db = database.TransactionsDB()
        categories = db.categories_search(event.GetEventObject().GetValue())
        for category in categories:
            self.list_categories.Append((category.ID, category.category))
        db.close()

    def open_new_category(self, event):
        TransactionCategoryData(self)

    def data_delete(self, event):
        category_index = self.list_categories.GetFocusedItem()
        if category_index == -1:
            return
        db = database.TransactionsDB()
        category_id = self.list_categories.GetItemText(category_index, 0)
        db.delete_category(category_id)
        self.setup(None)

    def data_edit(self, event):
        category_index = self.list_categories.GetFocusedItem()
        if category_index == -1:
            return
        category_id = self.list_categories.GetItemText(category_index, 0)
        category_name = self.list_categories.GetItemText(category_index, 1)
        TransactionCategoryData(self, category_name, category_id)


class CategoryData(wx.Frame):

    textbox_description = None
    panel_data = None

    def __init__(self, parent, title='Nova Categoria', category_id=-1, data=None):
        wx.Frame.__init__(self, parent, -1, title, size=(590, 200),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.category_id = category_id
        self.data = data
        self.parent = parent

        self.setup_gui()
        self.setup()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        self.Bind(wx.EVT_TEXT_ENTER, self.ask_end)

        # first
        self.panel_data = wx.Panel(self, -1, size=(420, 150), pos=(10, 10), style=wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL)
        self.panel_data.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        # last
        last = wx.Panel(self, -1, size=(140, 150), pos=(440, 10), style=wx.SIMPLE_BORDER)
        last.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
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
        pass

    def ask_clean(self, event):
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = self.textbox_description.GetValue()
        if not pl:
            self.exit(None)
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        if self.check_valid_data():
            dialogs.Ask(self, u'Finalizar Cadastro', 17)

    def clean(self):
        pass

    def check_valid_data(self):
        pass

    def exit(self, event):
        self.Close()


class ProductCategoryData(CategoryData):

    textbox_ncm = None
    combobox_cfop = None
    combobox_unit = None

    def __init__(self, parent, title='Nova Categoria', category_id=-1, data=None):
        CategoryData.__init__(self, parent, title, category_id, data)

    def setup_gui(self):
        CategoryData.setup_gui(self)

        wx.StaticText(self.panel_data, -1, u"Descrição:", pos=(10, 5))
        self.textbox_description = wx.TextCtrl(self.panel_data, -1, pos=(10, 25), size=(400, 30),
                                               style=wx.TE_PROCESS_ENTER)

        wx.StaticText(self.panel_data, -1, u"NCM:", pos=(10, 70))
        self.textbox_ncm = wx.TextCtrl(self.panel_data, pos=(10, 90), size=(60, -1), style=wx.TE_PROCESS_ENTER)
        self.textbox_ncm.Bind(wx.EVT_TEXT_ENTER, self.ask_end)
        self.textbox_ncm.Bind(wx.EVT_CHAR, core.check_ncm)

        wx.StaticText(self.panel_data, -1, u"CFOP:", pos=(90, 70))
        self.combobox_cfop = wx.ComboBox(self.panel_data, -1, pos=(90, 90), size=(170, 30),
                                         style=wx.TE_PROCESS_ENTER | wx.CB_READONLY)
        self.combobox_cfop.SetItems(core.cfop_optins)
        self.combobox_cfop.SetSelection(1)

        wx.StaticText(self.panel_data, -1, u"Unidade de medida:", pos=(280, 70))
        self.combobox_unit = wx.ComboBox(self.panel_data, -1, pos=(280, 90), size=(120, 30),
                                         style=wx.TE_PROCESS_ENTER | wx.CB_READONLY)
        self.combobox_unit.SetItems(core.unit_options)
        self.combobox_unit.SetSelection(0)

    def setup(self):
        if self.data:
            self.category_id = self.data.ID
        elif self.category_id != -1:
            db = database.InventoryDB()
            self.data = db.categories_search_id(self.category_id)
            db.close()
        else:
            return
        self.textbox_description.SetValue(self.data.category)
        self.textbox_ncm.SetValue(self.data.ncm)
        self.combobox_cfop.SetSelection(core.cfop_values.index(self.data.cfop))
        self.combobox_unit.SetValue(self.data.unit)

    def check_valid_data(self):
        if not string.strip(self.textbox_description.GetValue()):
            return dialogs.launch_error(self, u'Nome de categoria inválido')
        if len(self.textbox_ncm.GetValue()) != 8:
            return dialogs.launch_error(self, u'NCM inválido: O NCM deve ter 8 dígitos')
        try:
            int(self.textbox_ncm.GetValue())
        except ValueError:
            return dialogs.launch_error(self, u'NCM inválido: O NCM deve conter apenas números')
        return True

    def clean(self):

        if not self.data:
            self.textbox_description.Clear()
            self.textbox_ncm.Clear()
        else:
            self.textbox_description.SetValue(self.data.category)
            self.textbox_ncm.SetValue(self.data.ncm)

    def end(self):
        ncm = self.textbox_ncm.GetValue()
        category = self.textbox_description.GetValue()
        cfop = core.cfop_values[self.combobox_cfop.GetCurrentSelection()]
        unit = core.unit_options[self.combobox_unit.GetSelection()]

        db = database.InventoryDB()

        data = data_types.ProductCategoryData()
        data.ncm = ncm
        data.cfop = cfop
        data.unit = unit
        data.category = category
        data.ID = self.category_id

        if self.category_id == -1:
            db.insert_category(data)
        else:
            db.edit_category(data)

        try:
            imposto_122741(data=data, origin=self)
            db.edit_category_impostos(data)
        except exception.ExceptionNCM:
            db.close()
            self.data = data
            self.category_id = data.ID
            self.setup()
            return
        except exception.ExceptionInternet:
            pass

        db.close()

        if isinstance(self.parent, inventory.ProductData):
            self.parent.update_categories()

        if self.data:
            if isinstance(self.parent, ProductCategoryManager):
                self.parent.setup(None)
            self.exit(None)
            return

        self.clean()
        dialogs.Confirmation(self, u'Nova Categoria Cadastrada', 8)


class TransactionCategoryData(CategoryData):

    def __init__(self, parent, title='Nova Categoria', category_id=-1, data=None):
        CategoryData.__init__(self, parent, title, category_id, data)

    def setup_gui(self):
        CategoryData.setup_gui(self)
        wx.StaticText(self.panel_data, -1, u"Descrição:", pos=(10, 40))
        self.textbox_description = wx.TextCtrl(self.panel_data, -1, pos=(10, 60), size=(400, 30),
                                               style=wx.TE_PROCESS_ENTER)

    def setup(self):
        if self.data:
            self.category_id = self.data.ID
        elif self.category_id != -1:
            db = database.TransactionsDB()
            self.data = db.categories_search_id(self.category_id)
            db.close()
        else:
            return
        self.textbox_description.SetValue(self.data.category)

    def check_valid_data(self):
        if not string.strip(self.textbox_description.GetValue()):
            return dialogs.launch_error(self, u'Nome de categoria inválido')
        return True

    def clean(self):

        if not self.data:
            self.textbox_description.Clear()
        else:
            self.textbox_description.SetValue(self.data.category)

    def end(self):
        category = self.textbox_description.GetValue()

        db = database.TransactionsDB()

        data = data_types.TransactionCategoryData()
        data.category = category
        data.ID = self.category_id

        if self.category_id == -1:
            db.insert_category(data)
        else:
            db.edit_category(data)
        db.close()
        import transaction
        import expense
        if isinstance(self.parent, transaction.Transaction):
            self.parent.update_categories()
        if isinstance(self.parent, expense.Expense):
            self.parent.update_categories()
        if isinstance(self.parent, CategoryManager):
            self.parent.setup(None)

        if self.data:
            self.exit(None)
            return

        self.clean()
        dialogs.Confirmation(self, u'Nova Categoria Cadastrada', 8)
