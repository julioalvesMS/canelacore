#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import os

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import clients
import core
import daily_report
import inventory
import categories
import monthly_report
import sale
import database
import transaction

__author__ = 'Julio'


class Ask(wx.Dialog):
    def __init__(self, parent, title, option):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(400, 180))
        self.option = option

        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        wx.StaticText(self, wx.ID_ANY, ask_options[option], pos=(50, 50))
        self.Centre()
        ok = wx.Button(self, wx.ID_ANY, u"Sim", pos=(100, 100))
        nok = wx.Button(self, wx.ID_ANY, u"Não", pos=(200, 100))
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
        elif self.option / 10 == 9:
            caller.exit(event)


class Confirmation(wx.Dialog):
    def __init__(self, parent, title, option):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(400, 180))
        self.Centre()
        self.option = option
        wx.StaticText(self, wx.ID_ANY, confirmation_options[option], pos=(50, 50))
        ok = wx.Button(self, wx.ID_ANY, u"Sim", pos=(100, 100))
        ok.Bind(wx.EVT_BUTTON, self.exit)
        nok = wx.Button(self, wx.ID_ANY, u"Não", pos=(200, 100))
        nok.Bind(wx.EVT_BUTTON, self.cont)
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
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


class Notification(wx.Dialog):

    text_done = u''

    def __init__(self, parent, data, title=u'Aviso de Entrega!'):
        """
        Método construtor do Dialog para
        """
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(500, 230))
        self.Centre()

        self.image = None
        self.data = data
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        textbox_message = wx.TextCtrl(self, wx.ID_ANY, self.get_message(), pos=(75, 50), size=(400, 90),
                                      style=wx.NO_BORDER | wx.TE_READONLY | wx.TE_MULTILINE |
                                      wx.TE_NO_VSCROLL | wx.TE_BESTWRAP)
        textbox_message.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)

        panel_side_buttons = wx.Panel(self, pos=(100, 150), size=(370, 40), style=wx.SIMPLE_BORDER)

        button_show_more = GenBitmapTextButton(panel_side_buttons, wx.ID_ANY,
                                               wx.Bitmap(core.directory_paths['icons'] + 'Search.png'),
                                               u'Ver Mais', pos=(0, 0), size=(100, 40))
        button_ok = GenBitmapTextButton(panel_side_buttons, wx.ID_OK,
                                        wx.Bitmap(core.directory_paths['icons'] + 'Check.png'),
                                        u'OK', pos=(100, 0), size=(100, 40))
        button_done = GenBitmapTextButton(panel_side_buttons, wx.ID_EXIT,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Delivery.png'),
                                          self.text_done, pos=(200, 0), size=(170, 40), style=wx.BU_LEFT)

        button_show_more.Bind(wx.EVT_BUTTON, self.more)
        button_ok.Bind(wx.EVT_BUTTON, self.exit)
        button_done.Bind(wx.EVT_BUTTON, self.ready)

        panel_side_buttons.SetFocus()

        wx.EVT_PAINT(self, self.OnPaint)

    def OnPaint(self, event=None):
        wx.PaintDC(self).DrawBitmap(self.get_image(), 5, 57)

    def get_image(self):
        return self.image

    def exit(self, event):
        self.Destroy()

    def more(self, event):
        pass

    def get_message(self):
        pass

    def ready(self, event):
        pass


class DeliveryNotification(Notification):

    text_done = u'Entrega Realizada'

    def __init__(self, parent, data, title=u'Aviso de Entrega!'):
        """
        Método construtor do Dialog para
        :type data: data_types.DeliveryData
        """
        Notification.__init__(self, parent, data, title)

        maps = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(core.directory_paths['icons'] + 'map_icon_48.png'),
                               pos=(50, 146), size=(48, 48), style=wx.NO_BORDER)
        maps.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
        maps.Bind(wx.EVT_BUTTON, self.open_maps)

        self.ShowModal()
        self.Destroy()

    def get_image(self):
        if not self.image:
            self.image = wx.Bitmap(core.directory_paths['icons'] + 'Gift_64.png', wx.BITMAP_TYPE_PNG)
        return self.image

    def get_message(self):
        address = self.data.city + u' - ' + self.data.address
        blur = u'Lembrete'
        tempo = str(datetime.now().hour) + ':' + str(datetime.now().minute)
        minor = core.hour2int(self.data.hour) - core.hour2int(tempo)
        if minor >= 0:
            message = u"%s! Faltam menos de %s minutos para a entrega para o(a) Sr(a) %s em %s, a qual esta " \
                      u"marcada para as %s." % (blur, str(minor), self.data.receiver, address, self.data.hour)
        else:
            message = u"%s! Passou-se %s minutos da hora da entrega para o(a) Sr(a) %s em %s, a qual estava " \
                      u"marcada para as %s." % (blur, str(-minor), self.data.receiver, address, self.data.hour)
        return message

    def more(self, event):
        sale.Sale(self.GetParent(), key=self.data.sale_ID, delivery_id=self.data.ID, editable=False)
        self.exit(None)

    def ready(self, event):
        db = database.DeliveriesDB()
        self.data.active = False
        db.delete_delivery(self.data.ID)
        db.close()
        self.exit(None)

    def open_maps(self, event):
        address = self.data.city + ', ' + self.data.address
        import internet
        internet.search_in_maps(address)


