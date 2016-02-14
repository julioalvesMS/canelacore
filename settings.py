#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import pickle
import ConfigParser

import wx
from wx.lib.buttons import GenBitmapTextButton
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

    textbox_sat_cupom = None

    def __init__(self, parent, frame_id=-1, title=u'Configurações'):
        wx.Frame.__init__(self, parent, frame_id, title, size=(555, 430),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup()

        self.Show()

    def setup_gui(self):
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.notebook_settings = wx.Notebook(self, pos=(5, 5), size=(540, 340), style=wx.LEFT)
        # --Geral--
        # buscar atualizações
        page_general = wx.Panel(self.notebook_settings)
        panel_update = wx.StaticBox(page_general, -1, u'Atualizações', pos=(10, 10), size=(515, 150))
        self.checkbox_auto_update = wx.CheckBox(panel_update, -1, u'Buscar atualizações automaticamente?', (15, 50))
        self.checkbox_auto_update.SetValue(self.auto_update)
        # --Security--
        # escolher quais lugares precisam de senha
        page_security = wx.Panel(self.notebook_settings)
        self.panel_password = wx.Panel(page_security, pos=(10, 20), size=(515, 150), style=wx.SIMPLE_BORDER)
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
        button_change_password.Bind(wx.EVT_BUTTON, self.change_password)
        # --SAT--
        # configurações do SAT
        page_sat = wx.Panel(self.notebook_settings)

        panel_cupons = wx.StaticBox(page_sat, wx.ID_ANY, u'Cupons Fiscais', pos=(10, 10), size=(515, 100))

        wx.StaticText(panel_cupons, wx.ID_ANY, u'Salvar cupons em: ', pos=(10, 50))
        self.textbox_sat_cupom = wx.TextCtrl(panel_cupons, wx.ID_ANY, pos=(10, 70), size=(420, -1))
        button_sat_cupom_location = wx.Button(panel_cupons, wx.ID_ANY, u'Buscar', pos=(440, 70), size=(65, -1))

        button_sat_cupom_location.Bind(wx.EVT_BUTTON, self.open_directory_selector)

        self.textbox_sat_cupom.Disable()

        # --Custom--
        # logo da empresa, backgrounds
        page_custom = wx.Panel(self.notebook_settings)

        # --Barra inferior--
        panel_bottom = wx.Panel(self, size=(540, 50), pos=(5, 345))

        panel_buttons = wx.Panel(panel_bottom, size=(300, 40), pos=(200, 5), style=wx.SIMPLE_BORDER)
        button_ok = GenBitmapTextButton(panel_buttons, -1, wx.Bitmap(core.directory_paths['icons'] + 'Save.png'),
                                        u'OK', size=(100, 40), pos=(0, 0))
        button_apply = GenBitmapTextButton(panel_buttons, -1, wx.Bitmap(core.directory_paths['icons'] + 'Check.png'),
                                           u'Aplicar', size=(100, 40), pos=(100, 0))
        button_cancel = GenBitmapTextButton(panel_buttons, -1, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                            u'Sair', size=(100, 40), pos=(200, 0))

        button_ok.Bind(wx.EVT_BUTTON, self.save_and_exit)
        button_apply.Bind(wx.EVT_BUTTON, self.save)
        button_cancel.Bind(wx.EVT_BUTTON, self.exit)

        # --Prepare Notbook--
        self.notebook_settings.AddPage(page_general, u'Geral')
        self.notebook_settings.AddPage(page_security, u'Segurança')
        self.notebook_settings.AddPage(page_sat, u'SAT')
        self.notebook_settings.AddPage(page_custom, u'Customizações')

        wx.EVT_PAINT(self.panel_password, self.OnPaint)

    def OnPaint(self, event):
        lok = wx.Bitmap(core.directory_paths['icons'] + 'Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self.panel_password).DrawBitmap(lok, 0, 30)

    def setup(self):

        auto_update = config2type(CONFIG.get(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_UPDATE), bool)
        cupons_path = config2type(CONFIG.get(CONFIG_SECTION_SAT, CONFIG_FIELD_CUPOM_PATH), str)

        self.checkbox_auto_update.SetValue(auto_update)
        self.textbox_sat_cupom.SetValue(cupons_path)

    def save(self, event):
        auto_update = self.checkbox_auto_update.GetValue()
        cupons_path = self.textbox_sat_cupom.GetValue()

        CONFIG.set(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_UPDATE, type2config(auto_update))
        CONFIG.set(CONFIG_SECTION_SAT, CONFIG_FIELD_CUPOM_PATH, type2config(cupons_path))

        save_config()

    def save_and_exit(self, event):
        self.save(event)
        self.exit(event)

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
            self.textbox_password_notifier.SetForegroundColour(wx.RED)
            return

    def open_directory_selector(self, event):

        default_path = self.textbox_sat_cupom.GetValue()

        loc = wx.DirDialog(self, u'Salvar cupons em', default_path)
        loc.ShowModal()
        loc.Destroy()

        new_path = loc.GetPath()

        if new_path == default_path:
            return

        self.textbox_sat_cupom.SetValue(new_path)

    def exit(self, event):
        self.Close()


def type2config(entry):
    data_type = type(entry)

    def _bool(_entry):
        return str(_entry)

    def _str(_entry):
        return _entry

    functions = {
        str: _str,
        bool: _bool
    }

    return functions.get(data_type, str)(entry)


def config2type(entry, data_type):

    def _bool(_entry):
        return True if _entry == 'True' else False

    def _str(_entry):
        return _entry

    def _int(_entry):
        return int(_entry)

    functions = {
        str: _str,
        bool: _bool,
        int: _int
    }

    return functions.get(data_type, str)(entry)


def load_config():
    config = ConfigParser.ConfigParser()
    config.read(FILE_CONFIG)
    create_config(config)

    return config


def save_config():
    # save to a file
    with open(FILE_CONFIG, 'w') as configfile:
        CONFIG.write(configfile)


def create_config(config=None):
    """
    Cria um arquivo de configuração para armazenar as preferencias do usuario
    :param config: ConfigParser Object
    :type config: ConfigParser.ConfigParser
    :return:
    """
    if not config:
        config = ConfigParser.ConfigParser()

    # Adiciona as seções
    for section in CONFIG_DATA:
        if not config.has_section(section):
            config.add_section(section)

        # Aciciona os campos de cada seção
        for field in CONFIG_DATA[section]:
            if not config.has_option(section, field):
                print section, field
                config.set(section, field, type2config(CONFIG_DATA[section][field]))

    # save to a file
    with open(FILE_CONFIG, 'w') as configfile:
        config.write(configfile)

    return config


FILE_CONFIG = core.current_dir + 'config.ini'

CONFIG_FIELD_AUTO_UPDATE = 'AUTO_UPDATE'
CONFIG_FIELD_AUTO_BACKUP = 'AUTO_BACKUP'

CONFIG_FIELD_UPDATE_IMPOSTO_INTERVAL = 'IMPOSTO_UPDATE_INTERVAL'
CONFIG_FIELD_LAST_UPDATE_IMPOSTO = 'IMPOSTO_LAST_UPDATE'

CONFIG_FIELD_CUPOM_PATH = 'CUPONS_PATH'

CONFIG_DATA_GENERAL = {
    CONFIG_FIELD_AUTO_UPDATE: True,
    CONFIG_FIELD_AUTO_BACKUP: True
}

CONFIG_DATA_SAT = {
    CONFIG_FIELD_UPDATE_IMPOSTO_INTERVAL: 30,
    CONFIG_FIELD_LAST_UPDATE_IMPOSTO: '0-0-0',
    CONFIG_FIELD_CUPOM_PATH: core.directory_paths['cupons_fiscais']
}


CONFIG_SECTION_GENERAL = 'GENERAL'
CONFIG_SECTION_SAT = 'SAT'

CONFIG_DATA = {
    CONFIG_SECTION_GENERAL: CONFIG_DATA_GENERAL,
    CONFIG_SECTION_SAT: CONFIG_DATA_SAT
}

CONFIG = load_config()
