#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
from datetime import datetime
import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton
import core
import sale

__author__ = 'Julio'


class DeliveryManager(wx.Frame):
    combobox_date_start = None
    combobox_date_finish = None
    list_deliveries = None
    panel_right = None

    date_list = None
    database_deliveries = None

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
        self.list_deliveries = wx.ListCtrl(panel_deliveries, -1, pos=(10, 10), size=(710, 360),
                                           style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.list_deliveries.InsertColumn(0, u"Data", width=120)
        self.list_deliveries.InsertColumn(1, u"Horário", width=120)
        self.list_deliveries.InsertColumn(2, u"Endereço", width=300)
        self.list_deliveries.InsertColumn(3, u"Para", width=190)
        self.panel_right = wx.Panel(self, -1, size=(140, 380), pos=(750, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        tell = wx.Button(self.panel_right, -1, u'Mostrar mais', pos=(20, 150), size=(100, 30))
        tell.Bind(wx.EVT_BUTTON, self.open_view_sale)
        wx.StaticText(self.panel_right, -1, u"Entregas entre:", pos=(5, 10))
        wx.StaticText(self.panel_right, -1, "e:", pos=(5, 70))
        panel_side_buttons = wx.Panel(self.panel_right, pos=(10, 220), size=(120, 120), style=wx.SIMPLE_BORDER)
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
        red = self.list_deliveries.GetFocusedItem()
        if red == -1:
            return
        avatar = self.list_deliveries.GetItemText(red)
        earth = shelve.open(core.directory_paths['saves'] + self.database_deliveries[avatar][0] + '.txt')
        brown = earth['sales'][self.database_deliveries[avatar][1]]['time']
        sale.Sale(self, argv=[(core.directory_paths['saves'] + self.database_deliveries[avatar][0] + '.txt'),
                              self.database_deliveries[avatar][1], brown], editable=False)
        earth.close()

    def change_delivery_status(self, event):
        red = self.list_deliveries.GetFocusedItem()
        if red == -1:
            return
        date = self.list_deliveries.GetItemText(red)
        tempo = self.list_deliveries.GetItemText(red, 1)
        adr = self.list_deliveries.GetItemText(red, 2)
        nam = self.list_deliveries.GetItemText(red, 3)
        paco = shelve.open(core.directory_paths['saves'] + 'deliveries.txt')
        for a in self.database_deliveries:
            if date == self.database_deliveries[a][1] and tempo == self.database_deliveries[a][2] and adr == \
                    self.database_deliveries[a][3] and nam == self.database_deliveries[a][4]:
                tempo = str(datetime.now().hour) + ':' + str(datetime.now().minute)
                if paco[a][1]:
                    paco[a] = [date, False, tempo]
                else:
                    paco[a] = [date, True, tempo]
        paco.close()
        self.database_update(event)

    def database_update(self, event):
        self.list_deliveries.DeleteAllItems()
        gas = shelve.open(core.directory_paths['saves'] + 'deliveries.txt')
        e1 = self.combobox_date_start.GetValue()
        w1 = self.combobox_date_finish.GetValue()
        earth = core.date2int(e1)
        water = core.date2int(w1)
        emax = max((earth, water))
        emin = min((earth, water))
        for i in gas:
            fire = core.date2int(self.database_deliveries[i][1])
            if emin <= fire <= emax:
                tyr = self.list_deliveries.Append((self.database_deliveries[i][1], self.database_deliveries[i][2],
                                                   self.database_deliveries[i][3], self.database_deliveries[i][4]))
                if gas[i][1]:
                    self.list_deliveries.SetItemTextColour(tyr, '#ADADAD')
        gas.close()

    def setup(self, event):
        today1 = core.date2int(
            str(datetime.now().year) + '-' + core.good_show("o", str(datetime.now().month)) + '-' +
            core.good_show("o", str(datetime.now().day)))
        gas = shelve.open(core.directory_paths['saves'] + 'deliveries.txt')
        self.database_deliveries = {}
        for i in gas:
            key = gas[i][0]
            date1, time1 = i.split()
            air = shelve.open(core.directory_paths['saves'] + date1 + '.txt')
            adr = (str(air['sales'][key]['city']) + ' - ' + str(air['sales'][key]['adress']))
            rec = air['sales'][key]['receiver']
            tempo = str(air['sales'][key]['hour'])
            date = str(air['sales'][key]['date'])
            if int(core.date_reverse(date.replace('/', '-')).replace('-', '')) < int(
                            str(datetime.now().month) + core.good_show("o", str(datetime.now().day))):
                date = date + '/' + str(datetime.now().year + 1)
            else:
                date = date + '/' + str(datetime.now().year)
            self.database_deliveries[i] = [key, date, tempo, adr, rec]
            air.close()
        water = today1
        for i in gas:
            date = self.database_deliveries[i][1]
            fire = core.date2int(date)
            if fire < today1:
                g = gas
                del g[i]
                gas = g
            elif fire > water:
                water = fire
        b = today1
        dates_sortable = []
        while b <= water:
            dates_sortable.append(core.int2date(b))
            b += 1
        dates_sortable.sort()
        self.date_list = []
        for i in dates_sortable:
            nert = i[8:10] + '/' + i[5:7] + '/' + i[:4]
            self.date_list.append(nert)
        self.combobox_date_start = wx.ComboBox(self.panel_right, -1, choices=self.date_list, size=(130, -1),
                                               pos=(5, 30), style=wx.CB_READONLY)
        self.combobox_date_start.Bind(wx.EVT_COMBOBOX, self.database_update)
        self.combobox_date_start.SetValue(self.date_list[0])
        self.combobox_date_finish = wx.ComboBox(self.panel_right, -1, choices=self.date_list, size=(130, -1),
                                                pos=(5, 90), style=wx.CB_READONLY)
        self.combobox_date_finish.Bind(wx.EVT_COMBOBOX, self.database_update)
        self.combobox_date_finish.SetValue(self.date_list[len(self.date_list) - 1])
        gas.close()
        self.database_update(event)

    def exit(self, event):
        self.Close()
