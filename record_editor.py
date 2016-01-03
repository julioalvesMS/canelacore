#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import shutil
import threading
import time

import wx
import wx.gizmos

import core
import dialogs

__author__ = 'Julio'


class EditionManager(wx.Frame):
    combobox_day_option = None
    combobox_entry_type = None

    list_edited_data = None

    panel_control = None

    file_name = None
    dict_modified_entries = None

    days_files = None
    day_options = None

    def __init__(self, parent, title=u'Recuperação de Registros', record_date=''):
        wx.Frame.__init__(self, parent, -1, title, size=(1000, 430),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.record_date = record_date

        self.setup_gui()

        self.setup_options()
        self.setup(None)
        self.Show()

    def setup_gui(self):
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.Centre()
        self.SetBackgroundColour(core.default_background_color)
        panel_original = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.list_edited_data = wx.gizmos.TreeListCtrl(panel_original, -1, pos=(10, 10), size=(710, 360),
                                                       style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                       wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_edited_data.AddColumn(u"Horário", width=120)
        self.list_edited_data.AddColumn(u"Tipo de mud.", width=95)
        self.list_edited_data.AddColumn(u"Tipo de reg.", width=90)
        self.list_edited_data.AddColumn(u"Descrição", width=210)
        self.list_edited_data.AddColumn(u"Quantidade", width=90)
        self.list_edited_data.AddColumn(u"Valor", width=100)
        self.list_edited_data.SetMainColumn(0)
        self.panel_control = wx.Panel(self, -1, size=(240, 380), pos=(750, 10),
                                      style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        wx.StaticText(self.panel_control, -1, u"Registros de", pos=(5, 80))
        rec = wx.Button(self.panel_control, -1, u"Recuperar registro", pos=(5, 200))
        rec.Bind(wx.EVT_BUTTON, self.ask_remove)

    def setup(self, event):
        two = threading.Thread(target=self.__setup__)
        two.daemon = True
        two.start()

    def setup_options(self):
        self.day_options = []
        self.days_files = []
        for root, dirs, files in os.walk(core.directory_paths['saves']):
            if root != core.directory_paths['saves']:
                break
            files.sort()
            files.reverse()
            for i in files:
                try:
                    if len(str(int(i.replace("-", '').replace(".txt", "")))) == 8:
                        ab = i[8:10]
                        ab = ab + "/" + i[5:7]
                        ab = ab + "/" + i[0:4]
                        self.day_options.append(ab)
                        self.days_files.append(i)
                except ValueError:
                    pass
        self.combobox_day_option = wx.ComboBox(self.panel_control, -1, choices=self.day_options, size=(130, -1),
                                               pos=(5, 100), style=wx.CB_READONLY)
        self.combobox_day_option.Bind(wx.EVT_COMBOBOX, self.setup)
        self.combobox_day_option.Bind(wx.EVT_TEXT_ENTER, self.setup)
        if len(self.day_options) != 0 and self.record_date == "":
            self.combobox_day_option.SetValue(self.day_options[0])
        elif self.record_date != "":
            self.combobox_day_option.SetValue(self.record_date)
        entry_types = [u'Gastos, Vendas e Desperdícios', u'Produtos e Clientes']
        self.combobox_entry_type = wx.ComboBox(self.panel_control, choices=entry_types, size=(230, -1), pos=(5, 30),
                                               style=wx.CB_READONLY | wx.TE_MULTILINE)
        self.combobox_entry_type.SetValue(entry_types[0])
        self.combobox_entry_type.Bind(wx.EVT_COMBOBOX, self.data_update)
        self.combobox_entry_type.Bind(wx.EVT_TEXT_ENTER, self.data_update)

    def data_update(self, event):
        char = self.combobox_entry_type.GetSelection()
        if char == 0:
            self.combobox_day_option.Enable()
            self.setup(None)
        elif char == 1:
            self.combobox_day_option.Disable()
            self.setup(None)

    def __setup__(self):
        if str(self.combobox_day_option.GetValue()) != '' and self.combobox_entry_type.GetSelection() == 0:
            self.clean()
            self.file_name = self.days_files[self.day_options.index(self.combobox_day_option.GetValue())]
            day_data = shelve.open(core.directory_paths['saves'] + self.file_name)
            red = day_data["edit"]
            goal = self.list_edited_data.AddRoot(self.combobox_day_option.GetValue())
            self.list_edited_data.SetItemText(goal, u"Registros modificados", 3)
            count = 0
            for i in red:
                count += 1
                a = self.list_edited_data.AppendItem(goal, i)
                self.list_edited_data.SetItemFont(a, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
                if red[i]['mode'] == 1:
                    self.list_edited_data.SetItemText(a, u"Editado", 1)
                elif red[i]['mode'] == 2:
                    self.list_edited_data.SetItemText(a, u"Apagado", 1)
                if len(red[i]) == 6:
                    self.list_edited_data.SetItemText(a, u"Gasto", 2)
                    self.list_edited_data.SetItemText(a, red[i]['description'], 3)
                    self.list_edited_data.SetItemText(a, ("R$ " + core.good_show("money",
                                                      str(red[i]['value']).replace('.', ','))), 5)
                elif len(red[i]) == 8:
                    self.list_edited_data.SetItemText(a, u"Desperdício", 2)
                    self.list_edited_data.SetItemText(a, red[i]['description'], 3)
                    self.list_edited_data.SetItemText(a, str(red[i]['amount']), 4)
                    self.list_edited_data.SetItemText(a, ("R$ " + core.good_show("money",
                                                      str(red[i]['value']).replace('.', ','))), 5)
                else:
                    self.list_edited_data.SetItemText(a, u"Venda", 2)
                    self.list_edited_data.SetItemText(a, red[i]['time'], 3)
                    count2 = 0
                    val = 0
                    for x in red[i]['descriptions']:
                        p = red[i]['descriptions'].index(x)
                        ver = float(red[i]['prices'][p])
                        count2 += 1
                        val += ver
                        b = self.list_edited_data.AppendItem(a, "---------------")
                        self.list_edited_data.SetItemText(b, x, 3)
                        self.list_edited_data.SetItemText(b, str(red[i]['amounts'][p]), 4)
                        self.list_edited_data.SetItemText(b,
                                                          ("R$ " + core.good_show("money", str(ver)).replace('.', ',')),
                                                          5)
                    if red[i]['discount'] != 0:
                        ver = float(red[i]['discount'])
                        val -= ver
                        b = self.list_edited_data.AppendItem(a, "---------------")
                        self.list_edited_data.SetItemText(b, u'Desconto', 3)
                        self.list_edited_data.SetItemText(b,
                                                          ("R$ " + core.good_show("money", str(ver))).replace(".", ","),
                                                          5)
                    if red[i]['tax'] != 0:
                        ver = float(red[i]['tax'])
                        val += ver
                        b = self.list_edited_data.AppendItem(a, "---------------")
                        self.list_edited_data.SetItemText(b, u'Taxas adicionais', 3)
                        self.list_edited_data.SetItemText(b,
                                                          ("R$ " + core.good_show("money", str(ver))).replace(".", ","),
                                                          5)
                    self.list_edited_data.SetItemText(a, str(count2), 4)
                    self.list_edited_data.SetItemText(a, ("R$ " + core.good_show("money", str(val)).replace('.', ',')),
                                                      5)
            self.list_edited_data.SetItemText(goal, str(count), 4)
            self.list_edited_data.Expand(goal)
            self.list_edited_data.SetItemFont(goal, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            day_data.close()
        elif str(self.combobox_day_option.GetValue()) != '' and self.combobox_entry_type.GetSelection() == 1:
            self.clean()
            modified_entries = []
            for root, dirs, files in os.walk('#Trash'):
                hu = root.split('\\')
                if len(hu) == 5:
                    modified_entries.append(root)
            dict_modified_entries = {}
            for g in modified_entries:
                s = g.split('\\')
                e1 = s[4].split('_')
                e2 = e1[0].split('-')
                date = e2[2] + '/' + e2[1] + '/' + e2[0]
                pcid = s[3]
                if s[2] == 'edited':
                    done = u'Editado'
                elif s[2] == 'deleted':
                    done = u'Apagado'
                if s[1] == 'clients':
                    kind = u'Cliente'
                elif s[1] == 'products':
                    kind = u'Produto'
                if date in dict_modified_entries:
                    hj = dict_modified_entries[date]
                    hj.append([time, pcid, done, kind, g])
                    dict_modified_entries[date] = hj
                else:
                    dict_modified_entries[date] = [[time, pcid, done, kind, g]]
            root = self.list_edited_data.AddRoot(u'---------')
            self.list_edited_data.SetItemText(root, u'Registros Modificados', 3)
            self.list_edited_data.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            count = 0
            for a in dict_modified_entries:
                count2 = 0
                sec = self.list_edited_data.AppendItem(root, a)
                self.list_edited_data.SetItemFont(sec, wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
                for w in dict_modified_entries[a]:
                    count += 1
                    count2 += 1
                    ter = self.list_edited_data.AppendItem(sec, w[0])
                    self.list_edited_data.SetItemText(ter, w[3], 2)
                    self.list_edited_data.SetItemText(ter, w[2], 1)
                    self.list_edited_data.SetItemText(ter, w[1], 3)
                self.list_edited_data.SetItemText(sec, str(count2), 4)
            self.list_edited_data.SetItemText(root, str(count), 4)
            self.dict_modified_entries = dict_modified_entries
            self.list_edited_data.ExpandAll(root)

    def ask_remove(self, event):
        boom = self.list_edited_data.GetSelection()
        key2 = str(self.list_edited_data.GetItemText(boom, 0))
        if boom == self.list_edited_data.GetRootItem() or len(key2) == 10:
            return
        dialogs.Ask(self, u"Restauração", 30)

    def delete(self, event):
        boom = self.list_edited_data.GetSelection()
        atom = str(self.list_edited_data.GetItemText(boom, 2))
        key2 = str(self.list_edited_data.GetItemText(boom, 0))
        if boom == self.list_edited_data.GetRootItem() or len(key2) == 10:
            return
        if len(atom) == 0:
            boom = self.list_edited_data.GetItemParent(boom)
            atom = str(self.list_edited_data.GetItemText(boom, 2))
            key2 = str(self.list_edited_data.GetItemText(boom, 0))
        if self.combobox_entry_type.GetSelection() == 0:
            day_data = shelve.open(core.directory_paths['saves'] + self.file_name, writeback=True)
            if atom == u"Venda":
                key = day_data["edit"][key2]['key']
                tor = day_data["edit"][key2]
                del tor['mode']
                ckey = day_data['edit'][key2]['client_id']
                if ckey in os.listdir('clients'):
                    try:
                        h = shelve.open(core.directory_paths['clients'] + ckey + core.slash + ckey + '_deals.txt',
                                        writeback=True)
                        r = str(self.file_name[:10] + '_' + day_data['edit'][key2]['time'].replace(':', '-'))
                        h[r] = tor
                        h.close()
                    except KeyError:
                        shutil.rmtree(core.directory_paths['clients'] + ckey + core.slash + ckey + '_deals.txt')
                del tor['key']
                day_data["sales"][key] = tor
                hair = day_data["edit"]
                del hair[key2]
                day_data["edit"] = hair
                day_data.close()
                self.setup(1)
                return
            elif atom == u"Gasto":
                key = day_data["edit"][key2]['key']
                rt = day_data["edit"][key2]
                del rt['key']
                del rt['mode']
                day_data["spent"][key] = rt
                hair = day_data["edit"]
                del hair[key2]
                day_data["edit"] = hair
                day_data.close()
                self.setup(1)
                return
            elif atom == u"Desperdício":
                key = day_data["edit"][key2]['key']
                mn = day_data["edit"][key2]
                del mn['key']
                del mn['mode']
                day_data["wastes"][key] = mn
                hair = day_data["edit"]
                del hair[key2]
                day_data["edit"] = hair
                day_data.close()
                self.setup(1)
                return
        elif self.combobox_entry_type.GetSelection() == 1:
            for i in self.dict_modified_entries:
                for x in self.dict_modified_entries[i]:
                    if x[0] == key2:
                        s = x[4].split('\\')
                        y = s[1] + '/' + s[3]
                        if os.path.exists(y):
                            shutil.rmtree(y)
                        shutil.copytree(x[4], y)
                        shutil.rmtree(x[4])
                        self.setup(1)
                        return

    def clean(self):
        self.list_edited_data.DeleteAllItems()

    def exit(self, event):
        self.Close()
