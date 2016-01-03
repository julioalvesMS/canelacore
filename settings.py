#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import os
import pickle
import shelve

import wx
import wx.gizmos

import core

__author__ = 'Julio'


class SettingsMenu(wx.Frame):
    notebook_settings = None

    checkbox_auto_update = None
    auto_update = False

    panel_password = None
    textbox_old_password = None
    textbox_new_password_1 = None
    textbox_new_password_2 = None
    textbox_password_notifier = None

    def __init__(self, parent, frame_id=-1, title=u'Configurações'):
        wx.Frame.__init__(self, parent, frame_id, title, size=(550, 400),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.setup()

        self.setup_gui()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        self.notebook_settings = wx.Notebook(self, pos=(5, 5), style=wx.LEFT)
        # --Geral
        # buscar atualizações
        general = wx.Panel(self.notebook_settings)
        panel_update = wx.Panel(general, pos=(10, 20), size=(515, 150), style=wx.SIMPLE_BORDER)
        wx.StaticText(panel_update, -1, u'Atualizações', pos=(210, 5))
        self.checkbox_auto_update = wx.CheckBox(panel_update, -1, u'Buscar atualizações automaticamente?', (10, 50))
        self.checkbox_auto_update.SetValue(self.auto_update)
        # --Security
        # escolher quais lugares precisam de senha
        panel_security = wx.Panel(self.notebook_settings)
        self.panel_password = wx.Panel(panel_security, pos=(10, 20), size=(515, 150), style=wx.SIMPLE_BORDER)
        wx.StaticText(self.panel_password, -1, u'Alteração de senha', pos=(210, 5))
        wx.StaticText(self.panel_password, -1, u'Senha Atual:', pos=(100, 25))
        wx.StaticText(self.panel_password, -1, u'Nova Senha:', pos=(300, 25))
        wx.StaticText(self.panel_password, -1, u'Repita a nova senha:', pos=(300, 80))
        self.textbox_old_password = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(100, 45),
                                                style=wx.TE_PASSWORD)
        self.textbox_new_password_1 = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(300, 45),
                                                  style=wx.TE_PASSWORD)
        self.textbox_new_password_2 = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(300, 100),
                                                  style=wx.TE_PASSWORD)
        button_change_password = wx.Button(self.panel_password, -1, u'Alterar Senha', pos=(100, 90))
        self.textbox_password_notifier = wx.TextCtrl(self.panel_password, -1, size=(150, 25), pos=(100, 125),
                                                     style=wx.NO_BORDER | wx.TE_READONLY)
        self.textbox_password_notifier.SetBackgroundColour('#D6D6D6')
        button_change_password.Bind(wx.EVT_BUTTON, self.change_password)
        # Custom
        # logo da empresa, backgrounds
        custom = wx.Panel(self.notebook_settings)

        self.notebook_settings.AddPage(general, u'Geral')
        self.notebook_settings.AddPage(panel_security, u'Segurança')
        self.notebook_settings.AddPage(custom, u'Customizações')

        wx.EVT_PAINT(self.panel_password, self.OnPaint)

    def OnPaint(self, event):
        lok = wx.Bitmap(core.directory_paths['icons'] + 'Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self.panel_password).DrawBitmap(lok, 0, 30)

    def setup(self):
        if not os.path.exists('preferences'):
            os.mkdir('preferences')
        general_file = shelve.open(core.directory_paths['preferences'] + 'general.txt')
        if 'Auto Update' not in general_file:
            general_file['Auto Update'] = True
        self.auto_update = general_file['Auto Update']
        general_file.close()

    def change_password(self, event):
        if self.textbox_new_password_1.GetValue() != self.textbox_new_password_2.GetValue():
            self.textbox_password_notifier.SetValue(u'As senhas são diferentes!')
            self.textbox_password_notifier.SetForegroundColour('red')
            return
        if core.password_check(self.textbox_old_password.GetValue()):
            hex_pass = hashlib.sha256(self.textbox_new_password_1.GetValue()).hexdigest()
            pickle.dump(hex_pass, open(core.directory_paths['preferences'] + 'accounts.p', 'wb'))
            self.textbox_password_notifier.SetValue(u'Senha alterada com sucesso!')
            self.textbox_password_notifier.SetForegroundColour('#009900')
            self.textbox_old_password.Clear()
            self.textbox_new_password_1.Clear()
            self.textbox_new_password_2.Clear()
            return
        else:
            self.textbox_password_notifier.SetValue(u'Senha Incorreta!')
            self.textbox_password_notifier.SetForegroundColour('red')
            return

    def exit(self, event):
        self.Close()
