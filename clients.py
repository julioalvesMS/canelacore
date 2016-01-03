#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shelve
import shutil
import threading
from datetime import datetime
from string import lower

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs
import sale

__author__ = 'Julio'


class ClientManager(wx.Frame):

    list_clients = None
    dict_clients_basic_data = None
    textbox_filter = None

    def __init__(self, parent, title=u'Clientes', client_selection_mode=False):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.client_selection_mode = client_selection_mode
        self.parent = parent

        self.setup_gui()

        self.setup(1)
        self.Show()

    def setup_gui(self):
        self.SetPosition(wx.Point(100, 100))
        self.SetSize(wx.Size(1200, 550))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        panel_general = wx.Panel(self, pos=(10, 10), size=(1180, 100))
        if self.client_selection_mode:
            sele = GenBitmapTextButton(panel_general, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                       u'Selecionar', pos=(50, 40), size=(100, 40), style=wx.SIMPLE_BORDER)
            sele.SetBackgroundColour(core.default_background_color)
            sele.Bind(wx.EVT_BUTTON, self.data_select)
        panel_top = wx.Panel(panel_general, -1, size=(400, 40), pos=(200, 40), style=wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(panel_top, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'user-info.png', wx.BITMAP_TYPE_PNG),
                                  u'Ver Mais', pos=(0, 0), size=(100, 40))
        see.SetBackgroundColour(core.default_background_color)
        see.Bind(wx.EVT_BUTTON, self.data_open)
        plus = GenBitmapTextButton(panel_top, -1,
                                   wx.Bitmap(core.directory_paths['icons'] + 'contact-new.png', wx.BITMAP_TYPE_PNG),
                                   u'Novo', pos=(100, 0), size=(100, 40))
        plus.SetBackgroundColour(core.default_background_color)
        plus.Bind(wx.EVT_BUTTON, self.open_client_registry)
        edi = GenBitmapTextButton(panel_top, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG), u'Editar',
                                  pos=(200, 0), size=(100, 40))
        edi.SetBackgroundColour(core.default_background_color)
        edi.Bind(wx.EVT_BUTTON, self.data_edit)
        era = GenBitmapTextButton(panel_top, -1,
                                  wx.Bitmap(core.directory_paths['icons'] + 'Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar',
                                  pos=(300, 0), size=(100, 40))
        era.SetBackgroundColour(core.default_background_color)
        era.Bind(wx.EVT_BUTTON, self.ask_delete)
        self.textbox_filter = wx.SearchCtrl(panel_general, -1, pos=(650, 45), size=(200, 30), style=wx.TE_PROCESS_ENTER)
        self.textbox_filter.SetDescriptiveText(u'Busca por nome')
        fin = wx.BitmapButton(panel_general, -1, wx.Bitmap(core.directory_paths['icons'] + 'edit_find.png'),
                              pos=(855, 42),
                              size=(35, 35))
        fin.Bind(wx.EVT_BUTTON, self.database_search)
        self.textbox_filter.Bind(wx.EVT_TEXT_ENTER, self.database_search)
        self.textbox_filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.database_search)
        panel_bottom = wx.Panel(panel_general, size=(240, 40), pos=(900, 40), style=wx.SIMPLE_BORDER)
        button_exit = GenBitmapTextButton(panel_bottom, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                          u'Sair',
                                          pos=(120, 0), size=(120, 40))
        button_exit.SetBackgroundColour(core.default_background_color)
        button_exit.Bind(wx.EVT_BUTTON, self.exit)
        rep = GenBitmapTextButton(panel_bottom, -1, wx.Bitmap(core.directory_paths['icons'] + 'Reset.png'),
                                  u'Atualizar',
                                  pos=(0, 0), size=(120, 40))
        rep.SetBackgroundColour(core.default_background_color)
        rep.Bind(wx.EVT_BUTTON, self.setup)
        panel_middle = wx.Panel(self, -1, pos=(10, 110), size=(1180, 410))
        self.list_clients = wx.ListCtrl(panel_middle, -1, pos=(5, 5), size=(1170, 390),
                                        style=wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER | wx.LC_REPORT)
        self.list_clients.InsertColumn(0, u'Nome do cliente', width=400)
        self.list_clients.InsertColumn(1, u'ID', width=50)
        self.list_clients.InsertColumn(2, u'Telefone', width=200)
        self.list_clients.InsertColumn(3, u'e-mail', width=200)
        self.list_clients.InsertColumn(4, u'Endereço', width=315)
        if self.client_selection_mode:
            self.list_clients.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_select)
        else:
            self.list_clients.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.data_open)

    def setup(self, event):     # TODO Fazer a thread fechar direito com o resto do app
        turn = threading.Thread(target=self.__setup__)
        turn.daemon = True
        turn.start()

    def __setup__(self):
        self.list_clients.DeleteAllItems()
        self.textbox_filter.Clear()
        key_list = []
        self.dict_clients_basic_data = {}
        for root, dirs, files in os.walk(core.directory_paths['clients']):
            if root != core.directory_paths['clients']:
                try:
                    o = shelve.open(root + core.slash + root.split(core.slash)[-1] + '_infos.txt')
                    if not o['tel1']:
                        if o['tel2']:
                            tel = o['tel2']
                        else:
                            tel = '(__)____-____'
                    else:
                        tel = o['tel1']
                    if o['adress'] and o['city'] and o['state'] != '--':
                        ad = o['city'] + ' - ' + o['state'] + ', ' + o['adress']
                    else:
                        ad = '_____-__,_________ '
                    self.dict_clients_basic_data[o['name']] = [str(int(root.split(core.slash)[-1])), tel, o['email'], ad]
                    key_list.append(o['name'])
                    o.close()
                except ValueError or KeyError:
                    pass
        key_list.sort()
        for g in key_list:
            self.list_clients.Append((g, self.dict_clients_basic_data[g][0], self.dict_clients_basic_data[g][1],
                                      self.dict_clients_basic_data[g][2], self.dict_clients_basic_data[g][3]))

    def data_delete(self, event):
        it = self.list_clients.GetFocusedItem()
        if it == -1:
            return
        e_id = self.list_clients.GetItem(it, 1).GetText()
        rtime = core.good_show("o", str(datetime.now().hour)) + "-" + core.good_show("o", str(
            datetime.now().minute)) + "-" + core.good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(
                datetime.now().day))
        dt = '%s_%s' % (rdate, rtime)
        while len(e_id) < 6:
            e_id = '0' + e_id
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/clients'):
            os.mkdir('#Trash/clients')
        if not os.path.exists('#Trash/clients/deleted'):
            os.mkdir('#Trash/clients/deleted')
        if not os.path.exists('#Trash/clients/deleted/' + e_id):
            os.mkdir('#Trash/clients/deleted/' + e_id)
        shutil.copytree('clients/' + e_id, '#Trash/clients/deleted/%s/%s' % (e_id, dt))
        dirs = os.listdir('clients')
        for i in dirs:
            if int(i) == int(e_id):
                shutil.rmtree('clients/' + i)
        self.setup(None)

    def data_edit(self, event):
        po = self.list_clients.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_clients.GetItem(po, 1).GetText()
        ko = self.list_clients.GetItemText(po)
        ClientData(self, ko, lo, True)

    def data_open(self, event):
        po = self.list_clients.GetFocusedItem()
        if po == -1:
            return
        lo = self.list_clients.GetItem(po, 1).GetText()
        ko = self.list_clients.GetItemText(po)
        ClientData(self, ko, lo, False)

    def data_select(self, event):
        g = self.list_clients.GetFocusedItem()
        if g == -1:
            return
        name = self.list_clients.GetItemText(g, 0)
        client_id = self.list_clients.GetItemText(g, 1)
        while len(client_id) < 6:
            client_id = '0' + client_id
        self.parent.textbox_client_name.SetValue(name)
        self.parent.textbox_client_id.SetValue(client_id)
        self.exit(None)

    def database_search(self, event):
        self.list_clients.DeleteAllItems()
        key_list = []
        self.dict_clients_basic_data = {}
        for root, dirs, files in os.walk(core.directory_paths['clients']):
            if root != core.directory_paths['clients']:
                try:
                    o = shelve.open(root + core.slash + root.split(core.slash)[1] + '_infos.txt')
                    tex = lower(self.textbox_filter.GetValue())
                    num = len(tex)
                    fri = []
                    for a in o['name'].split():
                        fri.append(lower(a[:num]))
                    if (tex in fri) or (tex == str(int(root.split(core.slash)[1]))):
                        if not o['tel1']:
                            if o['tel2']:
                                tel = o['tel2']
                            else:
                                tel = '(__)____-____'
                        else:
                            tel = o['tel1']
                        if o['adress'] and o['city'] and o['state'] != '--':
                            ad = o['city'] + ' - ' + o['state'] + ', ' + o['adress']
                        else:
                            ad = '_____-__,_________ '
                        self.dict_clients_basic_data[o['name']] = [str(int(root.split(core.slash)[1])), tel, o['email'],
                                                                   ad]
                        key_list.append(o['name'])
                    o.close()
                except ValueError:
                    pass
        key_list.sort()
        for g in key_list:
            self.list_clients.Append((g, self.dict_clients_basic_data[g][0], self.dict_clients_basic_data[g][1],
                                      self.dict_clients_basic_data[g][2], self.dict_clients_basic_data[g][3]))

    def clean(self):
        self.textbox_filter.Clear()
        self.setup(None)

    def ask_delete(self, event):
        dialogs.Ask(self, u'Apagar Cliente', 24)

    def open_client_registry(self, event):
        ClientRegister(self)

    def exit(self, event):
        self.Close()


