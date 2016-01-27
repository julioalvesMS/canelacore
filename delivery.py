#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import sale
import database
import data_types

__author__ = 'Julio'


class DeliveryManager(wx.Frame):

    list_deliveries = None
    combobox_show_option = None

    def __init__(self, parent, frame_id=-1, title=u'Sistema de entregas'):
        wx.Frame.__init__(self, parent, frame_id, title, size=(900, 430), pos=(250, 100),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()
        self.setup(None)

        self.Show()

    def setup_gui(self):
        self.SetBackgroundColour(core.default_background_color)
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        panel_deliveries = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)

        self.list_deliveries = wx.gizmos.TreeListCtrl(panel_deliveries, -1, pos=(10, 10), size=(710, 360),
                                                      style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                      wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_deliveries.AddColumn(u"Data", width=120)
        self.list_deliveries.AddColumn(u"Horário", width=120)
        self.list_deliveries.AddColumn(u"Endereço", width=300)
        self.list_deliveries.AddColumn(u"Para", width=160)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.open_view_sale, self.list_deliveries)

        panel_right = wx.Panel(self, -1, size=(140, 380), pos=(750, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)

        show_options = [u'Apenas entregas ativas', u'Todas as entregas cadastradas']

        self.combobox_show_option = wx.ComboBox(panel_right, choices=show_options, size=(130, -1), pos=(5, 90),
                                                style=wx.CB_READONLY | wx.TE_MULTILINE)
        self.combobox_show_option.SetValue(show_options[0])
        self.combobox_show_option.Bind(wx.EVT_COMBOBOX, self.setup)

        tell = wx.Button(panel_right, -1, u'Mostrar mais', pos=(20, 150), size=(100, 30))
        tell.Bind(wx.EVT_BUTTON, self.open_view_sale)

        panel_side_buttons = wx.Panel(panel_right, pos=(10, 220), size=(120, 120), style=wx.SIMPLE_BORDER)
        change_delivery_status = GenBitmapTextButton(panel_side_buttons, -1,
                                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png'),
                                                     u"Concluída", pos=(0, 0), size=(120, 40))
        change_delivery_status.Bind(wx.EVT_BUTTON, self.change_delivery_status)
        up = GenBitmapTextButton(panel_side_buttons, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                 u"Atualizar", pos=(0, 40), size=(120, 40))
        up.Bind(wx.EVT_BUTTON, self.setup)
        down = GenBitmapTextButton(panel_side_buttons, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                   u'Sair', pos=(0, 80), size=(120, 40))
        down.Bind(wx.EVT_BUTTON, self.exit)

    def open_view_sale(self, event):
        red = self.list_deliveries.GetSelection()
        if self.list_deliveries.GetRootItem() == red:
            event.Skip()
            return
        data = self.list_deliveries.GetItemData(red)
        if not data:
            event.Skip()
            return
        delivery_data = data.GetData()
        if not isinstance(delivery_data, data_types.DeliveryData):
            event.Skip()
            return

        sale.Sale(self, key=delivery_data.sale_ID, delivery_id=delivery_data.ID, editable=False)

    def change_delivery_status(self, event):
        red = self.list_deliveries.GetSelection()
        if self.list_deliveries.GetRootItem() == red:
            event.Skip()
            return
        data = self.list_deliveries.GetItemData(red)
        if not data:
            event.Skip()
            return
        delivery_data = data.GetData()
        if not isinstance(delivery_data, data_types.DeliveryData):
            event.Skip()
            return

        delivery_data.active = not delivery_data.active

        deliveries_db = database.DeliveriesDB()
        deliveries_db.delivery_activity_change(delivery_data.ID, delivery_data.active)
        deliveries_db.close()

        if not delivery_data.active:
            self.list_deliveries.SetItemTextColour(red, '#ADADAD')
        else:
            self.list_deliveries.SetItemTextColour(red, wx.BLACK)

    def setup(self, event):
        date_today = core.datetime_today()[0]

        show_all = True if self.combobox_show_option.GetSelection() else False

        deliveries_db = database.DeliveriesDB()
        database_deliveries = deliveries_db.deliveries_list(show_all=show_all)
        deliveries_dates = dict()

        date_today_int = core.date2int(date_today)
        for delivery in database_deliveries:
            date_delivery_int = core.date2int(delivery.date)

            if date_delivery_int < date_today_int:
                deliveries_db.delivery_activity_change(delivery.ID, False)
                continue
            if delivery.date not in deliveries_dates:
                deliveries_dates[delivery.date] = []
            deliveries_dates[delivery.date].append(delivery)

        deliveries_db.close()

        self.list_deliveries.DeleteAllItems()

        root = self.list_deliveries.AddRoot(u"--------")
        self.list_deliveries.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        amount = 0

        for date in deliveries_dates:
            date_item = self.list_deliveries.AppendItem(root, date)
            self.list_deliveries.SetItemFont(date_item, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            counter = 0
            active = False
            for delivery in deliveries_dates[date]:
                counter += 1

                a = self.list_deliveries.AppendItem(date_item, delivery.date)
                self.list_deliveries.SetItemText(a, delivery.hour, 1)
                self.list_deliveries.SetItemText(a, delivery.city + ', ' + delivery.address, 2)
                self.list_deliveries.SetItemText(a, delivery.receiver, 3)

                self.list_deliveries.SetItemData(a, wx.TreeItemData(delivery))
                if not delivery.active:
                    self.list_deliveries.SetItemTextColour(a, '#ADADAD')
                else:
                    active = True

            text = u' Entrega'
            text = text + u's' if counter > 1 else text
            self.list_deliveries.SetItemText(date_item, str(counter) + text, 2)
            if not active:
                self.list_deliveries.SetItemTextColour(date_item, '#ADADAD')
            amount += counter
        if not show_all:
            text = u' ENTREGA PROGRAMADA'
        else:
            text = u' ENTREGA REGISTRADA'
        text = text[:8] + u'S' + text[8:] + u'S' if amount > 1 else text
        amount_str = str(amount) if amount > 0 else u'NENHUMA'
        self.list_deliveries.SetItemText(root, amount_str + text, 2)
        self.list_deliveries.ExpandAll(root)

    def exit(self, event):
        self.Close()
