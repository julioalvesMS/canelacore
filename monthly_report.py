#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import os
import shelve
import threading
import time
from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import transactions

__author__ = 'Julio'


class Report(wx.Frame):
    month_options = []
    months_files = []
    database_incomes = {}
    database_expenses = {}
    combobox_day_displayed = None
    list_incomes = None
    list_expenses = None
    list_left = None
    list_right = None

    text_profit = None
    text_spent = None
    text_income = None
    text_wasted = None
    text_daily_income = None
    text_credit_card_income = None
    text_better_week_day = None
    text_money_income = None
    text_worst_week_day = None

    def __init__(self, parent, title=u"Resumo Mensal"):
        wx.Frame.__init__(self, parent, -1, title, size=(1200, 680),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()
        self.Show()

    def clean(self):
        self.list_left.DeleteAllItems()
        self.list_right.DeleteAllItems()

    def setup(self, event):
        rest = threading.Thread(target=self.__setup__)
        rest.daemon = True
        rest.start()

    def __setup__(self):
        self.clean()
        if not os.path.exists('saves'):
            os.mkdir('saves')
        t0 = 0.0
        t1 = 0.0
        t2 = 0.0
        t3 = 0.0
        t4 = 0.0
        t5 = 0.0
        t6 = 0.0
        t7 = ''
        t8 = ''
        count = 0
        pr = {}
        we = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for root, dirs, files in os.walk(core.directory_paths['saves']):
            if root != core.directory_paths['saves']:
                return
            for i in files:
                try:
                    if len(i) == 14 and int(i[:10].replace('-', '')) and \
                                    i[:7] == self.months_files[
                                self.month_options.index(self.combobox_day_displayed.GetValue())]:
                        s = shelve.open(core.directory_paths['saves'] + i)
                        ol = i[:10]
                        ol = ol.split('-')
                        wd = calendar.weekday(int(ol[0]), int(ol[1]), int(ol[2]))
                        for v in s['sales']:
                            k = s['sales'][v]
                            t2 += k['value']
                            if k['payment'] == u'Dinheiro':
                                t6 += k['value']
                            elif k['payment'] == u'Cartão':
                                t5 += k['value']
                            we[wd] += k['value']
                            for p in k['descriptions']:
                                if p not in pr:
                                    pr[p] = [0, 0.0]
                                pr[p][0] += k['amounts'][k['descriptions'].index(p)]
                                pr[p][1] += k['prices'][k['descriptions'].index(p)]
                        for u in s['spent']:
                            k = s['spent'][u]
                            t1 += k['value']
                        for y in s['wastes']:
                            k = s['wastes'][y]
                            t3 += k['value']
                        count += 1
                        s.close()
                    elif len(i) == 11 and int(i[:7].replace('-', '')) and i[:7] == self.months_files[
                            self.month_options.index(self.combobox_day_displayed.GetValue())]:
                        s = shelve.open(core.directory_paths['saves'] + i)
                        for v in s['winning']:
                            k = s['winning'][v]
                            t2 += k['value']
                        for u in s['spent']:
                            k = s['spent'][u]
                            t1 += k['value']
                        s.close()
                        # TODO - Arrumar as exceções. Para testar deletar a linha abaixo.Acontece quando carrega as informações da janela dessa função.
                except ValueError or KeyError:
                    pass
        pr1 = []
        pr2 = []
        lp1 = []
        lp2 = []
        for t in range(0, 11):
            m = ['', 0, 0.0]
            for w in pr:
                if pr[w][1] > m[2] and w not in pr1:
                    m = [w, pr[w][0], pr[w][1]]
            n = ['', 0, 0.0]
            for z in pr:
                if pr[z][0] > n[1] and z not in pr2:
                    n = [z, pr[z][0], pr[z][1]]
            if m[2]:
                lp1.append(m)
                pr1.append(m[0])
            if n[1]:
                lp2.append(n)
                pr2.append(n[0])
        for e in lp1:
            self.list_left.Append((e[0], e[1], core.good_show('money', e[2])))
        for f in lp2:
            self.list_right.Append((f[0], f[1], core.good_show('money', f[2])))
        t0 = (t2 - t1)
        try:
            t4 = (t2 - t1) / count
        except ZeroDivisionError:
            t4 = 0.0
        if max(we):
            t7 = core.week_days[we.index(max(we))]
        else:
            t7 = '-------'
        if min(we):
            t8 = core.week_days[we.index(min(we))]
        else:
            try:
                while not min(we):
                    we.remove(0.0)
                t8 = core.week_days[we.index(min(we))]
                if t7 == t8:
                    t8 = '-------'
            except ValueError:
                t8 = '-------'
        self.text_profit.SetValue('R$ ' + core.good_show('money', t0))
        self.text_spent.SetValue('R$ ' + core.good_show('money', t1))
        self.text_income.SetValue('R$ ' + core.good_show('money', t2))
        self.text_wasted.SetValue('R$ ' + core.good_show('money', t3))
        self.text_daily_income.SetValue('R$ ' + core.good_show('money', t4))
        self.text_credit_card_income.SetValue('R$ ' + core.good_show('money', t5))
        self.text_money_income.SetValue('R$ ' + core.good_show('money', t6))
        self.text_worst_week_day.SetValue(t7)
        self.text_better_week_day.SetValue(t8)
        self.setup_monthly_incomes(-1)
        self.setup_monthly_expenses(-1)

    def setup_gui(self):
        self.SetBackgroundColour(core.default_background_color)
        self.Centre()
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        part1 = wx.Panel(self, -1, pos=(10, 10), size=(1180, 280), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.text_profit = wx.TextCtrl(part1, -1, pos=(200, 70), size=(100, 30), style=wx.TE_READONLY)
        self.text_spent = wx.TextCtrl(part1, -1, pos=(200, 125), size=(100, 30), style=wx.TE_READONLY)
        self.text_income = wx.TextCtrl(part1, -1, pos=(200, 180), size=(100, 30), style=wx.TE_READONLY)
        self.text_wasted = wx.TextCtrl(part1, -1, pos=(200, 235), size=(100, 30), style=wx.TE_READONLY)
        self.text_daily_income = wx.TextCtrl(part1, -1, pos=(500, 15), size=(100, 30), style=wx.TE_READONLY)
        self.text_credit_card_income = wx.TextCtrl(part1, -1, pos=(500, 70), size=(100, 30), style=wx.TE_READONLY)
        self.text_money_income = wx.TextCtrl(part1, -1, pos=(500, 125), size=(100, 30), style=wx.TE_READONLY)
        self.text_worst_week_day = wx.TextCtrl(part1, -1, pos=(500, 180), size=(100, 30), style=wx.TE_READONLY)
        self.text_better_week_day = wx.TextCtrl(part1, -1, pos=(500, 235), size=(100, 30), style=wx.TE_READONLY)
        self.list_left = wx.ListCtrl(part1, -1, pos=(625, 30), size=(250, 240),
                                     style=wx.SIMPLE_BORDER | wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.list_right = wx.ListCtrl(part1, -1, pos=(900, 30), size=(250, 240),
                                      style=wx.SIMPLE_BORDER | wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.list_left.InsertColumn(0, u'Descrição')
        self.list_left.InsertColumn(1, u'Quantidade')
        self.list_left.InsertColumn(2, u'Valor')
        self.list_right.InsertColumn(3, u'Descrição')
        self.list_right.InsertColumn(4, u'Quantidade')
        self.list_right.InsertColumn(5, u'Valor')
        wx.StaticText(part1, -1, u'Mês/Ano', pos=(10, 22))
        wx.StaticText(part1, -1, u'Lucro do Mês', pos=(10, 77))
        wx.StaticText(part1, -1, u'Total Gasto', pos=(10, 132))
        wx.StaticText(part1, -1, u'Total Vendido', pos=(10, 187))
        wx.StaticText(part1, -1, u'Total Perdido', pos=(10, 242))
        wx.StaticText(part1, -1, u'Rendimento Médio por dia', pos=(310, 22))
        wx.StaticText(part1, -1, u'Total Vendido no Cartão', pos=(310, 77))
        wx.StaticText(part1, -1, u'Total Vendido em Dinheiro', pos=(310, 132))
        wx.StaticText(part1, -1, u'Dia da Semana menos rentável', pos=(310, 187))
        wx.StaticText(part1, -1, u'Dia da Semana mais rentável', pos=(310, 242))
        wx.StaticText(part1, -1, u'Produtos de Maior Redimento', pos=(625, 10)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        wx.StaticText(part1, -1, u'Produtos Mais Vendidos', pos=(900, 10)).SetFont(
            wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.text_profit.SetBackgroundColour('#C6C6C6')
        self.text_spent.SetBackgroundColour('#C6C6C6')
        self.text_income.SetBackgroundColour('#C6C6C6')
        self.text_wasted.SetBackgroundColour('#C6C6C6')
        self.text_daily_income.SetBackgroundColour('#C6C6C6')
        self.text_credit_card_income.SetBackgroundColour('#C6C6C6')
        self.text_money_income.SetBackgroundColour('#C6C6C6')
        self.text_worst_week_day.SetBackgroundColour('#C6C6C6')
        self.text_better_week_day.SetBackgroundColour('#C6C6C6')
        part2 = wx.Panel(self, -1, pos=(10, 295), size=(1180, 60), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        part21 = wx.Panel(part2, -1, pos=(10, 5), size=(620, 50), style=wx.SIMPLE_BORDER)
        part22 = wx.Panel(part2, -1, pos=(790, 5), size=(380, 50), style=wx.SIMPLE_BORDER)
        button1 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Vendas', pos=(0, 0), size=(150, 50))
        button2 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Gastos', pos=(150, 0), size=(150, 50))
        button3 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Produtos', pos=(300, 0), size=(150, 50))
        button7 = GenBitmapTextButton(part21, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Report.png', wx.BITMAP_TYPE_PNG),
                                      u'Tabela de Desperdícios', pos=(450, 0), size=(170, 50))
        button8 = GenBitmapTextButton(part2, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Recalcular', pos=(645, 5), size=(130, 50), style=wx.SIMPLE_BORDER)
        button4 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Registar Gasto', pos=(0, 0), size=(130, 50))
        button5 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Registrar Ganho', pos=(130, 0), size=(130, 50))
        button6 = GenBitmapTextButton(part22, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                      u'Observações', pos=(260, 0), size=(120, 50))
        button1.Bind(wx.EVT_BUTTON, self.open_sheets_sales)
        button2.Bind(wx.EVT_BUTTON, self.open_sheets_expenses)
        button3.Bind(wx.EVT_BUTTON, self.open_sheets_products)
        button7.Bind(wx.EVT_BUTTON, self.open_sheets_wastes)
        button8.Bind(wx.EVT_BUTTON, self.setup)
        button4.Bind(wx.EVT_BUTTON, self.open_new_monthly_expense)
        button5.Bind(wx.EVT_BUTTON, self.open_new_monthly_income)
        button6.Bind(wx.EVT_BUTTON, self.open_text_box)
        button1.SetBackgroundColour('#FFDF85')
        button2.SetBackgroundColour('#FFDF85')
        button3.SetBackgroundColour('#FFDF85')
        button7.SetBackgroundColour('#FFDF85')
        button4.SetBackgroundColour('#C2E6F8')
        button5.SetBackgroundColour('#C2E6F8')
        button6.SetBackgroundColour('#C2E6F8')

        part3 = wx.Panel(self, pos=(10, 360), size=(1180, 280), style=wx.SIMPLE_BORDER)

        part31 = wx.Panel(part3, 56, pos=(10, 5), size=(575, 260), style=wx.SUNKEN_BORDER)
        part31.SetBackgroundColour(core.default_background_color)
        self.list_incomes = wx.gizmos.TreeListCtrl(part31, -1, pos=(10, 10), size=(400, 240),
                                                   style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE |
                                                         wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_incomes.AddColumn(u"Data", width=110)
        self.list_incomes.AddColumn(u"Descrição", width=180)
        self.list_incomes.AddColumn(u"Valor", width=110)
        self.list_incomes.SetMainColumn(0)
        dr = wx.StaticText(part31, -1, u'Ganhos\nMensais', pos=(420, 10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        last_panel = wx.Panel(part31, pos=(420, 80), size=(145, 160), style=wx.SIMPLE_BORDER)

        button31 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                       u'Adicionar', pos=(0, 0), size=(145, 40))
        button32 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                       pos=(0, 40), size=(145, 40))
        button33 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                       u'Apagar', pos=(0, 80), size=(145, 40))
        button34 = GenBitmapTextButton(last_panel, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                       u'Atualizar', pos=(0, 120), size=(145, 40))
        button31.Bind(wx.EVT_BUTTON, self.open_new_monthly_income)
        button32.Bind(wx.EVT_BUTTON, self.open_edit_monthly_income)
        button33.Bind(wx.EVT_BUTTON, self.ask_delete_income)
        button34.Bind(wx.EVT_BUTTON, self.setup_monthly_incomes)

        part32 = wx.Panel(part3, 56, pos=(590, 5), size=(575, 260), style=wx.SUNKEN_BORDER)
        part32.SetBackgroundColour(core.default_background_color)
        self.list_expenses = wx.gizmos.TreeListCtrl(part32, -1, pos=(10, 10), size=(400, 240),
                                                    style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_expenses.AddColumn(u"Data", width=110)
        self.list_expenses.AddColumn(u"Descrição", width=180)
        self.list_expenses.AddColumn(u"Valor", width=110)
        self.list_expenses.SetMainColumn(0)
        dr = wx.StaticText(part32, -1, u'Gastos\nMensais', pos=(420, 10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        last_buttons = wx.Panel(part32, pos=(420, 80), size=(145, 160), style=wx.SIMPLE_BORDER)

        button41 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                       u'Adicionar', pos=(0, 0), size=(145, 40))
        button42 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                       pos=(0, 40), size=(145, 40))
        button43 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                       u'Apagar', pos=(0, 80), size=(145, 40))
        button44 = GenBitmapTextButton(last_buttons, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                       u'Atualizar', pos=(0, 120), size=(145, 40))
        button41.Bind(wx.EVT_BUTTON, self.open_new_monthly_expense)
        button42.Bind(wx.EVT_BUTTON, self.open_edit_monthly_expense)
        button43.Bind(wx.EVT_BUTTON, self.ask_delete_expense)
        button44.Bind(wx.EVT_BUTTON, self.setup_monthly_expenses)

        for root, dirs, files in os.walk("saves"):
            if root != "saves":
                break
            files.sort()
            files.reverse()
            d = str(datetime.now().year) + '-' + core.good_show('o', str(datetime.now().month))
            self.month_options.append(core.date_reverse(d).replace('-', '/'))
            self.months_files.append(d)
            for i in files:
                try:
                    if int(i[:7].replace("-", '')) and (i[:7] not in self.months_files):
                        ab = i[5:7] + "/" + i[0:4]
                        self.month_options.append(ab)
                        self.months_files.append(i[:7])
                except ValueError:
                    pass
        self.combobox_day_displayed = wx.ComboBox(part1, -1, choices=self.month_options, size=(100, 30), pos=(200, 15),
                                                  style=wx.CB_READONLY)
        self.combobox_day_displayed.Bind(wx.EVT_COMBOBOX, self.setup)
        if len(self.month_options) != 0:
            self.combobox_day_displayed.SetValue(self.month_options[0])
        self.setup(None)

    def setup_monthly_incomes(self, event):
        self.list_incomes.DeleteAllItems()
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        f = shelve.open(core.directory_paths['saves'] + month + '.txt')
        days = {}
        root = self.list_incomes.AddRoot(self.combobox_day_displayed.GetValue())
        self.list_incomes.SetItemText(root, u'Ganhos Mensais', 1)
        self.list_incomes.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        total = 0.0
        if len(f):
            for dd in f['winning']:
                i = f['winning'][dd]
                if i['date'] not in days:
                    days[i['date']] = [self.list_incomes.AppendItem(root, i['date']), 0.0]
                x = self.list_incomes.AppendItem(days[i['date']][0], i['time'][:5])
                self.list_incomes.SetItemText(x, i['description'], 1)
                self.list_incomes.SetItemText(x, 'R$ ' + core.good_show('money', i['value']), 2)
                self.database_incomes[x] = dd
                total += i['value']
                days[i['date']][1] += i['value']
            self.list_incomes.SetItemText(root, 'R$ ' + core.good_show('money', total), 2)
            for k in days:
                self.list_incomes.SetItemText(days[k][0], 'R$ ' + core.good_show('money', days[k][1]), 2)
                self.list_incomes.SetItemFont(days[k][0], wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.list_incomes.ExpandAll(root)
        f.close()

    def setup_monthly_expenses(self, event):
        self.list_expenses.DeleteAllItems()
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        f = shelve.open(core.directory_paths['saves'] + month + '.txt')
        days = {}
        root = self.list_expenses.AddRoot(self.combobox_day_displayed.GetValue())
        self.list_expenses.SetItemText(root, u'Gastos Mensais', 1)
        self.list_expenses.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        total = 0.0
        if len(f):
            for dd in f['spent']:
                i = f['spent'][dd]
                if i['date'] not in days:
                    days[i['date']] = [self.list_expenses.AppendItem(root, i['date']), 0.0]
                x = self.list_expenses.AppendItem(days[i['date']][0], i['time'][:5])
                self.list_expenses.SetItemText(x, i['description'], 1)
                self.list_expenses.SetItemText(x, 'R$ ' + core.good_show('money', i['value']), 2)
                self.database_expenses[x] = dd
                total += i['value']
                days[i['date']][1] += i['value']
            self.list_expenses.SetItemText(root, 'R$ ' + core.good_show('money', total), 2)
            for k in days:
                self.list_expenses.SetItemText(days[k][0], 'R$ ' + core.good_show('money', days[k][1]), 2)
                self.list_expenses.SetItemFont(days[k][0], wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.list_expenses.ExpandAll(root)
        f.close()

    def open_text_box(self, event):
        month = self.months_files[self.month_options.index(self.combobox_day_displayed.GetValue())]
        TextBox(self, month)

    def open_sheets_sales(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        DataSheets(self, sheet_to_focus=1, month=month)

    def open_sheets_expenses(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        DataSheets(self, sheet_to_focus=2, month=month)

    def open_sheets_products(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        DataSheets(self, sheet_to_focus=3, month=month)

    def open_sheets_wastes(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        DataSheets(self, sheet_to_focus=4, month=month)

    def open_new_monthly_expense(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        transactions.Expense(self, month=month)

    def open_edit_monthly_expense(self, event):
        red = self.list_expenses.GetSelection()
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        temporary_key = -1
        if red == self.list_expenses.GetRootItem() or self.list_expenses.GetItemParent(
                red) is self.list_expenses.GetRootItem():
            return
        for x in self.database_expenses:
            if x == red:
                temporary_key = x
                break
        key = self.database_expenses[temporary_key]
        bravo = shelve.open(core.directory_paths['saves'] + month + '.txt')
        original_hour = bravo['spent'][key]['time']
        transactions.Expense(self, u"Editar Gasto n°" + str(key), month,
                             [(core.directory_paths['saves'] + month + '.txt'), key, original_hour])
        bravo.close()

    def open_new_monthly_income(self, event):
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        transactions.Expense(self, -1, u'Ganhos', month)

    def open_edit_monthly_income(self, event):
        red = self.list_incomes.GetSelection()
        month = self.months_files[self.combobox_day_displayed.GetSelection()]
        temporary_key = -1
        if red == self.list_incomes.GetRootItem() or self.list_incomes.GetItemParent(
                red) is self.list_incomes.GetRootItem():
            return
        for x in self.database_incomes:
            if x == red:
                temporary_key = x
                break
        key = self.database_incomes[temporary_key]
        bravo = shelve.open(core.directory_paths['saves'] + month + '.txt')
        original_hour = bravo['winning'][key]['time']
        transactions.Expense(self, u"Editar Ganho n°" + str(key), month,
                             [(core.directory_paths['saves'] + month + '.txt'), key, original_hour])
        bravo.close()

    def ask_delete_income(self, event):
        boom = self.list_incomes.GetSelection()
        if boom == self.list_incomes.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Ganho", 26)

    def ask_delete_expense(self, event):
        boom = self.list_expenses.GetSelection()
        if boom == self.list_expenses.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Gasto", 22)

    def data_delete(self, box):
        temporary_key = -1
        if box == 11:
            red = self.list_incomes.GetSelection()
            month = self.months_files[self.combobox_day_displayed.GetSelection()]
            if red == self.list_incomes.GetRootItem() or self.list_incomes.GetItemParent(
                    red) is self.list_incomes.GetRootItem():
                return
            bravo = shelve.open(core.directory_paths['saves'] + month + '.txt')
            for x in self.database_incomes:
                if x == red:
                    temporary_key = x
                    break
            key = self.database_incomes[temporary_key]
            finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
            asw = bravo["edit"]
            asw[finish_time] = bravo["winning"][key]
            asw[finish_time]['key'] = key
            asw[finish_time]['sheet_to_focus'] = 2
            bravo["edit"] = asw
            hair = bravo["winning"]
            del hair[key]
            bravo["winning"] = hair
            bravo.close()
            self.setup_monthly_incomes(1)
            return
        elif box == 12:
            red = self.list_expenses.GetSelection()
            month = self.months_files[self.combobox_day_displayed.GetSelection()]
            if red == self.list_expenses.GetRootItem() or self.list_expenses.GetItemParent(
                    red) is self.list_expenses.GetRootItem():
                return
            bravo = shelve.open(core.directory_paths['saves'] + month + '.txt')
            for x in self.database_expenses:
                if x == red:
                    temporary_key = x
                    break
            key = self.database_expenses[temporary_key]
            finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
            asw = bravo["edit"]
            asw[finish_time] = bravo["spent"][key]
            asw[finish_time]['key'] = key
            asw[finish_time]['sheet_to_focus'] = 2
            bravo["edit"] = asw
            hair = bravo["spent"]
            del hair[key]
            bravo["spent"] = hair
            bravo.close()
            self.setup_monthly_expenses(1)
            return

    def exit(self, event):
        self.Close()


class TextBox(wx.Frame):
    notes_box = None
    status_bar = None

    def __init__(self, parent, month, title=u'Observações'):
        wx.Frame.__init__(self, parent, -1, title, size=(400, 300))
        self.month = month
        self.parent = parent

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetMinSize((400, 300))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        menu1 = wx.Menu()
        menu1.Append(4001, u'&Salvar\tCTRL+S')
        menu1.Append(4002, u'&Salvar uma Cópia\tCTRL+SHIFT+S')
        menu1.Append(4009, u'&Sair\tCTRL+Q')
        menu2 = wx.Menu()
        menu2.Append(4101, u'&Copiar\tCTRL+C')
        menu2.Append(4102, u'&Recortar\tCTRL+X')
        menu2.Append(4103, u'&Colar\tCTRL+V')
        menu2.Append(4104, u'&Apagar')
        menu2.AppendSeparator()
        menu2.Append(4105, u'&Selecionar Tudo\tCTRL+A')
        menu = wx.MenuBar()
        menu.Append(menu1, u'Arquivos')
        menu.Append(menu2, u'Ferramentas')
        self.SetMenuBar(menu)
        tool_bar = wx.ToolBar(self, size=(500, 50))
        tool_bar.AddSimpleTool(4501, wx.Bitmap(core.directory_paths['icons'] + 'Save.png', wx.BITMAP_TYPE_PNG), u'Salvar', '')
        tool_bar.AddSeparator()
        tool_bar.AddSimpleTool(4502, wx.Bitmap(core.directory_paths['icons'] + 'Copy.png', wx.BITMAP_TYPE_PNG), u'Copiar', '')
        tool_bar.AddSimpleTool(4503, wx.Bitmap(core.directory_paths['icons'] + 'Cut.png', wx.BITMAP_TYPE_PNG), u'Recortar', '')
        tool_bar.AddSimpleTool(4504, wx.Bitmap(core.directory_paths['icons'] + 'Paste.png', wx.BITMAP_TYPE_PNG), u'Colar', '')
        tool_bar.AddSimpleTool(4505, wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', '')
        tool_bar.AddSeparator()
        tool_bar.AddSimpleTool(4509, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG), u'Sair', '')
        self.notes_box = wx.TextCtrl(self, -1, pos=(10, 60), size=(400, 300), style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_MENU, self.save, id=4001)
        self.Bind(wx.EVT_MENU, self.save_to, id=4002)
        self.Bind(wx.EVT_MENU, self.exit, id=4009)
        self.Bind(wx.EVT_MENU, self.text_copy, id=4101)
        self.Bind(wx.EVT_MENU, self.text_cut, id=4102)
        self.Bind(wx.EVT_MENU, self.text_paste, id=4103)
        self.Bind(wx.EVT_MENU, self.text_erase, id=4104)
        self.Bind(wx.EVT_MENU, self.text_select_all, id=4105)
        self.Bind(wx.EVT_TOOL, self.save, id=4501)
        self.Bind(wx.EVT_TOOL, self.text_copy, id=4502)
        self.Bind(wx.EVT_TOOL, self.text_cut, id=4503)
        self.Bind(wx.EVT_TOOL, self.text_paste, id=4504)
        self.Bind(wx.EVT_TOOL, self.text_erase, id=4505)
        self.Bind(wx.EVT_TOOL, self.exit, id=4509)
        hsi = wx.BoxSizer(wx.VERTICAL)
        hsi.Add(tool_bar, 0, wx.EXPAND)
        hsi.Add(self.notes_box, 1, wx.EXPAND)
        self.notes_box.SetPosition(wx.Point(30, 60))
        vsi = wx.BoxSizer(wx.HORIZONTAL)
        vsi.Add(tool_bar, 1, wx.EXPAND)
        self.SetSizer(vsi)
        self.SetSizer(hsi)
        tool_bar.Realize()
        self.status_bar = self.CreateStatusBar()

    def save(self, event):
        if type(self.GetParent()) is Report:
            if self.notes_box.SaveFile(core.directory_paths['saves'] + '%s_obs.txt' % self.month):
                self.status_bar.SetStatusText(u'Observação salva com sucesso')
                time.sleep(1)
                self.status_bar.SetStatusText('')
            else:
                self.status_bar.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
                time.sleep(2)
                self.status_bar.SetStatusText('')

    def save_to(self, event):
        loc = wx.FileDialog(self, 'Salvar em', os.getcwd(), self.month + '_obs.txt', '*.*', wx.FD_SAVE)
        loc.ShowModal()
        loc.Destroy()
        if self.notes_box.SaveFile(loc.GetPath()):
            self.status_bar.SetStatusText(u'Observação salva com sucesso em %s' % loc.GetPath())
            time.sleep(1)
            self.status_bar.SetStatusText('')
        else:
            self.status_bar.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
            time.sleep(2)
            self.status_bar.SetStatusText('')

    def text_copy(self, event):
        self.notes_box.Copy()

    def text_cut(self, event):
        self.notes_box.Cut()

    def text_paste(self, event):
        self.notes_box.Paste()

    def text_select_all(self, event):
        self.notes_box.SelectAll()

    def text_erase(self, event):
        p = self.notes_box.GetSelection()
        self.notes_box.Remove(p[0], p[1])

    def exit(self, event):
        self.Close()


class DataSheets(wx.Frame):
    def __init__(self, parent, month, title=u'Tabelas', sheet_to_focus=1):
        wx.Frame.__init__(self, parent, -1, title, size=(970, 600))
        self.month = month
        self.parent = parent
        self.SetBackgroundColour(core.default_background_color)
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        box = wx.BoxSizer(wx.VERTICAL)
        note = wx.Notebook(self, style=wx.LEFT)
        if sheet_to_focus == 1:
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
        elif sheet_to_focus == 2:
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
        elif sheet_to_focus == 3:
            self.main3 = Sheet(note, 'prod')
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
        elif sheet_to_focus == 4:
            self.main4 = Sheet(note, 'was')
            self.main1 = Sheet(note, 'won')
            self.main2 = Sheet(note, 'loss')
            self.main3 = Sheet(note, 'prod')
        note.AddPage(self.main1, u'Vendas')
        note.AddPage(self.main2, u'Gastos')
        note.AddPage(self.main3, u'Produtos')
        note.AddPage(self.main4, u'Desperdícios')
        button_exit = GenBitmapTextButton(self, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                          u'Sair', pos=(600, -1), style=wx.SIMPLE_BORDER)
        button_exit.Bind(wx.EVT_BUTTON, self.exit)
        box.Add(note, 1, wx.EXPAND | wx.ALL, 5)
        box.Add(button_exit, 0, wx.ALL | wx.ALIGN_RIGHT, 15)
        self.SetSizer(box)
        note.SetSelection(sheet_to_focus - 1)

        self.Centre()
        self.Show()

    def exit(self, event):
        self.Close()


class Sheet(wx.gizmos.TreeListCtrl):
    def __init__(self, parent, content):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.content = content
        self.parent = parent.GetParent()
        prepaire = threading.Thread(target=self.setup)
        prepaire.daemon = True
        prepaire.start()
        self.Show()

    def setup(self):
        month = self.parent.month
        if self.content is 'prod':
            plist = {}
            for root, dirs, files in os.walk(core.directory_paths['saves']):
                if root is core.directory_paths['saves']:
                    for i in files:
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['sales']:
                                for x in range(0, len(s['sales'][a]['descriptions'])):
                                    key = s['sales'][a]['descriptions'][x] + '\\_/' + str(
                                        s['sales'][a]['unit_prices'][x])
                                    if key in plist:
                                        plist[key][0] += s['sales'][a]['amounts'][x]
                                        plist[key][1] += s['sales'][a]['prices'][x]
                                        plist[key][2] += 1
                                    else:
                                        plist[key] = [s['sales'][a]['amounts'][x], s['sales'][a]['prices'][x], 1]
            self.AddColumn(u'Produto', 300)
            self.AddColumn(u'Preço Unitário', 100)
            self.AddColumn(u'Quantidade vendida', 150)
            self.AddColumn(u'Quantidade de vezes vendido', 200)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Produtos Vendidos em %s' % core.date_reverse(month).replace('-', '/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a = 0.0
            b = 0
            for i in plist:
                e = i.split('\\_/')
                item = self.AppendItem(root, e[0])
                self.SetItemText(item, 'R$ ' + core.good_show('money', e[1]), 1)
                self.SetItemText(item, str(plist[i][0]), 2)
                self.SetItemText(item, str(plist[i][2]), 3)
                self.SetItemText(item, 'R$ ' + core.good_show('money', str(plist[i][1])), 4)
                a += plist[i][1]
                b += plist[i][0]
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + core.good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'won':
            wlist = []
            for root, dirs, files in os.walk(core.directory_paths['saves']):
                if root is core.directory_paths['saves']:
                    for i in files:
                        if i[:7] == month and len(i) is 11:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['winning']:
                                wlist = [[core.date_reverse(month),
                                          core.date_reverse(s['winning'][a]['date']).replace('-', '/'),
                                          s['winning'][a]['value'], '-------', s['winning'][a]['description']]] + wlist
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['sales']:
                                loo = []
                                for x in range(0, len(s['sales'][a]['descriptions'])):
                                    loo.append([s['sales'][a]['descriptions'][x], str(s['sales'][a]['amounts'][x]),
                                                str(s['sales'][a]['prices'][x])])
                                wlist.append([core.date_reverse(i[:10]), s['sales'][a]['time'], s['sales'][a]['value'],
                                              s['sales'][a]['payment'], loo])
            self.AddColumn(u'Data/Horário', 250)
            self.AddColumn(u'Forma de Pagamento', 150)
            self.AddColumn(u'Descrição', 250)
            self.AddColumn(u'Quantidade', 100)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Ganhos de %s' % core.date_reverse(month).replace('-', '/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a = 0.0
            b = 0
            days = {}
            sat = core.week_end(month)
            weeks = {}
            for i in range(0, len(wlist)):
                for pol in sat:
                    if pol >= int(wlist[i][0][:2]):
                        k = sat.index(pol) + 1
                        break
                if k not in weeks and type(wlist[i][4]) is list:
                    we = self.AppendItem(root, u'%i° Semana' % k)
                    self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                    weeks[k] = [we, 0.0, 0]
                if wlist[i][0] not in days:
                    if type(wlist[i][4]) is list:
                        item = self.AppendItem(weeks[k][0], wlist[i][0].replace('-', '/'))
                    else:
                        item = self.AppendItem(root, wlist[i][0].replace('-', '/'))
                    self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                    days[wlist[i][0]] = [item, 0.0, 0]
                boss = days[wlist[i][0]][0]
                if type(wlist[i][4]) is list:
                    x = '-----------'
                    y = str(len(wlist[i][4]))
                    weeks[k][1] += wlist[i][2]
                    weeks[k][2] += 1
                else:
                    x = wlist[i][4]
                    y = '--'
                father = self.AppendItem(boss, wlist[i][1])
                self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.SetItemText(father, wlist[i][3], 1)
                self.SetItemText(father, x, 2)
                self.SetItemText(father, y, 3)
                self.SetItemText(father, 'R$ ' + core.good_show('money', str(wlist[i][2])), 4)
                b += 1
                a += wlist[i][2]
                days[wlist[i][0]][1] += wlist[i][2]
                days[wlist[i][0]][2] += 1
                if type(wlist[i][4]) is list:
                    for z in wlist[i][4]:
                        kid = self.AppendItem(father, '-------')
                        self.SetItemText(kid, '-------', 1)
                        self.SetItemText(kid, z[0], 2)
                        self.SetItemText(kid, z[1], 3)
                        self.SetItemText(kid, 'R$ ' + core.good_show('money', str(z[2])), 4)
            for j in weeks:
                self.SetItemText(weeks[j][0], str(weeks[j][2]), 3)
                self.SetItemText(weeks[j][0], 'R$ ' + core.good_show('money', weeks[j][1]), 4)
                self.SortChildren(weeks[j][0])
            for j in days:
                self.SetItemText(days[j][0], str(days[j][2]), 3)
                self.SetItemText(days[j][0], 'R$ ' + core.good_show('money', days[j][1]), 4)
                self.SortChildren(days[j][0])
            self.SetItemText(root, str(b), 3)
            self.SetItemText(root, 'R$ ' + core.good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'loss':
            llist = []
            for root, dirs, files in os.walk(core.directory_paths['saves']):
                if root is core.directory_paths['saves']:
                    for i in files:
                        if i[:7] == month and len(i) is 11:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['spent']:
                                llist.append([core.date_reverse(i[:7]).replace('-', '/'), s['spent'][a]['time'],
                                              s['spent'][a]['value'], s['spent'][a]['description']])
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['spent']:
                                llist.append([core.date_reverse(i[:10]).replace('-', '/'), s['spent'][a]['time'],
                                              s['spent'][a]['value'], s['spent'][a]['description']])
            self.AddColumn(u'Data/Horário', 250)
            self.AddColumn(u'Descrição', 400)
            self.AddColumn(u'Quantidade', 100)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Gastos de %s' % core.date_reverse(month).replace('-', '/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a = 0.0
            b = 0
            days = {}
            sat = core.week_end(month)
            weeks = {}
            for i in range(0, len(llist)):
                for pol in sat:
                    if pol >= int(llist[i][0][:2]):
                        k = sat.index(pol) + 1
                        break
                if k not in weeks and len(llist[i][0]) == 10:
                    we = self.AppendItem(root, u'%i° Semana' % k)
                    self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                    weeks[k] = [we, 0.0, 0]
                if llist[i][0] not in days:
                    if len(llist[i][0]) == 10:
                        item = self.AppendItem(weeks[k][0], llist[i][0].replace('-', '/'))
                    else:
                        item = self.AppendItem(root, llist[i][0].replace('-', '/'))
                    self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                    days[llist[i][0]] = [item, 0.0, 0]
                boss = days[llist[i][0]][0]
                father = self.AppendItem(boss, llist[i][1])
                self.SetItemText(father, llist[i][3], 1)
                self.SetItemText(father, 'R$ ' + core.good_show('money', str(llist[i][2])), 3)
                b += 1
                a += llist[i][2]
                days[llist[i][0]][2] += 1
                days[llist[i][0]][1] += llist[i][2]
                if len(llist[i][0]) == 10:
                    weeks[k][1] += llist[i][2]
                    weeks[k][2] += 1
            for key in days:
                self.SetItemText(days[key][0], str(days[key][2]), 2)
                self.SetItemText(days[key][0], 'R$ ' + core.good_show('money', days[key][1]), 3)
                self.SortChildren(days[key][0])
            for j in weeks:
                self.SetItemText(weeks[j][0], str(weeks[j][2]), 2)
                self.SetItemText(weeks[j][0], 'R$ ' + core.good_show('money', weeks[j][1]), 3)
                self.SortChildren(weeks[j][0])
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + core.good_show('money', a), 3)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'was':
            walist = {}
            for root, dirs, files in os.walk(core.directory_paths['saves']):
                if root is core.directory_paths['saves']:
                    for i in files:
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(core.directory_paths['saves'] + i)
                            for a in s['wastes']:
                                key = s['wastes'][a]['description'] + '\\_/' + str(s['wastes'][a]['unit_price'])
                                if key in walist:
                                    walist[key][0] += s['wastes'][a]['amount']
                                    walist[key][1] += s['wastes'][a]['value']
                                    walist[key][2] += 1
                                else:
                                    walist[key] = [s['wastes'][a]['amount'], s['wastes'][a]['value'], 1]
            self.AddColumn(u'Descrição', 300)
            self.AddColumn(u'Preço Unitário', 150)
            self.AddColumn(u'Quantidade', 100)
            self.AddColumn(u'Quantidade de vezes', 200)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Desperdícios de %s' % core.date_reverse(month).replace('-', '/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a = 0.0
            b = 0
            for i in walist:
                e = i.split('\\_/')
                item = self.AppendItem(root, e[0])
                self.SetItemText(item, 'R$ ' + core.good_show('money', e[1]), 1)
                self.SetItemText(item, str(walist[i][0]), 2)
                self.SetItemText(item, str(walist[i][2]), 3)
                self.SetItemText(item, 'R$ ' + core.good_show('money', str(walist[i][1])), 4)
                a += walist[i][1]
                b += walist[i][0]
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + core.good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)
