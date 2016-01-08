#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import threading
from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import record_editor
import sale
import transactions
import waste

__author__ = 'Julio'


class Report(wx.Frame):

    panel_top = None
    combobox_day_option = None

    textbox_day_total = None
    textbox_sales_value = None
    textbox_sales_amount = None
    textbox_money_value = None
    textbox_money_amount = None
    textbox_card_value = None
    textbox_card_amount = None
    textbox_spent_value = None
    textbox_spent_amount = None
    textbox_cash_previous = None
    textbox_cash_ideal = None
    textbox_cash_real = None
    textbox_cash_tomorrow = None
    textbox_cash_removed = None

    list_sales = None
    list_expenses = None
    list_wastes = None

    month_options = None
    months_files = None

    available_lists = None

    day_file = ''

    def __init__(self, parent, title=u'Fechamento de Caixa'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup(None)

        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(75, 0))
        self.SetSize(wx.Size(1240, 720))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        # first
        self.panel_top = wx.Panel(self, -1, pos=(10, 5), size=(1220, 50), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.panel_top.SetBackgroundColour(core.default_background_color)
        wx.StaticText(self.panel_top, -1, u"Fechamento de:", pos=(500, 15))
        self.setup_options()
        fupdate = GenBitmapTextButton(self.panel_top, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Atualizar janela', pos=(750, 5), size=(140, 40))
        fupdate.Bind(wx.EVT_BUTTON, self.reopen)
        pol = wx.Button(self.panel_top, -1, u"Recuperação de registros", pos=(900, 5), size=(-1, 40))
        pol.Bind(wx.EVT_BUTTON, self.open_record_editor)
        # Painel das vendas
        panel1 = wx.Panel(self, -1, pos=(10, 65), size=(810, 260), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel1.SetBackgroundColour(core.default_background_color)
        self.list_sales = wx.gizmos.TreeListCtrl(panel1, -1, pos=(10, 5), size=(620, 250),
                                                 style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_sales.AddColumn(u"Descrição", width=250)
        self.list_sales.AddColumn(u"Quantidade")
        self.list_sales.AddColumn(u"Pagamento", width=150)
        self.list_sales.AddColumn(u"Valor", width=120)
        self.list_sales.SetMainColumn(0)
        panel1b = wx.Panel(panel1, pos=(650, 50), size=(145, 160), style=wx.SIMPLE_BORDER)
        plus = GenBitmapTextButton(panel1b, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                   u"Nova venda",
                                   pos=(0, 0), size=(145, 40))
        plus.Bind(wx.EVT_BUTTON, self.open_new_sale)
        edit = GenBitmapTextButton(panel1b, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                   u"Editar venda", pos=(0, 40), size=(145, 40))
        edit.Bind(wx.EVT_BUTTON, self.open_edit_sale)
        remove = GenBitmapTextButton(panel1b, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                     u'Apagar venda', pos=(0, 80), size=(145, 40))
        remove.Bind(wx.EVT_BUTTON, self.ask_delete_sale)
        update = GenBitmapTextButton(panel1b, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                     u'Atualizar', pos=(0, 120), size=(145, 40))
        update.Bind(wx.EVT_BUTTON, self.setup)
        # Painel dos gastos
        panel2 = wx.Panel(self, 53, pos=(10, 335), size=(810, 170), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel2.SetBackgroundColour(core.default_background_color)
        self.list_expenses = wx.gizmos.TreeListCtrl(panel2, -1, pos=(10, 5), size=(620, 160),
                                                    style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_expenses.AddColumn(u"Data/Horário", width=130)
        self.list_expenses.AddColumn(u"Descrição", width=280)
        self.list_expenses.AddColumn(u"Quantidade", width=100)
        self.list_expenses.AddColumn(u"Valor", width=110)
        self.list_expenses.SetMainColumn(0)
        panel2b = wx.Panel(panel2, pos=(650, 5), size=(145, 160), style=wx.SIMPLE_BORDER)
        splus = GenBitmapTextButton(panel2b, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                    u'Adicionar gasto', pos=(0, 0), size=(145, 40))
        splus.Bind(wx.EVT_BUTTON, self.open_new_expense)
        sedit = GenBitmapTextButton(panel2b, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                    u'Editar gasto', pos=(0, 40), size=(145, 40))
        sedit.Bind(wx.EVT_BUTTON, self.open_edit_expense)
        sremove = GenBitmapTextButton(panel2b, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                      u'Apagar gasto', pos=(0, 80), size=(145, 40))
        sremove.Bind(wx.EVT_BUTTON, self.ask_delete_expense)
        supdate = GenBitmapTextButton(panel2b, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Atualizar', pos=(0, 120), size=(145, 40))
        supdate.Bind(wx.EVT_BUTTON, self.setup)

        # Painel dos desperdicios
        panel_last = wx.Panel(self, 56, pos=(10, 515), size=(810, 170), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel_last.SetBackgroundColour(core.default_background_color)
        self.list_wastes = wx.gizmos.TreeListCtrl(panel_last, -1, pos=(10, 5), size=(620, 160),
                                                  style=wx.SIMPLE_BORDER | wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.list_wastes.AddColumn(u"Descrição", width=280)
        self.list_wastes.AddColumn(u"Quantidade", width=100)
        self.list_wastes.AddColumn(u"Valor", width=110)
        self.list_wastes.SetMainColumn(0)
        panel_last_buttons = wx.Panel(panel_last, pos=(650, 5), size=(145, 160), style=wx.SIMPLE_BORDER)
        wplus = GenBitmapTextButton(panel_last_buttons, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Add.png', wx.BITMAP_TYPE_PNG),
                                    u'Adicionar registro', pos=(0, 0), size=(145, 40))
        wplus.Bind(wx.EVT_BUTTON, self.open_new_waste)
        wedit = GenBitmapTextButton(panel_last_buttons, -1,
                                    wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                    u'Editar registro', pos=(0, 40), size=(145, 40))
        wedit.Bind(wx.EVT_BUTTON, self.open_edit_waste)
        wremove = GenBitmapTextButton(panel_last_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                                      u'Apagar registro', pos=(0, 80), size=(145, 40))
        wremove.Bind(wx.EVT_BUTTON, self.ask_delete_waste)
        wupdate = GenBitmapTextButton(panel_last_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      'Atualizar', pos=(0, 120), size=(145, 40))
        wupdate.Bind(wx.EVT_BUTTON, self.setup, wupdate)

        self.available_lists = [self.list_sales, self.list_expenses, self.list_wastes]

        # Painel com o resulmo do dia
        panel3 = wx.Panel(self, 54, pos=(830, 65), size=(400, 620), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        panel3.SetBackgroundColour(core.default_background_color)
        part1 = wx.Panel(panel3, -1, pos=(5, 50), size=(390, 265), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        part2 = wx.Panel(panel3, -1, pos=(5, 320), size=(390, 85), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        part3 = wx.Panel(panel3, -1, pos=(5, 410), size=(390, 200), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)

        static_money_texts = []
        static_number_texts = []

        self.textbox_day_total = wx.TextCtrl(panel3, -1, "0,00", pos=(315, 10), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_sales_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 5), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_sales_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 50), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_money_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 95), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_money_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 140), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_card_value = wx.TextCtrl(part1, -1, "0,00", pos=(310, 185), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_card_amount = wx.TextCtrl(part1, -1, "0", pos=(310, 230), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_spent_value = wx.TextCtrl(part2, -1, "0,00", pos=(310, 5), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_spent_amount = wx.TextCtrl(part2, -1, "0", pos=(310, 50), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_previous = wx.TextCtrl(part3, -1, "0,00", pos=(310, 5), size=(70, 30))
        self.textbox_cash_ideal = wx.TextCtrl(part3, -1, "0,00", pos=(310, 45), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_real = wx.TextCtrl(part3, -1, "0,00", pos=(310, 85), size=(70, 30))
        self.textbox_cash_tomorrow = wx.TextCtrl(part3, -1, "0,00", pos=(310, 125), size=(70, 30), style=wx.TE_READONLY)
        self.textbox_cash_removed = wx.TextCtrl(part3, -1, "0,00", pos=(310, 165), size=(70, 30))

        self.textbox_day_total.SetBackgroundColour(core.default_disabled_color)
        self.textbox_sales_value.SetBackgroundColour(core.default_disabled_color)
        self.textbox_sales_amount.SetBackgroundColour(core.default_disabled_color)
        self.textbox_money_value.SetBackgroundColour(core.default_disabled_color)
        self.textbox_money_amount.SetBackgroundColour(core.default_disabled_color)
        self.textbox_card_value.SetBackgroundColour(core.default_disabled_color)
        self.textbox_card_amount.SetBackgroundColour(core.default_disabled_color)
        self.textbox_spent_value.SetBackgroundColour(core.default_disabled_color)
        self.textbox_spent_amount.SetBackgroundColour(core.default_disabled_color)
        self.textbox_cash_ideal.SetBackgroundColour(core.default_disabled_color)
        self.textbox_cash_tomorrow.SetBackgroundColour(core.default_disabled_color)

        static_money_texts.append(wx.StaticText(panel3, -1, u"Total do dia", pos=(10, 17)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das Vendas", pos=(5, 12)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas", pos=(5, 57)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das vendas em dinheiro", pos=(5, 102)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas em dinheiro", pos=(5, 147)))
        static_money_texts.append(wx.StaticText(part1, -1, u"Total das vendas no cartão", pos=(5, 192)))
        static_number_texts.append(wx.StaticText(part1, -1, u"Quantidade de vendas no cartão", pos=(5, 237)))
        static_money_texts.append(wx.StaticText(part2, -1, u"Total de gastos", pos=(5, 12)))
        static_number_texts.append(wx.StaticText(part2, -1, u"Quantidade de gastos", pos=(5, 57)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa do dia anterior", pos=(5, 12)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa ideal", pos=(5, 52)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa real", pos=(5, 92)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Caixa de amanhã", pos=(5, 132)))
        static_money_texts.append(wx.StaticText(part3, -1, u"Dinheiro retirado", pos=(5, 172)))
        self.textbox_cash_previous.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_cash_real.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_cash_removed.Bind(wx.EVT_CHAR, core.check_money)

        # Adiciona os pontos em cada linha com os numeros a direita para facilitar a leitura
        mon = self.GetTextExtent('R$')[0]
        dot = self.GetTextExtent('.')[0]
        space = 302
        for box in static_money_texts:
            wid = box.GetSize()[0]
            post = box.GetPosition()[1]
            free = space - wid
            if box in static_number_texts:
                dots = free // dot
                wx.StaticText(box.GetParent(), -1, '.' * dots, pos=(5 + wid, post))
            else:
                free = free - mon
                dots = free // dot
                if box is static_money_texts[0]:
                    wx.StaticText(box.GetParent(), -1, '.' * dots + 'R$', pos=(10 + wid, post))
                else:
                    wx.StaticText(box.GetParent(), -1, '.' * dots + 'R$', pos=(5 + wid, post))

    def ask_delete_sale(self, event):
        boom = self.list_sales.GetSelection()
        if boom == self.list_sales.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Venda", 21)

    def ask_delete_expense(self, event):
        boom = self.list_expenses.GetSelection()
        if boom == self.list_expenses.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Gasto", 22)

    def ask_delete_waste(self, event):
        boom = self.list_wastes.GetSelection()
        if boom == self.list_wastes.GetRootItem():
            return
        dialogs.Ask(self, u"Apagar Registro", 23)

    def delete(self, box):
        boom = box.GetSelection()
        atom = box.GetItemText(boom, 0)
        if boom == box.GetRootItem():
            return
        if len(str(atom)) != 8 and box == self.list_sales:
            boom = box.GetItemParent(boom)
            atom = box.GetItemText(boom, 0)
        day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
        if box == self.list_sales:
            for i in day_data["sales"]:
                if day_data["sales"][i]['time'] == atom:
                    ckey = day_data['sales'][i]['client_id']
                    if ckey in os.listdir('clients'):
                        try:
                            h = shelve.open(core.directory_paths['clients'] + ckey + core.slash + ckey + '_deals.txt')
                            r = str(self.day_file[:10] + '_' + day_data['sales'][i]['time'].replace(':', '-'))
                            del h[r]
                            h.close()
                        except:
                            pass
                    finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                        datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
                    asw = day_data["edit"]
                    asw[finish_time] = day_data["sales"][i]
                    asw[finish_time]['key'] = i
                    asw[finish_time]['mode'] = 2
                    day_data["edit"] = asw
                    hair = day_data["sales"]
                    del hair[i]
                    day_data["sales"] = hair
                    day_data.close()
                    self.setup(None)
                    return
        elif box == self.list_expenses:
            for i in day_data["spent"]:
                if day_data["spent"][i]['time'] == atom:
                    finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                        datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
                    asw = day_data["edit"]
                    asw[finish_time] = day_data["spent"][i]
                    asw[finish_time]['key'] = i
                    asw[finish_time]['mode'] = 2
                    day_data["edit"] = asw
                    hair = day_data["spent"]
                    del hair[i]
                    day_data["spent"] = hair
                    day_data.close()
                    self.setup(None)
                    return
        elif box == self.list_wastes:
            for i in day_data["wastes"]:
                neutron = int(box.GetItemText(boom, 1))
                proton = float(box.GetItemText(boom, 2).replace('R$ ', '').replace(',', '.'))
                if (day_data["wastes"][i]['description']) == atom and day_data["wastes"][i][
                    'amount'] == neutron and day_data["wastes"][i]['value'] == proton:
                    finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
                        datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
                    asw = day_data["edit"]
                    asw[finish_time] = day_data["wastes"][i]
                    asw[finish_time]['key'] = i
                    asw[finish_time]['mode'] = 2
                    day_data["edit"] = asw
                    hair = day_data["wastes"]
                    del hair[i]
                    day_data["wastes"] = hair
                    day_data.close()
                    self.setup(-1)
                    return

    def setup_options(self):
        self.month_options = []
        self.months_files = []
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
                        self.month_options.append(ab)
                        self.months_files.append(i)
                except ValueError or IndexError:
                    pass
        self.combobox_day_option = wx.ComboBox(self.panel_top, -1, choices=self.month_options, size=(130, -1),
                                               pos=(600, 10),
                                               style=wx.CB_READONLY)
        self.combobox_day_option.Bind(wx.EVT_COMBOBOX, self.setup)
        if len(self.month_options) != 0:
            self.combobox_day_option.SetSelection(0)

    def setup(self, event): # TODO Fazer a thread fechar direito com o resto do app
        self.combobox_day_option.Disable()
        rest = threading.Thread(target=self.__setup__)
        rest.start()

    def __setup__(self):
        if self.combobox_day_option.GetValue() != u'':
            self.clean()
            self.day_file = self.months_files[self.combobox_day_option.GetCurrentSelection()]
            day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
            root = self.list_sales.AddRoot("Vendas de " + self.combobox_day_option.GetValue())
            self.list_sales.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            sales_value = 0.0
            sales_amount = 0
            money_value = 0.00
            money_amount = 0
            card_value = 0.00
            card_amount = 0
            for i in day_data["sales"]:
                sales_value += float(day_data["sales"][i]['value'])
                sold = self.list_sales.AppendItem(root, day_data["sales"][i]['time'])
                self.list_sales.SetItemText(sold, day_data["sales"][i]['payment'], 2)
                self.list_sales.SetItemText(sold, ("R$ " + core.good_show("money", str(day_data["sales"][i]['value']))),
                                            3)
                self.list_sales.SetItemFont(sold, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                try:
                    for n in range(0, len(day_data["sales"][i]['descriptions'])):
                        pan = (day_data["sales"][i]['descriptions'][n])
                        a = self.list_sales.AppendItem(sold, pan)
                        self.list_sales.SetItemText(a, str(day_data["sales"][i]['amounts'][n]), 1)
                        self.list_sales.SetItemText(a, (
                            "R$ " + core.good_show("money", str(day_data["sales"][i]['prices'][n]))).replace(".", ","),
                                                    3)
                except ValueError:
                    pass
                if day_data["sales"][i]['discount'] != 0:
                    web = self.list_sales.AppendItem(sold, u"Desconto")
                    self.list_sales.SetItemText(web, (
                        "R$ " + core.good_show("money", str(day_data["sales"][i]['discount']))).replace(".", ","), 3)
                if day_data["sales"][i]['tax'] != 0:
                    bew = self.list_sales.AppendItem(sold, u"Taxas adicionais")
                    self.list_sales.SetItemText(bew,
                                                ("R$ " + core.good_show("money",
                                                                        str(day_data["sales"][i]['tax']))).replace(".",
                                                                                                                   ","),
                                                3)
                sales_amount += 1
                if day_data["sales"][i]['payment'] == u"Dinheiro":
                    money_amount += 1
                    money_value += float(day_data["sales"][i]['value'])
                elif day_data["sales"][i]['payment'] == u"Cartão":
                    card_amount += 1
                    card_value += float(day_data["sales"][i]['value'])

            self.list_sales.SetItemText(root, str(sales_amount), 1)
            self.list_sales.SetItemText(root, ("R$ " + core.good_show("money", str(sales_value))).replace(".", ","), 3)
            self.list_sales.Expand(root)

            raz = self.list_expenses.AddRoot(self.combobox_day_option.GetValue())
            expenses_value = 0.0
            expenses_amount = 0
            self.list_expenses.SetItemFont(raz, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            for i in day_data["spent"]:
                hour = day_data["spent"][i]['time']
                val = float(day_data["spent"][i]['value'])
                des = (day_data["spent"][i]['description'])
                expenses_amount += 1
                expenses_value += val
                golf = self.list_expenses.AppendItem(raz, hour)
                self.list_expenses.SetItemText(golf, des, 1)
                self.list_expenses.SetItemText(golf, ("R$ " + core.good_show("money", str(val))).replace(".", ","), 3)
            self.list_expenses.SetItemText(raz, "Gastos", 1)
            self.list_expenses.SetItemText(raz, str(expenses_amount), 2)
            self.list_expenses.SetItemText(raz,
                                           ("R$ " + core.good_show("money", str(expenses_value))).replace(".", ","), 3)
            self.list_expenses.Expand(raz)

            pain = self.list_wastes.AddRoot(u"Desperdícios de " + str(self.combobox_day_option.GetValue()))
            wastes_value = 0.0
            wastes_amount = 0
            self.list_wastes.SetItemFont(pain, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            for i in day_data["wastes"]:
                amt = int(day_data["wastes"][i]['amount'])
                valo = float(day_data["wastes"][i]['unit_price']) * amt
                desc = (day_data["wastes"][i]['description'])
                wastes_amount += 1
                wastes_value += valo
                king = self.list_wastes.AppendItem(pain, desc)
                self.list_wastes.SetItemText(king, str(amt), 1)
                self.list_wastes.SetItemText(king, ("R$ " + core.good_show("money", str(valo))).replace(".", ","), 2)
            self.list_wastes.SetItemText(pain, str(wastes_amount), 1)
            self.list_wastes.SetItemText(pain, ("R$ " + core.good_show("money", str(wastes_value))).replace(".", ","),
                                         2)
            self.list_wastes.Expand(pain)

            self.textbox_day_total.SetValue(
                core.good_show("money", str(sales_value - expenses_value)).replace(".", ","))
            self.textbox_sales_value.SetValue(core.good_show("money", str(sales_value)).replace(".", ","))
            self.textbox_sales_amount.SetValue(str(sales_amount))
            self.textbox_money_value.SetValue(core.good_show("money", str(money_value)).replace(".", ","))
            self.textbox_money_amount.SetValue(str(money_amount))
            self.textbox_card_value.SetValue(core.good_show("money", str(card_value)).replace(".", ","))
            self.textbox_card_amount.SetValue(str(card_amount))
            self.textbox_spent_value.SetValue(core.good_show("money", str(expenses_value)).replace(".", ","))
            self.textbox_spent_amount.SetValue(str(expenses_amount))
            try:
                if len(day_data["closure"]) == 0:
                    alpha = self.months_files[self.month_options.index(self.combobox_day_option.GetValue()) + 1]
                    zetta = shelve.open(core.directory_paths['saves'] + alpha)
                    self.textbox_cash_previous.SetValue(
                        core.good_show("money", str(zetta["closure"][0])).replace(".", ","))
                    zetta.close()

                elif day_data["closure"][10] == 0.0:

                    alpha = self.months_files[self.month_options.index(self.combobox_day_option.GetValue()) + 1]
                    zetta = shelve.open(core.directory_paths['saves'] + alpha)
                    self.textbox_cash_previous.SetValue(
                        core.good_show("money", str(zetta["closure"][0])).replace(".", ","))
                    zetta.close()
                else:
                    self.textbox_cash_previous.SetValue(
                        core.good_show("money", str(day_data["closure"][10])).replace(".", ","))
            except IndexError:
                self.textbox_cash_previous.SetValue('0,00')
            try:
                self.textbox_cash_real.SetValue(core.good_show("money", str(day_data["closure"][12])).replace(".", ","))
            except IndexError:
                self.textbox_cash_real.SetValue('0,00')
            try:
                self.textbox_cash_removed.SetValue(
                    core.good_show("money", str(day_data["closure"][14])).replace(".", ","))
            except IndexError:
                self.textbox_cash_removed.SetValue('0,00')
            tyde = float(self.textbox_cash_previous.GetValue().replace(",", ".")) + float(
                self.textbox_money_value.GetValue().replace(",", ".")) - float(
                self.textbox_spent_value.GetValue().replace(",", "."))
            self.textbox_cash_ideal.SetValue(core.good_show("money", str(tyde).replace(".", ",")))
            if self.textbox_cash_real.GetValue() == "0,00":
                tide = float(self.textbox_cash_ideal.GetValue().replace(",", ".")) - float(
                    self.textbox_cash_removed.GetValue().replace(",", "."))
            else:
                tide = float(self.textbox_cash_real.GetValue().replace(",", ".")) - float(
                    self.textbox_cash_removed.GetValue().replace(",", "."))
            if tide < 0:
                tide = 0.0
            self.textbox_cash_tomorrow.SetValue(core.good_show("money", str(tide).replace(".", ",")))
            day_data.close()
            self.save()
            self.combobox_day_option.Enable()

    def clean(self):
        self.list_sales.DeleteAllItems()
        self.list_expenses.DeleteAllItems()
        self.list_wastes.DeleteAllItems()
        self.textbox_day_total.SetValue("0,00")
        self.textbox_sales_value.SetValue("0,00")
        self.textbox_sales_amount.SetValue("0")
        self.textbox_money_value.SetValue("0,00")
        self.textbox_money_amount.SetValue("0")
        self.textbox_card_value.SetValue("0,00")
        self.textbox_card_amount.SetValue("0")
        self.textbox_spent_value.SetValue("0,00")
        self.textbox_spent_amount.SetValue("0")
        self.textbox_cash_previous.SetValue("0,00")
        self.textbox_cash_ideal.SetValue("0,00")
        self.textbox_cash_real.SetValue("0,00")
        self.textbox_cash_tomorrow.SetValue("0,00")
        self.textbox_cash_removed.SetValue("0,00")

    def reopen(self, event):
        self.combobox_day_option.Destroy()
        self.setup_options()
        self.setup(None)

    def save(self):
        a1 = float(self.textbox_day_total.GetValue().replace(",", "."))
        b1 = float(self.textbox_sales_value.GetValue().replace(",", "."))
        c1 = int(self.textbox_sales_amount.GetValue().replace(",", "."))
        d1 = float(self.textbox_money_value.GetValue().replace(",", "."))
        e1 = int(self.textbox_money_amount.GetValue().replace(",", "."))
        f1 = float(self.textbox_card_value.GetValue().replace(",", "."))
        g1 = int(self.textbox_card_amount.GetValue().replace(",", "."))
        h1 = float(self.textbox_spent_value.GetValue().replace(",", "."))
        i1 = int(self.textbox_spent_amount.GetValue().replace(",", "."))
        j1 = float(self.textbox_cash_previous.GetValue().replace(",", "."))
        k1 = float(self.textbox_cash_ideal.GetValue().replace(",", "."))
        l1 = float(self.textbox_cash_real.GetValue().replace(",", "."))
        m1 = float(self.textbox_cash_tomorrow.GetValue().replace(",", "."))
        n1 = float(self.textbox_cash_removed.GetValue().replace(",", "."))
        if l1:
            a0 = l1 - n1
        else:
            a0 = k1 - n1
        if a0 < 0:
            a0 = 0.0
        self.day_file = self.months_files[self.month_options.index(self.combobox_day_option.GetValue())]
        day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
        day_data["closure"] = [a0, a1, b1, c1, d1, e1, f1, g1, h1, i1, j1, k1, l1, m1, n1]
        day_data.close()

    def open_new_sale(self, event):
        sale.Sale(self)

    def open_edit_sale(self, event):
        red = self.list_sales.GetSelection()
        if self.list_sales.GetRootItem() == red:
            return
        registry_time = self.list_sales.GetItemText(red, 0)
        day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
        for i in day_data["sales"]:
            if day_data["sales"][i]['time'] == registry_time or day_data["sales"][i][
                'time'] == self.list_sales.GetItemText(
                    self.list_sales.GetItemParent(red), 0):
                key = i
                sale.Sale(self, argv=[(core.directory_paths['saves'] + self.day_file), key, registry_time])
        day_data.close()

    def open_new_expense(self, event):
        transactions.Expense(self)

    def open_edit_expense(self, event):
        red = self.list_expenses.GetSelection()
        if self.list_expenses.GetRootItem() == red:
            return
        registry_time = self.list_expenses.GetItemText(red, 0)
        day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
        for i in day_data["spent"]:
            if day_data["spent"][i]['time'] == registry_time:
                key = i
                transactions.Expense(self, argv=[(core.directory_paths['saves'] + self.day_file), key, registry_time])
        day_data.close()

    def open_record_editor(self, event):
        record_editor.EditionManager(self, record_date=self.combobox_day_option.GetValue())

    def open_new_waste(self, event):
        waste.Waste(self)

    def open_edit_waste(self, event):
        red = self.list_wastes.GetSelection()
        if self.list_wastes.GetRootItem() == red:
            return
        registry = self.list_wastes.GetItemText(red, 0)
        day_data = shelve.open(core.directory_paths['saves'] + self.day_file)
        for i in day_data["wastes"]:
            thor = float(str(self.list_wastes.GetItemText(red, 2)).replace('R$ ', '').replace(',', '.'))
            if day_data["wastes"][i]['description'] == registry and day_data["wastes"][i]['amount'] == int(
                    self.list_wastes.GetItemText(red, 1)) and thor == day_data["wastes"][i]['value'] == float(
                    self.list_wastes.GetItemText(red, 2).replace(',', '.').replace('R$ ', '')):
                key = i
                waste.Waste(self,
                            argv=[(core.directory_paths['saves'] + self.day_file), key, day_data["wastes"][i]['time']])
        day_data.close()

    def exit(self, event):
        self.Close()
