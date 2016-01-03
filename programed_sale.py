#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

__author__ = 'Julio'


class ProgramedSalesManager(wx.Frame):
    def __init__(self, parent, frame_id=-1, title=u'Agendamento de vendas'):
        wx.Frame.__init__(self, parent, frame_id, title, size=(900, 430), pos=(250, 100),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.update_gui(1)
        self.Show()

    def setup_gui(self):
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO)))
        self.pilot = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.pdel = wx.gizmos.TreeListCtrl(self.pilot, -1, pos=(10, 10), size=(710, 360),
                                           style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.pdel.InsertColumn(0, u"Data", width=120)
        self.pdel.InsertColumn(1, u"", width=120)
        self.pdel.InsertColumn(2, u"Endereço", width=300)
        self.pdel.InsertColumn(3, u"Para", width=190)
        self.final = wx.Panel(self, -1, size=(140, 380), pos=(750, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        tell = wx.Button(self.final, -1, u'Mostrar mais', pos=(20, 150), size=(100, 30))
        tell.Bind(wx.EVT_BUTTON, self.open_old_sale)
        wx.StaticText(self.final, -1, u"Entregas entre:", pos=(5, 10))
        wx.StaticText(self.final, -1, "e:", pos=(5, 70))
        self.finalb = wx.Panel(self.final, pos=(10, 220), size=(120, 120), style=wx.SIMPLE_BORDER)
        ready = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png'), u"Concluída",
                                    pos=(0, 0), size=(120, 40))
        ready.Bind(wx.EVT_BUTTON, self.ready)
        up = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png'), u"Atualizar",
                                 pos=(0, 40), size=(120, 40))
        up.Bind(wx.EVT_BUTTON, self.update_gui)
        down = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png'), u'Sair',
                                   pos=(0, 80), size=(120, 40))
        down.Bind(wx.EVT_BUTTON, self.closer)

    def open_old_sale(self, event):
        red = self.pdel.GetFocusedItem()
        if red == -1:
            return
        avatar = self.pdel.GetItemText(red)
        earth = shelve.open(current_dir + '\\saves\\' + self.maresia[avatar][0] + '.txt')
        brown = earth['sales'][self.maresia[avatar][1]]['time']
        sell(self,
             mode=[(current_dir + "\\saves\\" + self.maresia[avatar][0] + '.txt'), self.maresia[avatar][1], brown],
             delmode=1)
        earth.close()

    def ready(self, event):
        red = self.pdel.GetFocusedItem()
        if red == -1:
            return
        date = self.pdel.GetItemText(red)
        tempo = self.pdel.GetItemText(red, 1)
        adr = self.pdel.GetItemText(red, 2)
        nam = self.pdel.GetItemText(red, 3)
        paco = shelve.open(current_dir + '\\saves\\deliverys.txt')
        for a in self.maresia:
            if date == self.maresia[a][1] and tempo == self.maresia[a][2] and adr == self.maresia[a][3] and nam == \
                    self.maresia[a][4]:
                tempo = str(datetime.now().hour) + ':' + str(datetime.now().minute)
                if paco[a][1]:
                    paco[a] = [date, False, tempo]
                else:
                    paco[a] = [date, True, tempo]
        paco.close()
        self.collect_delivery_data(event)

    def collect_delivery_data(self, event):
        self.pdel.DeleteAllItems()
        gas = shelve.open(current_dir + '\\saves\\deliverys.txt')
        e1 = self.alpha.GetValue()
        w1 = self.zetta.GetValue()
        earth = datetime_int(2, self.fall[self.son.index(e1)])
        water = datetime_int(2, self.fall[self.son.index(w1)])
        emax = max((earth, water))
        emin = min((earth, water))
        for i in gas:
            fire = datetime_int(2, self.maresia[i][1])
            if emin <= fire <= emax:
                tyr = self.pdel.Append((self.maresia[i][1], self.maresia[i][2], self.maresia[i][3], self.maresia[i][4]))
                if gas[i][1]:
                    self.pdel.SetItemTextColour(tyr, '#ADADAD')
        gas.close()

    def update_gui(self, event):
        today1 = datetime_int(2, str(datetime.now().year) + '-' + good_show("o", str(
            datetime.now().month)) + '-' + good_show("o", str(datetime.now().day)))
        gas = shelve.open(current_dir + '\\saves\\deliverys.txt')
        self.maresia = {}
        for i in gas:
            key = gas[i][0]
            date1, time1 = i.split()
            air = shelve.open(current_dir + '\\saves\\' + date1 + '.txt')
            adr = s_acentos(str(air['sales'][key]['city']) + ' - ' + str(air['sales'][key]['adress']))
            rec = s_acentos(r_acentos(air['sales'][key]['receiver']))
            tempo = str(air['sales'][key]['hour'])
            date = str(air['sales'][key]['date'])
            if int(date_reverse(date.replace('/', '-')).replace('-', '')) < int(
                            str(datetime.now().month) + good_show("o", str(datetime.now().day))):
                date = date + '/' + str(datetime.now().year + 1)
            else:
                date = date + '/' + str(datetime.now().year)
            self.maresia[i] = [key, date, tempo, adr, rec]
            air.close()
        water = today1
        for i in gas:
            date = self.maresia[i][1]
            fire = datetime_int(2, date)
            if fire < today1:
                g = gas
                del g[i]
                gas = g
            elif fire > water:
                water = fire
        b = today1
        self.fall = []
        while b <= water:
            self.fall.append(datetime_int(3, b))
            b += 1
        self.fall.sort()
        self.gon = []
        self.son = []
        for i in self.fall:
            self.gon.append(i)
            nert = i[8:10] + '/' + i[5:7] + '/' + i[:4]
            self.son.append(nert)
        self.alpha = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 30), style=wx.CB_READONLY)
        self.alpha.Bind(wx.EVT_COMBOBOX, self.collect_delivery_data)
        self.alpha.SetValue(self.son[0])
        self.zetta = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 90), style=wx.CB_READONLY)
        self.zetta.Bind(wx.EVT_COMBOBOX, self.collect_delivery_data)
        self.zetta.SetValue(self.son[len(self.son) - 1])
        gas.close()
        self.collect_delivery_data(event)

    def closer(self, event):
        self.Close()