class TransactionNotification(Notification):

    text_done = u'Pagamento Realizada'

    def __init__(self, parent, data, title=u'Aviso de Pendencia no Pagamento!'):
        """
        Método construtor do Dialog para
        :type data: data_types.TransactionData
        """
        Notification.__init__(self, parent, data, title)

        self.ShowModal()
        self.Destroy()

    def get_image(self):
        if not self.image:
            self.image = wx.Bitmap(core.directory_paths['icons'] + 'Bills_64.png', wx.BITMAP_TYPE_PNG)
        return self.image

    def get_message(self):
        blur = u'Atenção'
        what = u'recebimento' if self.data.type is transaction.INCOME else u'pagamento'

        args = (blur, what, self.data.description, core.format_cash_user(self.data.value, currency=True),
                core.format_date_user(self.data.transaction_date))
        message = u'%s! O %s da conta "%s" no valor de %s, ' \
                  u'a qual está programada para %s ainda está pendente' % args

        return message

    def more(self, event):
        transaction.Transaction(self.GetParent(), transaction_type=self.data.type,
                                data=self.data, editable=False)
        self.exit(None)

    def ready(self, event):
        db = database.TransactionsDB()
        db.edit_transaction_payment(self.data.ID)
        db.close()
        self.exit(None)


class PasswordBox(wx.Dialog):
    def __init__(self, parent, protected_function, title=u'Acesso Restrito'):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(400, 180))
        self.parent = parent
        self.protected_function = protected_function
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        wx.EVT_PAINT(self, self.OnPaint)
        text_digite = wx.StaticText(self, wx.ID_ANY, u'Digíte a senha:', pos=(100, 25))
        text_digite.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.password = wx.TextCtrl(self, wx.ID_ANY, pos=(100, 50), size=(250, 30), style=wx.TE_PASSWORD)
        cancel = wx.Button(self, wx.ID_CANCEL, u'Cancelar', pos=(120, 90))
        contin = wx.Button(self, wx.ID_OK, u'Continuar', pos=(250, 90))
        cancel.Bind(wx.EVT_BUTTON, self.exit)
        contin.Bind(wx.EVT_BUTTON, self.go_on)
        self.denied_message = wx.StaticText(self, wx.ID_ANY, u'Acesso Negado!', pos=(170, 130))
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
            self.protected_function()
            self.Destroy()
        else:
            self.denied_message.Show()


class TextBox(wx.Frame):
    notes_box = None
    status_bar = None

    def __init__(self, parent, month, title=u'Observações'):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
        self.month = month
        self.parent = parent

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetMinSize((400, 300))
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.COLOR_DEFAULT_BACKGROUND)
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
        self.notes_box = wx.TextCtrl(self, wx.ID_ANY, pos=(10, 60), size=(400, 300),
                                     style=wx.TE_MULTILINE | wx.TE_BESTWRAP)
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


def lauch_directory_selector(parent, title=u'Selecionar Diretório', default_path=None):

    if not default_path:
        default_path = core.current_dir

    loc = wx.DirDialog(parent, title, default_path)
    loc.ShowModal()
    loc.Destroy()

    new_path = loc.GetPath()

    if new_path == default_path:
        return None

    return new_path

def launch_error(origin, message, title=u'Error 404'):
    a = wx.MessageDialog(origin, message, title, style=wx.OK | wx.ICON_ERROR)
    a.ShowModal()
    a.Destroy()
    return False


def backup_confirmation(origin=None):
    a = wx.MessageDialog(origin, u'Backup salvo com sucesso!', u'Backup', style=wx.OK | wx.ICON_INFORMATION)
    a.ShowModal()
    a.Destroy()
    return True

ask_options = {
    1: u'Você tem certeza que deseja apagar tudo?',
    11: u"Finalizar registro de venda?",
    12: u"Finalizar registro de despesa?",
    13: u"Finalizar registro de perda?",
    14: u"Finalizar cadastro de cliente?",
    15: u"Finalizar cadastro de produto?",
    16: u"Finalizar registro de ganho?",
    17: u"Finalizar registro de categoria?",
    21: u"Você tem certeza que deseja apagar esta venda?",
    22: u"Você tem certeza que deseja apagar esta despesa?",
    23: u"Você tem certeza que deseja apagar este registro?",
    24: u"Você tem certeza que deseja apagar este cliente?",
    25: u"Você tem certeza que deseja apagar este produto?",
    26: u"Você tem certeza que deseja apagar este ganho?",
    27: u"Você tem certeza que deseja apagar esta categoria?",
    28: u"Você tem certeza que deseja apagar esta venda?",
    30: u"Você tem certeza que deseja restaurar esse registro?",
    40: u"Você tem certeza que deseja desconectar essa venda?",
    90: u"Você tem certeza que deseja sair do programa?",
    91: u"Você tem certeza que deseja sair agora?"
}

confirmation_options = {
    1: u"Venda registrada com sucesso!\nRegistrar outra venda?",
    2: u"Despesa registrada com sucesso!\nRegistrar outra despesa?",
    3: u"Desperdício registrado com sucesso!\nRegistrar outro?",
    4: u"Cliente cadastrado com sucesso!\nCadatrar outro?",
    5: u"Produto cadastrado com sucesso!\nCadatrar outro?",
    6: u"Produtos registrados com sucesso!\nRegistrar outros?",
    7: u"Ganho registrado com sucesso!\nRegistrar outro?",
    8: u"Categoria registrada com sucesso!\nRegistrar outra?"
}
