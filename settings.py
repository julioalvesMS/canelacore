#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import pickle
import ConfigParser

import wx
from wx.lib.buttons import GenBitmapTextButton
import wx.gizmos

import dialogs
import core
import core_gui as gui

__author__ = 'Julio'


class SettingsMenu(wx.Frame):

    notebook_settings = None

    page_general = None
    page_notification = None
    page_security = None
    page_sat = None
    page_custom = None

    def __init__(self, parent, frame_id=wx.ID_ANY, title=u'Configurações'):
        wx.Frame.__init__(self, parent, frame_id, title, size=(800, 430),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.setup_gui()

        self.setup()

        self.Show()

    def setup_gui(self):
        sizer = wx.FlexGridSizer(2, 1)
        self.Centre()
        self.SetIcon(wx.Icon(core.ICON_MAIN, wx.BITMAP_TYPE_ICO))
        self.notebook_settings = wx.Notebook(self, size=(800, 350), style=wx.LEFT)

        # --Geral--
        self.page_general = GeneralPanel(self.notebook_settings)

        # --Notificações--
        self.page_notification = NotificationPanel(self.notebook_settings)

        # --Security--
        self.page_security = SecurityPanel(self.notebook_settings)

        # --SAT--
        self.page_sat = SATPanel(self.notebook_settings)

        # --Custom--
        # logo da empresa, backgrounds
        self.page_custom = wx.Panel(self.notebook_settings)

        # --Barra inferior--
        panel_bottom = wx.Panel(self, size=(800, 50))

        panel_buttons = wx.Panel(panel_bottom, size=(300, 40), pos=(450, 5), style=wx.SIMPLE_BORDER)
        button_ok = GenBitmapTextButton(panel_buttons, bitmap=wx.Bitmap(core.directory_paths['icons'] + 'Save.png'),
                                        label=u'OK', size=(100, 40), pos=(0, 0))
        button_apply = GenBitmapTextButton(panel_buttons, bitmap=wx.Bitmap(core.directory_paths['icons'] + 'Check.png'),
                                           label=u'Aplicar', size=(100, 40), pos=(100, 0))
        button_cancel = GenBitmapTextButton(panel_buttons, bitmap=wx.Bitmap(core.directory_paths['icons'] + 'Exit.png'),
                                            label=u'Sair', size=(100, 40), pos=(200, 0))

        button_ok.Bind(wx.EVT_BUTTON, self.save_and_exit)
        button_apply.Bind(wx.EVT_BUTTON, self.save)
        button_cancel.Bind(wx.EVT_BUTTON, self.exit)

        # --Prepare Notbook--
        self.notebook_settings.AddPage(self.page_general, u'Geral')
        self.notebook_settings.AddPage(self.page_security, u'Segurança')
        self.notebook_settings.AddPage(self.page_sat, u'SAT')
        self.notebook_settings.AddPage(self.page_notification, u'Notificações')
        self.notebook_settings.AddPage(self.page_custom, u'Customizações')

        sizer.Add(self.notebook_settings)
        sizer.Add(panel_bottom)
        self.SetSizer(sizer)

    def setup(self):
        self.page_general.setup()
        self.page_sat.setup()
        self.page_notification.setup()

    def save(self, event):
        self.page_general.save()
        self.page_sat.save()
        self.page_notification.save()

        save_config()

        import routines
        routines.update_routines()

    def save_and_exit(self, event):
        self.save(event)
        self.exit(event)

    def exit(self, event):
        self.Close()


class GeneralPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        sizer_general = wx.BoxSizer(wx.VERTICAL)

        panel_update = wx.StaticBox(self, wx.ID_ANY, u'Atualizações', size=(780, 140))
        self.checkbox_auto_update = wx.CheckBox(panel_update, wx.ID_ANY, u'Buscar atualizações automaticamente',
                                                pos=(15, 50))
        self.panel_update_frequency = gui.FrequencyPanel(panel_update, pos=(15, 90))
        self.checkbox_auto_update.Bind(wx.EVT_CHECKBOX, self.panel_update_frequency.change_enable)

        panel_backup = wx.StaticBox(self, wx.ID_ANY, u'Backups', size=(780, 140))
        self.checkbox_auto_backup = wx.CheckBox(panel_backup, wx.ID_ANY, u'Realizar backups automaticamente', (15, 50))
        self.panel_backup_frequency = gui.FrequencyPanel(panel_backup, pos=(15, 90))
        self.checkbox_auto_backup.Bind(wx.EVT_CHECKBOX, self.panel_backup_frequency.change_enable)

        sizer_general.Add(panel_update)
        sizer_general.AddSpacer(10)
        sizer_general.Add(panel_backup)

        self.SetSizer(sizer_general)

    def save(self):
        auto_update = self.checkbox_auto_update.GetValue()
        auto_backup = self.checkbox_auto_backup.GetValue()

        backup_frequency = self.panel_backup_frequency.get_string_selections()

        CONFIG.set(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_UPDATE, type2config(auto_update))
        CONFIG.set(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_BACKUP, type2config(auto_backup))
        CONFIG.set(CONFIG_SECTION_GENERAL, CONFIG_FIELD_BACKUP_FREQUENCY, type2config(backup_frequency))

    def setup(self):

        auto_update = config2type(CONFIG.get(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_UPDATE), bool)
        auto_backup = config2type(CONFIG.get(CONFIG_SECTION_GENERAL, CONFIG_FIELD_AUTO_BACKUP), bool)
        backup_frequency = config2type(CONFIG.get(CONFIG_SECTION_GENERAL, CONFIG_FIELD_BACKUP_FREQUENCY), str)

        backup_frequency_selections = gui.FrequencyPanel.get_selections_from_string(backup_frequency)

        setup_enabled(self.panel_update_frequency, auto_update)
        setup_enabled(self.panel_backup_frequency, auto_backup)

        self.checkbox_auto_update.SetValue(auto_update)
        self.checkbox_auto_backup.SetValue(auto_backup)
        self.panel_backup_frequency.set_selections(backup_frequency_selections)


class SecurityPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.panel_password = wx.Panel(self, pos=(10, 20), size=(760, 150), style=wx.SIMPLE_BORDER)
        wx.StaticText(self.panel_password, wx.ID_ANY, u'Alteração de senha', pos=(210, 5))
        wx.StaticText(self.panel_password, wx.ID_ANY, u'Senha Atual:', pos=(100, 25))
        wx.StaticText(self.panel_password, wx.ID_ANY, u'Nova Senha:', pos=(300, 25))
        wx.StaticText(self.panel_password, wx.ID_ANY, u'Repita a nova senha:', pos=(300, 80))
        self.textbox_old_password = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(100, 45),
                                                style=wx.TE_PASSWORD)
        self.textbox_new_password_1 = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(300, 45),
                                                  style=wx.TE_PASSWORD)
        self.textbox_new_password_2 = wx.TextCtrl(self.panel_password, size=(150, 30), pos=(300, 100),
                                                  style=wx.TE_PASSWORD)
        button_change_password = wx.Button(self.panel_password, wx.ID_ANY, u'Alterar Senha', pos=(100, 90))
        self.textbox_password_notifier = wx.TextCtrl(self.panel_password, wx.ID_ANY, size=(150, 25), pos=(100, 125),
                                                     style=wx.NO_BORDER | wx.TE_READONLY)
        button_change_password.Bind(wx.EVT_BUTTON, self.change_password)

        wx.EVT_PAINT(self.panel_password, self.OnPaint)

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

    def OnPaint(self, event):
        lok = wx.Bitmap(core.directory_paths['icons'] + 'Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self.panel_password).DrawBitmap(lok, 0, 30)


class SATPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        panel_cupons = wx.StaticBox(self, wx.ID_ANY, u'Cupons Fiscais', pos=(10, 10), size=(760, 100))

        wx.StaticText(panel_cupons, wx.ID_ANY, u'Salvar cupons em: ', pos=(10, 50))
        self.textbox_sat_cupom = wx.TextCtrl(panel_cupons, wx.ID_ANY, pos=(10, 70), size=(420, -1))
        button_sat_cupom_location = wx.Button(panel_cupons, wx.ID_ANY, u'Buscar', pos=(440, 70), size=(65, -1))

        button_sat_cupom_location.Bind(wx.EVT_BUTTON, self.open_directory_selector)

        self.textbox_sat_cupom.Disable()

    def setup(self):

        cupons_path = config2type(CONFIG.get(CONFIG_SECTION_SAT, CONFIG_FIELD_CUPOM_PATH), str)

        self.textbox_sat_cupom.SetValue(cupons_path)

    def save(self):
        cupons_path = self.textbox_sat_cupom.GetValue()

        CONFIG.set(CONFIG_SECTION_SAT, CONFIG_FIELD_CUPOM_PATH, type2config(cupons_path))

    def open_directory_selector(self, event):
        default_path = self.textbox_sat_cupom.GetValue()
        new_path = dialogs.lauch_directory_selector(self, u'Salvar cupons em', default_path)

        if new_path:
            self.textbox_sat_cupom.SetValue(new_path)


class NotificationPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        sizer_general = wx.BoxSizer(wx.VERTICAL)

        panel_transaction = wx.StaticBox(self, wx.ID_ANY, u'Contas e Entradas', size=(780, 140))
        text_transaction = wx.StaticText(panel_transaction, wx.ID_ANY, u'Notificações de Contas e Entradas pendentes',
                                         pos=(150, 25))
        text_transaction.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.checkbox_expenses = wx.CheckBox(self, wx.ID_ANY, u'Contas', pos=(15, 70))
        self.checkbox_incomes = wx.CheckBox(self, wx.ID_ANY, u'Entradas', pos=(90, 70))
        self.panel_transaction_frequency = gui.FrequencyPanel(self, pos=(15, 110))

        self.checkbox_expenses.Bind(wx.EVT_CHECKBOX, self.transaction_change_enable)
        self.checkbox_incomes.Bind(wx.EVT_CHECKBOX, self.transaction_change_enable)

        sizer_general.Add(self)
        sizer_general.AddSpacer(10)
        sizer_general.Add(panel_transaction)

        self.SetSizer(sizer_general)

    def setup(self):

        notify_expenses = config2type(CONFIG.get(CONFIG_SECTION_NOTIFICATIONS, CONFIG_FIELD_NOTIFY_EXPENSES), bool)
        notify_incomes = config2type(CONFIG.get(CONFIG_SECTION_NOTIFICATIONS, CONFIG_FIELD_NOTIFY_INCOMES), bool)
        transaction_frequency = config2type(CONFIG.get(CONFIG_SECTION_NOTIFICATIONS,
                                                       CONFIG_FIELD_TRANSACTIONS_FREQUENCY), str)

        transactions_selections = gui.FrequencyPanel.get_selections_from_string(transaction_frequency)

        self.checkbox_expenses.SetValue(notify_expenses)
        self.checkbox_incomes.SetValue(notify_incomes)
        self.panel_transaction_frequency.set_selections(transactions_selections)

        setup_enabled(self.panel_transaction_frequency, notify_expenses or notify_incomes)

    def save(self):
        notify_expenses = self.checkbox_expenses.GetValue()
        notify_incomes = self.checkbox_incomes.GetValue()
        transactions_frequency = self.panel_transaction_frequency.get_string_selections()

        CONFIG.set(CONFIG_SECTION_NOTIFICATIONS, CONFIG_FIELD_NOTIFY_EXPENSES, type2config(notify_expenses))
        CONFIG.set(CONFIG_SECTION_NOTIFICATIONS, CONFIG_FIELD_NOTIFY_INCOMES, type2config(notify_incomes))
        CONFIG.set(CONFIG_SECTION_NOTIFICATIONS, CONFIG_FIELD_TRANSACTIONS_FREQUENCY,
                   type2config(transactions_frequency))

    def transaction_change_enable(self, event):
        if self.checkbox_expenses.GetValue() or self.checkbox_incomes.GetValue():
            self.panel_transaction_frequency.Enable()
        else:
            self.panel_transaction_frequency.Disable()


def setup_enabled(window, activate=True):
    """
    Deixa uma sessão da GUI inativa ou ativa, de acordo com o ideal, especificado pelo param activate
    :param wx.Window window:
    :param bool activate: Diz se o Window deveria estar ativado ou desativado
    :return:
    """
    if activate and not window.IsEnabled():
        window.Enable()
    elif not activate and window.IsEnabled():
        window.Disable()


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

    return functions.get(data_type)(entry)


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
                config.set(section, field, type2config(CONFIG_DATA[section][field]))

    # save to a file
    with open(FILE_CONFIG, 'w') as configfile:
        config.write(configfile)

    return config


FILE_CONFIG = core.current_dir + 'config.ini'

CONFIG_FIELD_AUTO_UPDATE = 'AUTO_UPDATE'
CONFIG_FIELD_AUTO_BACKUP = 'AUTO_BACKUP'
CONFIG_FIELD_UPDATE_FREQUENCY = 'UPDATE_FREQUENCY'
CONFIG_FIELD_BACKUP_FREQUENCY = 'BACKUP_FREQUENCY'

CONFIG_FIELD_UPDATE_IMPOSTO_INTERVAL = 'IMPOSTO_UPDATE_INTERVAL'
CONFIG_FIELD_LAST_UPDATE_IMPOSTO = 'IMPOSTO_LAST_UPDATE'
CONFIG_FIELD_CUPOM_PATH = 'CUPONS_PATH'

CONFIG_FIELD_NOTIFY_EXPENSES = 'NOTIFY_EXPENSES'
CONFIG_FIELD_NOTIFY_INCOMES = 'NOTIFY_INCOMES'
CONFIG_FIELD_TRANSACTIONS_FREQUENCY = 'TRANSACTIONS_FREQUENCY'

CONFIG_DATA_GENERAL = {
    CONFIG_FIELD_AUTO_UPDATE: True,
    CONFIG_FIELD_AUTO_BACKUP: True,
    CONFIG_FIELD_UPDATE_FREQUENCY: ' 12:30',
    CONFIG_FIELD_BACKUP_FREQUENCY: ' 12:30'
}

CONFIG_DATA_SAT = {
    CONFIG_FIELD_UPDATE_IMPOSTO_INTERVAL: 30,
    CONFIG_FIELD_LAST_UPDATE_IMPOSTO: '0-0-0',
    CONFIG_FIELD_CUPOM_PATH: core.directory_paths['cupons_fiscais']
}


CONFIG_DATA_NOTIFICATIONS = {
    CONFIG_FIELD_NOTIFY_EXPENSES: True,
    CONFIG_FIELD_NOTIFY_INCOMES: True,
    CONFIG_FIELD_TRANSACTIONS_FREQUENCY: ' 12:30'
}

CONFIG_SECTION_GENERAL = 'GENERAL'
CONFIG_SECTION_SAT = 'SAT'
CONFIG_SECTION_NOTIFICATIONS = 'NOTIFICATIONS'

CONFIG_DATA = {
    CONFIG_SECTION_GENERAL: CONFIG_DATA_GENERAL,
    CONFIG_SECTION_SAT: CONFIG_DATA_SAT,
    CONFIG_SECTION_NOTIFICATIONS: CONFIG_DATA_NOTIFICATIONS
}

CONFIG = load_config()
