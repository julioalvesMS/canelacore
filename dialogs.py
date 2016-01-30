#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import os

import wx
import wx.gizmos

import clients
import core
import daily_report
import inventory
import categories
import monthly_report
import sale
import database

__author__ = 'Julio'


class Ask(wx.Dialog):
    def __init__(self, parent, title, option):
        wx.Dialog.__init__(self, parent, -1, title, size=(400, 180))
        self.option = option

        self.SetBackgroundColour(core.default_background_color)
        wx.StaticText(self, -1, ask_options[option], pos=(50, 50))
        self.Centre()
        ok = wx.Button(self, -1, u"Sim", pos=(100, 100))
        nok = wx.Button(self, -1, u"Não", pos=(200, 100))
        ok.Bind(wx.EVT_BUTTON, self.confirmed)
        nok.Bind(wx.EVT_BUTTON, self.exit)

        self.ShowModal()

    def exit(self, event):
        self.Close()

    def confirmed(self, event):
        caller = self.GetParent()
        self.Destroy()
        if self.option == 1:
            caller.clean()
        elif self.option / 10 == 1:
            caller.end()
        elif self.option / 10 == 2 and self.option % 10 <= 3:
            caller.delete(caller.available_lists[self.option % 10 - 1])
        elif self.option / 10 == 2 and self.option % 10 >= 4:
            caller.data_delete(None)
        elif self.option / 10 == 3:
            caller.delete()
        elif self.option / 10 == 4:
            caller.sale_disconnect()
        elif self.option / 10 == 9:
            caller.exit(event)


class Confirmation(wx.Dialog):
    def __init__(self, parent, title, option):
        wx.Dialog.__init__(self, parent, -1, title, size=(400, 180))
        self.Centre()
        self.option = option
        wx.StaticText(self, -1, confirmation_options[option], pos=(50, 50))
        ok = wx.Button(self, -1, u"Sim", pos=(100, 100))
        ok.Bind(wx.EVT_BUTTON, self.exit)
        nok = wx.Button(self, -1, u"Não", pos=(200, 100))
        nok.Bind(wx.EVT_BUTTON, self.cont)
        self.SetBackgroundColour(core.default_background_color)
        if type(parent.GetParent()) in [daily_report.Report, monthly_report.Report, clients.ClientManager,
                                        inventory.InventoryManager, categories.ProductCategoryManager]:
            parent.GetParent().setup(None)
        self.ShowModal()
        self.Destroy()

    def exit(self, event):
        self.Close()

    def cont(self, event):
        self.GetParent().exit(None)
        self.exit(None)


class Warner(wx.Dialog):
    def __init__(self, parent, data, title=u'Aviso de Entrega!'):
        """
        :type data: data_types.DeliveryData
        """
        wx.Dialog.__init__(self, parent, -1, title, size=(500, 230))
        self.data = data
        self.SetBackgroundColour(core.default_background_color)

        address = data.city + u' - ' + data.address
        blur = u'Lembrete'
        tempo = str(datetime.now().hour) + ':' + str(datetime.now().minute)
        minor = core.hour2int(data.hour) - core.hour2int(tempo)
        if minor >= 0:
            y = u"%s! Falta menos de %s minutos para a entrega para o(a) Sr(a) %s\n" \
                u"em %s, a qual esta marcada para as %s." % (blur, str(minor), data.receiver, address, data.hour)
        else:
            y = u"%s! Passou-se %s minutos da hora da entrega para o(a) Sr(a) %s\n" \
                u"em %s, a qual estava marcada para as %s." % (blur, str(-minor), data.receiver, address, data.hour)
        wx.StaticText(self, -1, y, pos=(10, 50))
        self.Centre()
        ok = wx.Button(self, -1, u"Ver Mais", pos=(100, 150))
        ok.Bind(wx.EVT_BUTTON, self.more)
        nok = wx.Button(self, -1, u"OK", pos=(200, 150))
        nok.Bind(wx.EVT_BUTTON, self.exit)
        gray = wx.Button(self, -1, u"Entrega realizada", pos=(300, 150))
        gray.Bind(wx.EVT_BUTTON, self.ready)
        self.ShowModal()
        self.Destroy()

    def exit(self, event):
        self.Close()

    def more(self, event):
        sale.Sale(self.GetParent(), key=self.data.sale_ID, delivery_id=self.data.ID, editable=False)
        self.exit(None)

    def ready(self, event):
        db = database.DeliveriesDB()
        self.data.active = False
        db.delete_delivery(self.data.ID)
        db.close()
        self.exit(None)


