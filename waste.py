#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import database
import data_types

__author__ = 'Julio'


def update_inventory(data, undo=False):
    """
    Atualiza o estoque de acordo com um registro de desperdicio
    :type data: data_types.WasteData
    :type undo: bool
    :param data: dados do desperdicio
    :param undo: Caso True desfaz as mudanças causadas no BD pelo registro da perda
    :return: None
    :rtype: None
    """
    db = database.InventoryDB()

    prduct_id = data.product_ID
    amount = data.amount if undo else -data.amount

    db.update_product_stock(prduct_id, amount, sold=False)
    db.close()


class Waste(wx.Frame):
    
    textbox_description = None
    textbox_amount = None
    textbox_id = None
    textbox_product_unit = None

    list_inventory = None

    def __init__(self, parent, title=u'Desperdícios', key=-1, data=None):
        wx.Frame.__init__(self, parent, -1, title, size=(630, 280),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        self.key = key
        self.data = data

        self.setup_gui()

        self.database_inventory = database.InventoryDB(':memory:')

        if self.key != -1 or data:
            if not data:
                db = database.TransactionsDB()
                self.data = db.wastes_search_id(self.key)
                db.close()
                self.key = self.data.ID
            self.recover_waste()

        self.database_search(None)

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        # first
        first = wx.Panel(self, -1, size=(450, 230), pos=(10, 10), style=wx.SIMPLE_BORDER | wx.TAB_TRAVERSAL)
        first.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        
        self.textbox_description = wx.SearchCtrl(first, -1, pos=(10, 10), size=(430, 30))
        self.textbox_description.Bind(wx.EVT_TEXT, self.database_search)
        self.textbox_description.ShowSearchButton(True)
        self.textbox_description.SetDescriptiveText(u'Busca de produto')

        self.list_inventory = wx.ListCtrl(first, -1, pos=(10, 45), size=(430, 115),
                                          style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.list_inventory.InsertColumn(0, u'Descrição', width=230)
        self.list_inventory.InsertColumn(1, u'Estoque')
        self.list_inventory.InsertColumn(2, u'Preço')
        self.list_inventory.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.database_select)

        wx.StaticText(first, -1, u"ID: *", pos=(50, 170))
        self.textbox_id = wx.TextCtrl(first, -1, pos=(50, 190), size=(150, 30))
        self.textbox_id.Bind(wx.EVT_CHAR, core.check_number)

        wx.StaticText(first, -1, u"Quantidade: *", pos=(250, 170))
        self.textbox_amount = wx.TextCtrl(first, -1, pos=(250, 190), size=(150, 30))

        self.textbox_product_unit = wx.TextCtrl(first, -1, pos=(405, 195), size=(30, -1),
                                                style=wx.NO_BORDER | wx.TE_READONLY)
        self.textbox_product_unit.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        # last
        last = wx.Panel(self, -1, size=(140, 230), pos=(470, 10), style=wx.SIMPLE_BORDER)
        last.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        last_ = wx.Panel(last, pos=(10, 55), size=(120, 120), style=wx.SIMPLE_BORDER)
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

    def recover_waste(self):

        product = self.database_inventory.inventory_search_id(self.data.product_ID)
        category = self.database_inventory.categories_search_id(product.category_ID)
        self.textbox_id.SetValue(str(self.data.product_ID))
        self.textbox_amount.SetValue(core.format_amount_user(self.data.amount))
        self.textbox_product_unit.SetValue(category.unit)

    def ask_clean(self, event):
        """
        Confirma se o usuario quer apagar tudo
        :param event:
        :return:
        """
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = str(self.textbox_description.GetValue())
        po = str(self.textbox_id.GetValue())
        pk = str(self.textbox_amount.GetValue())
        if pl == '' and po == '0,00' and (pk == '' or pk == '0'):
            self.Close()
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        dialogs.Ask(self, u"Finalizar Registro", 13)

    def clean(self):
        self.textbox_description.Clear()
        self.textbox_id.Clear()
        self.textbox_amount.Clear()
        self.textbox_product_unit.Clear()

    def database_search(self, event):
        self.list_inventory.DeleteAllItems()
        product_list = self.database_inventory.inventory_search_description(self.textbox_description.GetValue())
        for product in product_list:
            category = self.database_inventory.categories_search_id(product.category_ID)
            item = self.list_inventory.Append((product.description,
                                               core.format_amount_user(product.amount, category.unit),
                                               core.format_cash_user(product.price, currency=True)))
            self.list_inventory.SetItemData(item, product.ID)

    def database_select(self, event):
        j = self.list_inventory.GetFocusedItem()
        unit = self.list_inventory.GetItemText(j, 1).split()[-1]
        self.textbox_id.SetValue(str(self.list_inventory.GetItemData(j)))
        self.textbox_description.SetValue(self.list_inventory.GetItemText(j, 0))
        self.textbox_product_unit.SetValue(unit)
        self.textbox_amount.SetFocus()

    def end(self):
        _product_id = self.textbox_id.GetValue()
        _amount = self.textbox_amount.GetValue()

        if not _product_id or not _amount:
            return dialogs.launch_error(self, u'Dados insuficientes!')

        date, finish_time = core.datetime_today()

        data = data_types.WasteData()
        data.product_ID = int(_product_id)
        data.amount = float(_amount)
        data.record_date = date
        data.record_time = finish_time
        data.ID = self.key

        db = database.TransactionsDB()
        if self.key != -1 or self.data:
            db.edit_waste(data)
            update_inventory(self.data, undo=True)
        else:
            db.insert_waste(data)
        db.close()

        update_inventory(data)

        self.clean()

        dialogs.Confirmation(self, u"Sucesso", 3)

    def exit(self, event):
        self.Close()