class ClientRegister(wx.Frame):
    textbox_client_name = None
    textbox_client_sex = None
    textbox_client_birth = None
    textbox_client_telephone_1 = None
    textbox_client_telephone_2 = None
    textbox_client_email = None
    textbox_client_cpf = None
    textbox_client_state = None
    textbox_client_city = None
    textbox_client_district = None
    textbox_client_address = None
    textbox_client_observations = None

    panel_client_image = None

    dict_clients_basic_data = None

    def __init__(self, parent, title=u'Cadastro de Clientes'):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU |
                          wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.SetSize(wx.Size(500, 585))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        self.Centre()

        panel_client_intel = wx.Panel(self, -1, pos=(0, 0), size=(500, 500), style=wx.TAB_TRAVERSAL)
        wx.StaticText(panel_client_intel, -1, u'Nome do cliente:', pos=(190, 10))
        wx.StaticText(panel_client_intel, -1, u'Sexo:', pos=(190, 70))
        wx.StaticText(panel_client_intel, -1, u'Data de Nascimento:', pos=(340, 70))
        wx.StaticText(panel_client_intel, -1, u'Telefone 1:', pos=(190, 130))
        wx.StaticText(panel_client_intel, -1, u'Telefone 2:', pos=(340, 130))
        wx.StaticText(panel_client_intel, -1, u'e-mail:', pos=(10, 190))
        wx.StaticText(panel_client_intel, -1, u'CPF:', pos=(340, 190))
        wx.StaticText(panel_client_intel, -1, u'Estado:', pos=(10, 250))
        wx.StaticText(panel_client_intel, -1, u'Cidade:', pos=(100, 250))
        wx.StaticText(panel_client_intel, -1, u'Bairro:', pos=(280, 250))
        wx.StaticText(panel_client_intel, -1, u'Endereço:', pos=(10, 310))
        wx.StaticText(panel_client_intel, -1, u'Observações:', pos=(10, 370))
        self.textbox_client_name = wx.TextCtrl(panel_client_intel, -1, pos=(190, 30), size=(300, 30))
        self.textbox_client_sex = wx.ComboBox(panel_client_intel, -1, choices=[u'Feminino', u'Maculino'], pos=(190, 90),
                                              size=(120, 30), style=wx.CB_READONLY)
        self.textbox_client_birth = wx.TextCtrl(panel_client_intel, -1, pos=(340, 90), size=(120, 30))
        self.textbox_client_telephone_1 = wx.TextCtrl(panel_client_intel, -1, pos=(190, 150), size=(120, 30))
        self.textbox_client_telephone_2 = wx.TextCtrl(panel_client_intel, -1, pos=(340, 150), size=(120, 30))
        self.textbox_client_email = wx.TextCtrl(panel_client_intel, -1, pos=(10, 210), size=(300, 30))
        self.textbox_client_cpf = wx.TextCtrl(panel_client_intel, -1, pos=(340, 210), size=(120, 30))
        self.textbox_client_state = wx.ComboBox(panel_client_intel, -1, choices=core.brazil_states, pos=(10, 270),
                                                size=(60, 30), style=wx.CB_READONLY)
        self.textbox_client_city = wx.TextCtrl(panel_client_intel, -1, pos=(100, 270), size=(150, 30))
        self.textbox_client_district = wx.TextCtrl(panel_client_intel, -1, pos=(280, 270), size=(150, 30))
        self.textbox_client_address = wx.TextCtrl(panel_client_intel, -1, pos=(10, 330), size=(300, 30))
        self.textbox_client_observations = wx.TextCtrl(panel_client_intel, -1, pos=(10, 390), size=(480, 100),
                                                       style=wx.TE_MULTILINE)
        self.textbox_client_birth.Bind(wx.EVT_CHAR, core.check_date)
        self.textbox_client_telephone_1.Bind(wx.EVT_CHAR, core.check_telephone)
        self.textbox_client_telephone_2.Bind(wx.EVT_CHAR, core.check_telephone)
        self.textbox_client_cpf.Bind(wx.EVT_CHAR, core.check_cpf)
        self.textbox_client_sex.SetValue(u'Feminino')
        self.textbox_client_birth.SetValue(u'__/__/____')
        self.textbox_client_state.SetValue('SP')
        self.textbox_client_city.SetValue(u'Itatiba')

        self.panel_client_image = wx.Panel(panel_client_intel, -1, size=(150, 150), pos=(10, 25),
                                           style=wx.SIMPLE_BORDER)
        self.panel_client_image.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.panel_client_image, self.OnPaint)
        panel_bottom = wx.Panel(self, -1, pos=(0, 500), size=(500, 50))
        panel_bottom_buttons = wx.Panel(panel_bottom, pos=(90, 5), size=(320, 40), style=wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(panel_bottom_buttons, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                     u"Finalizar", pos=(0, 0), size=(100, 40))
        finish.Bind(wx.EVT_BUTTON, self.ask_delete)
        restart = GenBitmapTextButton(panel_bottom_buttons, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u"Recomeçar", pos=(100, 0), size=(120, 40))
        restart.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",
                                     pos=(220, 0), size=(100, 40))
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit)

    def ask_delete(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 14)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        if self.textbox_client_name.GetValue():
            dialogs.Ask(self, u'Sair', 91)
        else:
            self.Close()

    def clean(self):
        self.textbox_client_name.SetValue(u'')
        self.textbox_client_sex.SetValue(u'Feminino')
        self.textbox_client_birth.SetValue(u'__/__/____')
        self.textbox_client_telephone_1.SetValue(u'')
        self.textbox_client_telephone_2.SetValue(u'')
        self.textbox_client_email.SetValue(u'')
        self.textbox_client_cpf.SetValue(u'')
        self.textbox_client_state.SetValue(u'SP')
        self.textbox_client_city.SetValue(u'Itatiba')
        self.textbox_client_district.SetValue(u'')
        self.textbox_client_address.SetValue(u'')
        self.textbox_client_observations.SetValue(u'')

    def end(self):
        if not self.textbox_client_name.GetValue():
            dialogs.launch_error(self, u'É necessário o nome, para o cadastro', u'Error 404')
            return
        if not os.path.exists('clients'):
            os.mkdir('clients')
        dirs = os.listdir('clients')
        if os.path.exists('#Trash/clients/deleted'):
            dirs += os.listdir('#Trash/clients/deleted')
        if os.path.exists('#Trash/clients/edited'):
            dirs += os.listdir('#Trash/clients/edited')
        last_id = 0
        for i in dirs:
            if int(i) > last_id:
                last_id = int(i)
        new_id = last_id + 1
        idstr = str(new_id)
        while len(idstr) < 6:
            idstr = '0' + idstr
        os.mkdir('clients/' + idstr)
        rtime = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(
                datetime.now().day))
        po = (core.directory_paths['clients'] + idstr + core.slash + idstr + '_infos.txt')
        s = shelve.open(po)
        xname = self.textbox_client_name.GetValue()
        while xname[0] == ' ':
            xname = xname[1:]
        names = xname.split()
        for i in range(0, len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['name'] = namef
        s['sex'] = self.textbox_client_sex.GetValue()
        s['birth'] = self.textbox_client_birth.GetValue()
        s['email'] = self.textbox_client_email.GetValue()
        s['cpf'] = self.textbox_client_cpf.GetValue()
        s['tel1'] = self.textbox_client_telephone_1.GetValue()
        s['tel2'] = self.textbox_client_telephone_2.GetValue()
        s['state'] = self.textbox_client_state.GetValue()
        s['city'] = self.textbox_client_city.GetValue()
        s['hood'] = self.textbox_client_district.GetValue()
        s['adress'] = self.textbox_client_address.GetValue()
        s['obs'] = self.textbox_client_observations.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        self.clean()
        parent = self.GetParent()
        if type(parent) is ClientManager:
            parent.setup(1)
        if type(parent) is sale.Sale:
            parent.client_name.SetValue(namef)
            parent.client_id.SetValue(idstr)
            self.Close()
            return
        dialogs.Confirmation(self, u'Sucesso', 4)

    def OnPaint(self, event):
        wx.PaintDC(self.panel_client_image).DrawBitmap(wx.Bitmap(core.directory_paths['icons'] + 'stock_person.png'), 0,
                                                       0)

    def exit(self, event):
        self.Close()


class ClientData(wx.Frame):
    textbox_client_name = None
    textbox_client_sex = None
    textbox_client_birth = None
    textbox_client_telephone_1 = None
    textbox_client_telephone_2 = None
    textbox_client_email = None
    textbox_client_cpf = None
    textbox_client_state = None
    textbox_client_city = None
    textbox_client_district = None
    textbox_client_address = None
    textbox_client_observations = None
    textbox_client_intel = None

    list_bought = None

    panel_client_image = None

    dict_clients_basic_data = None

    def __init__(self, parent, title, client_id, editable=True):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU |
                          wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)

        client_id = str(client_id)
        while len(client_id) < 6:
            client_id = '0' + client_id
        self.editable = editable
        self.client_id = client_id
        self.parent = parent
        self.title = title

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.SetSize(wx.Size(850, 585))
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(core.default_background_color)
        self.Centre()
        panel_client_intel = wx.Panel(self, -1, pos=(0, 0), size=(500, 500), style=wx.TAB_TRAVERSAL)
        wx.StaticText(panel_client_intel, -1, u'Nome do cliente:', pos=(190, 10))
        self.textbox_client_name = wx.TextCtrl(panel_client_intel, -1, pos=(190, 30), size=(300, 30))
        wx.StaticText(panel_client_intel, -1, u'Sexo:', pos=(190, 70))
        if self.editable:
            self.textbox_client_sex = wx.ComboBox(panel_client_intel, -1, choices=[u'Feminino', u'Maculino'],
                                                  pos=(190, 90), size=(120, 30),
                                                  style=wx.CB_READONLY)
        else:
            self.textbox_client_sex = wx.TextCtrl(panel_client_intel, -1, pos=(190, 90), size=(100, 30))
        wx.StaticText(panel_client_intel, -1, u'Data de Nascimento:', pos=(340, 70))
        self.textbox_client_birth = wx.TextCtrl(panel_client_intel, -1, pos=(340, 90), size=(120, 30))
        self.textbox_client_birth.SetValue('__/__/____')
        self.textbox_client_birth.Bind(wx.EVT_CHAR, core.check_date)
        wx.StaticText(panel_client_intel, -1, u'Telefone 1:', pos=(190, 130))
        self.textbox_client_telephone_1 = wx.TextCtrl(panel_client_intel, -1, pos=(190, 150), size=(120, 30))
        self.textbox_client_telephone_1.Bind(wx.EVT_CHAR, core.check_telephone)
        wx.StaticText(panel_client_intel, -1, u'Telefone 2:', pos=(340, 130))
        self.textbox_client_telephone_2 = wx.TextCtrl(panel_client_intel, -1, pos=(340, 150), size=(120, 30))
        self.textbox_client_telephone_2.Bind(wx.EVT_CHAR, core.check_telephone)
        wx.StaticText(panel_client_intel, -1, u'e-mail:', pos=(10, 190))
        self.textbox_client_email = wx.TextCtrl(panel_client_intel, -1, pos=(10, 210), size=(300, 30))
        wx.StaticText(panel_client_intel, -1, u'CPF:', pos=(340, 190))
        self.textbox_client_cpf = wx.TextCtrl(panel_client_intel, -1, pos=(340, 210), size=(120, 30))
        self.textbox_client_cpf.Bind(wx.EVT_CHAR, core.check_cpf)
        wx.StaticText(panel_client_intel, -1, u'Estado:', pos=(10, 250))
        if self.editable:
            self.textbox_client_state = wx.ComboBox(panel_client_intel, -1, choices=core.brazil_states, pos=(10, 270),
                                                    size=(60, 30),
                                                    style=wx.CB_READONLY)
        else:
            self.textbox_client_state = wx.TextCtrl(panel_client_intel, -1, pos=(10, 270), size=(60, 30))
        wx.StaticText(panel_client_intel, -1, u'Cidade:', pos=(100, 250))
        self.textbox_client_city = wx.TextCtrl(panel_client_intel, -1, pos=(100, 270), size=(150, 30))
        wx.StaticText(panel_client_intel, -1, u'Bairro:', pos=(280, 250))
        self.textbox_client_district = wx.TextCtrl(panel_client_intel, -1, pos=(280, 270), size=(150, 30))
        wx.StaticText(panel_client_intel, -1, u'Endereço:', pos=(10, 310))
        self.textbox_client_address = wx.TextCtrl(panel_client_intel, -1, pos=(10, 330), size=(300, 30))
        wx.StaticText(panel_client_intel, -1, u'Observações:', pos=(10, 370))
        self.textbox_client_observations = wx.TextCtrl(panel_client_intel, -1, pos=(10, 390), size=(480, 100),
                                                       style=wx.TE_MULTILINE)
        self.panel_client_image = wx.Panel(panel_client_intel, -1, size=(150, 150), pos=(10, 25),
                                           style=wx.SIMPLE_BORDER)
        self.panel_client_image.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.panel_client_image, self.OnPaint)
        panel_bottom = wx.Panel(self, -1, pos=(0, 500), size=(500, 50))
        if self.editable:
            panel_bottom_buttons = wx.Panel(panel_bottom, pos=(90, 5), size=(320, 40), style=wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                         u"Salvar", pos=(0, 0), size=(100, 40))
            finish.Bind(wx.EVT_BUTTON, self.ask_delete)
            restart = GenBitmapTextButton(panel_bottom_buttons, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                          u"Recomeçar", pos=(100, 0), size=(120, 40))
            restart.Bind(wx.EVT_BUTTON, self.ask_clean)
            cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(220, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
        else:
            panel_bottom_buttons = wx.Panel(panel_bottom, pos=(150, 5), size=(200, 40), style=wx.SIMPLE_BORDER)
            edipo = GenBitmapTextButton(panel_bottom_buttons, -1,
                                        wx.Bitmap(core.directory_paths['icons'] + 'Edit.png', wx.BITMAP_TYPE_PNG),
                                        u"Editar", pos=(0, 0), size=(100, 40))
            edipo.Bind(wx.EVT_BUTTON, self.set_editable)
            cancel = GenBitmapTextButton(panel_bottom_buttons, -1,
                                         wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                         u"Sair",
                                         pos=(100, 0), size=(100, 40))
            cancel.Bind(wx.EVT_BUTTON, self.ask_exit)
        panel_side = wx.Panel(self, -1, pos=(500, 10), size=(340, 530), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.textbox_client_intel = wx.TextCtrl(panel_side, -1, pos=(10, 10), size=(320, 100),
                                                style=wx.TE_MULTILINE | wx.NO_BORDER)
        self.textbox_client_intel.SetBackgroundColour(core.default_background_color)
        if self.editable:
            bp1 = wx.Panel(panel_side, -1, pos=(20, 120), size=(300, 40), style=wx.SIMPLE_BORDER)
            sunbind = GenBitmapTextButton(bp1, -1,
                                          wx.Bitmap(core.directory_paths['icons'] + 'list-remove.png',
                                                    wx.BITMAP_TYPE_PNG),
                                          u'Desconectar Venda', pos=(120, 0), size=(180, 40))
            sunbind.Bind(wx.EVT_BUTTON, self.ask_sale_disconnect)
            ssee = GenBitmapTextButton(bp1, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'edit_find.png', wx.BITMAP_TYPE_PNG),
                                       u'Ver Mais', pos=(0, 0), size=(120, 40))
            ssee.Bind(wx.EVT_BUTTON, self.sale_view)
        else:
            bp1 = wx.Panel(panel_side, -1, pos=(110, 120), size=(120, 40), style=wx.SIMPLE_BORDER)
            ssee = GenBitmapTextButton(bp1, -1,
                                       wx.Bitmap(core.directory_paths['icons'] + 'edit_find.png', wx.BITMAP_TYPE_PNG),
                                       u'Ver Mais', pos=(0, 0), size=(120, 40))
            ssee.Bind(wx.EVT_BUTTON, self.sale_view)
        self.list_bought = wx.ListCtrl(panel_side, -1, pos=(10, 170), size=(320, 350),
                                       style=wx.LC_VRULES | wx.LC_HRULES | wx.LC_REPORT | wx.SIMPLE_BORDER)
        self.list_bought.InsertColumn(0, u'Data/Horário', width=180)
        self.list_bought.InsertColumn(1, u'Valor', width=140)
        self.clean()
        if self.editable == 0:
            self.textbox_client_name.Disable()
            self.textbox_client_name.SetBackgroundColour('#C6C6C6')
            self.textbox_client_sex.Disable()
            self.textbox_client_sex.SetBackgroundColour('#C6C6C6')
            self.textbox_client_birth.Disable()
            self.textbox_client_birth.SetBackgroundColour('#C6C6C6')
            self.textbox_client_telephone_1.Disable()
            self.textbox_client_telephone_1.SetBackgroundColour('#C6C6C6')
            self.textbox_client_telephone_2.Disable()
            self.textbox_client_telephone_2.SetBackgroundColour('#C6C6C6')
            self.textbox_client_email.Disable()
            self.textbox_client_email.SetBackgroundColour('#C6C6C6')
            self.textbox_client_cpf.Disable()
            self.textbox_client_cpf.SetBackgroundColour('#C6C6C6')
            self.textbox_client_state.Disable()
            self.textbox_client_state.SetBackgroundColour('#C6C6C6')
            self.textbox_client_city.Disable()
            self.textbox_client_city.SetBackgroundColour('#C6C6C6')
            self.textbox_client_district.Disable()
            self.textbox_client_district.SetBackgroundColour('#C6C6C6')
            self.textbox_client_address.Disable()
            self.textbox_client_address.SetBackgroundColour('#C6C6C6')
            self.textbox_client_observations.Disable()

    def ask_delete(self, event):
        dialogs.Ask(self, u'Finalizar Cadastro', 14)

    def ask_clean(self, event):
        dialogs.Ask(self, u'Recomeçar', 1)

    def ask_exit(self, event):
        if self.editable:
            dialogs.Ask(self, u'Sair', 91)
        elif not self.editable:
            self.exit(None)

    def ask_sale_disconnect(self, event):
        dialogs.Ask(self, u'Desconectar', 40)

    def set_editable(self, event):
        ClientData(self.parent, self.title, self.client_id, True)
        self.Close()

    def sale_view(self, event):
        t = self.list_bought.GetFocusedItem()
        if t == -1:
            return
        tex = self.list_bought.GetItemText(t, 0)
        try:
            j = shelve.open(core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_deals.txt')
            r = j[self.dict_clients_basic_data[tex]]
            j.close()
        except KeyError:
            dialogs.launch_error(self, 'Não há mais registro dessa venda')
            return
        sale.Sale(self, tex,
                  [(core.directory_paths['saves'] + self.dict_clients_basic_data[tex][:10] + '.txt'), r['key'],
                   r['time']], False)

    def sale_disconnect(self):
        t = self.list_bought.GetFocusedItem()
        if t == -1:
            return
        tex = self.list_bought.GetItemText(t, 0)
        j = shelve.open(core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_deals.txt')
        r = j[self.dict_clients_basic_data[tex]]
        del j[self.dict_clients_basic_data[tex]]
        s = shelve.open(core.directory_paths['saves'] + self.dict_clients_basic_data[tex][:10] + '.txt')
        v = s['sales'][r['client_id']]
        if v['client_id'] == self.client_id:
            v['client_name'] = ''
            v['client_id'] = ''
            u = s['sales']
            u[r['client_id']] = v
            s['sales'] = u
        s.close()
        j.close()
        self.sales_list()

    def sales_list(self):
        self.list_bought.DeleteAllItems()
        s = shelve.open(core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_infos.txt')
        bat = s['date']
        dat = bat.split('-')
        cat = dat[2] + '/' + dat[1] + '/' + dat[0]
        s.close()
        sn = 0
        tv = 0.0
        cc = 0
        cv = 0.0
        mc = 0
        mv = 0.0
        self.dict_clients_basic_data = {}
        y = shelve.open(core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_deals.txt')
        for o in y:
            dt = o.split('_')
            dt[1] = dt[1].replace('-', ':')
            der = dt[0].split('-')
            der.reverse()
            dt[0] = '/'.join(der)
            fdt = '   '.join(dt)
            self.dict_clients_basic_data[fdt] = o
            self.list_bought.Append((fdt, 'R$ ' + core.good_show('money', y[o]['value'])))
            sn += 1
            tv += y[o]['value']
            if u'Dinheiro' == y[o]['payment']:
                mc += 1
                mv += y[o]['value']
            elif u'Cartão' == y[o]['payment']:
                cc += 1
                cv += y[o]['value']
        y.close()
        self.textbox_client_intel.SetValue(
            u'Cliente desde %s \n'
            u'Já gastou R$ %s na Canela Santa através de %i compras, das quais %i, no valor de R$ %s, '
            u'foram pagas em dinheiro e %i, no valor de R$ %s, foram pagas no cartão.'
            % (cat, core.good_show('money',
                                   str(tv)).replace('.', ','), sn, mc, core.good_show('money',
                                                                                      str(mv)).replace('.', ','), cc,
               core.good_show('money',
                              str(cv)).replace('.', ',')))

    def clean(self):
        p = shelve.open(core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_infos.txt')
        self.textbox_client_name.SetValue(p['name'])
        self.textbox_client_sex.SetValue(p['sex'])
        self.textbox_client_birth.SetValue(p['birth'])
        self.textbox_client_telephone_1.SetValue(p['tel1'])
        self.textbox_client_telephone_2.SetValue(p['tel2'])
        self.textbox_client_email.SetValue(p['email'])
        self.textbox_client_state.SetValue(p['state'])
        self.textbox_client_city.SetValue(p['city'])
        self.textbox_client_district.SetValue(p['hood'])
        self.textbox_client_address.SetValue(p['adress'])
        self.textbox_client_observations.SetValue(p['obs'])
        self.sales_list()
        p.close()

    def end(self):
        if not self.textbox_client_name.GetValue():
            a = wx.MessageDialog(self, u'É necessário o nome para o cadastro', u'Error 404',
                                 style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        rtime = core.good_show("o", str(datetime.now().hour)) + "-" + core.good_show("o", str(
                datetime.now().minute)) + "-" + core.good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
                "o", str(datetime.now().day))
        dt = '%s_%s' % (rdate, rtime)
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/clients'):
            os.mkdir('#Trash/clients')
        if not os.path.exists('#Trash/clients/edited'):
            os.mkdir('#Trash/clients/edited')
        if not os.path.exists('#Trash/clients/edited/' + self.client_id):
            os.mkdir('#Trash/clients/edited/' + self.client_id)
        shutil.copytree('clients/' + self.client_id, '#Trash/clients/edited/%s/%s' % (self.client_id, dt))
        po = (core.directory_paths['clients'] + self.client_id + core.slash + self.client_id + '_infos.txt')
        s = shelve.open(po)
        xname = self.textbox_client_name.GetValue()
        while xname[0] == ' ':
            xname = xname[1:]
        names = xname.split()
        for i in range(0, len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['name'] = namef
        s['name'] = self.textbox_client_name.GetValue()
        s['sex'] = self.textbox_client_sex.GetValue()
        s['birth'] = self.textbox_client_birth.GetValue()
        s['email'] = self.textbox_client_email.GetValue()
        s['tel1'] = self.textbox_client_telephone_1.GetValue()
        s['tel2'] = self.textbox_client_telephone_2.GetValue()
        s['cpf'] = self.textbox_client_cpf.GetValue()
        s['state'] = self.textbox_client_state.GetValue()
        s['city'] = self.textbox_client_city.GetValue()
        s['hood'] = self.textbox_client_district.GetValue()
        s['adress'] = self.textbox_client_address.GetValue()
        s['obs'] = self.textbox_client_observations.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        if type(self.GetParent()) is ClientManager:
            self.GetParent().setup(None)
        self.exit(None)

    def exit(self, event):
        self.Close()