class PasswordBox(wx.Dialog):
    def __init__(self, parent, title=u'Acesso Restrito'):
        wx.Dialog.__init__(self, parent, -1, title, size=(400, 180))
        self.parent = parent
        self.Centre()
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        wx.EVT_PAINT(self, self.OnPaint)
        wx.StaticText(self, -1, u'Digíte a senha:', pos=(100, 25)).SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.password = wx.TextCtrl(self, -1, pos=(100, 50), size=(250, 30), style=wx.TE_PASSWORD)
        cancel = wx.Button(self, wx.ID_CANCEL, u'Cancelar', pos=(120, 90))
        contin = wx.Button(self, wx.ID_OK, u'Continuar', pos=(250, 90))
        cancel.Bind(wx.EVT_BUTTON, self.exit)
        contin.Bind(wx.EVT_BUTTON, self.go_on)
        self.denied_message = wx.StaticText(self, -1, u'Acesso Negado!', pos=(170, 130))
        self.denied_message.SetForegroundColour(wx.RED)
        self.denied_message.Hide()
        self.password.SetFocus()
        self.ShowModal()
        self.Destroy()

    def OnPaint(self, event):
        lok = wx.Bitmap(core.directory_paths['icons'] + 'Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self).DrawBitmap(lok, 0, 30)

    def exit(self, event):
        self.Destroy()

    def go_on(self, event):
        key = self.password.GetValue()
        if core.password_check(key):
            self.parent.open_monthly_report(None)
            self.Destroy()
        else:
            self.denied_message.Show()


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
        tool_bar.AddSimpleTool(4501, wx.Bitmap(core.directory_paths['icons'] + 'Save.png', wx.BITMAP_TYPE_PNG),
                               u'Salvar', '')
        tool_bar.AddSeparator()
        tool_bar.AddSimpleTool(4502, wx.Bitmap(core.directory_paths['icons'] + 'Copy.png', wx.BITMAP_TYPE_PNG),
                               u'Copiar', '')
        tool_bar.AddSimpleTool(4503, wx.Bitmap(core.directory_paths['icons'] + 'Cut.png', wx.BITMAP_TYPE_PNG),
                               u'Recortar', '')
        tool_bar.AddSimpleTool(4504, wx.Bitmap(core.directory_paths['icons'] + 'Paste.png', wx.BITMAP_TYPE_PNG),
                               u'Colar', '')
        tool_bar.AddSimpleTool(4505, wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG),
                               u'Apagar', '')
        tool_bar.AddSeparator()
        tool_bar.AddSimpleTool(4509, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                               u'Sair', '')
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
        if type(self.GetParent()) is monthly_report.Report:
            if self.notes_box.SaveFile(core.directory_paths['saves'] + '%s_obs.txt' % self.month):
                self.status_bar.SetStatusText(u'Observação salva com sucesso')
                time.sleep(1)
                self.status_bar.SetStatusText('')
            else:
                self.status_bar.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
                time.sleep(2)
                self.status_bar.SetStatusText('')

    def save_to(self, event):
        loc = wx.FileDialog(self, u'Salvar em', os.getcwd(), self.month + '_obs.txt', '*.*', wx.FD_SAVE)
        loc.ShowModal()
        loc.Destroy()
        if self.notes_box.SaveFile(loc.GetPath()):
            self.status_bar.SetStatusText(u'Observação salva com sucesso em %s' % loc.GetPath())
            time.sleep(1)
            self.status_bar.SetStatusText(u'')
        else:
            self.status_bar.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
            time.sleep(2)
            self.status_bar.SetStatusText(u'')

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


def launch_error(origin, message, title=u'Error 404'):
    a = wx.MessageDialog(origin, message, title, style=wx.OK | wx.ICON_ERROR)
    a.ShowModal()
    a.Destroy()
    return False

ask_options = {
    1: u'Você tem certeza que deseja apagar tudo?',
    11: u"Finalizar registro de venda?",
    12: u"Finalizar registro de gasto?",
    13: u"Finalizar registro de perda?",
    14: u"Finalizar cadastro de cliente?",
    15: u"Finalizar cadastro de produto?",
    16: u"Finalizar registro de ganho?",
    17: u"Finalizar registro de categoria?",
    21: u"Você tem certeza que deseja apagar esta venda?",
    22: u"Você tem certeza que deseja apagar este gasto?",
    23: u"Você tem certeza que deseja apagar este registro?",
    24: u"Você tem certeza que deseja apagar este cliente?",
    25: u"Você tem certeza que deseja apagar este produto?",
    26: u"Você tem certeza que deseja apagar este ganho?",
    27: u"Você tem certeza que deseja apagar esta categoria?",
    30: u"Você tem certeza que deseja restaurar esse registro?",
    40: u"Você tem certeza que deseja desconectar essa venda?",
    90: u"Você tem certeza que deseja sair do programa?",
    91: u"Você tem certeza que deseja sair agora?"
}

confirmation_options = {
    1: u"Venda registrada com sucesso!\nRegistrar outra venda?",
    2: u"Gasto registrado com sucesso!\nRegistrar outro gasto?",
    3: u"Desperdício registrado com sucesso!\nRegistrar outro?",
    4: u"Cliente cadastrado com sucesso!\nCadatrar outro?",
    5: u"Produto cadastrado com sucesso!\nCadatrar outro?",
    6: u"Produtos registrados com sucesso!\nRegistrar outros?",
    7: u"Ganho registrado com sucesso!\nRegistrar outro?",
    8: u"Categoria registrada com sucesso!\nRegistrar outra?"
}
