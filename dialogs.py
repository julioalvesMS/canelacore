#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

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
                                        inventory.InventoryManager, categories.CategoryManager]:
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
        cancel = wx.Button(self, -1, u'Cancelar', pos=(120, 90))
        contin = wx.Button(self, -1, u'Continuar', pos=(250, 90))
        cancel.Bind(wx.EVT_BUTTON, self.exit)
        contin.Bind(wx.EVT_BUTTON, self.go_on)
        self.denied_message = wx.StaticText(self, -1, u'Acesso Negado!', pos=(170, 130))
        self.denied_message.SetForegroundColour(wx.RED)
        self.denied_message.Hide()
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
