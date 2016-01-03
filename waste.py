#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
from datetime import datetime

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import core
import dialogs

__author__ = 'Julio'


class Waste(wx.Frame):
    
    textbox_description = None
    textbox_amount = None
    textbox_value = None

    def __init__(self, parent, title=u'Desperdícios', argv=None):
        wx.Frame.__init__(self, parent, -1, title, size=(500, 200),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        if not argv:
            argv = []
        
        self.argv = argv
        
        self.setup_gui()
        
        if argv:
            self.recover_waste()

        self.Show()

    def setup_gui(self):
        self.SetBackgroundColour(core.default_background_color)
        self.Centre()
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        
        # first
        first = wx.Panel(self, -1, size=(480, 85), pos=(10, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        first.SetBackgroundColour(core.default_background_color)
        
        self.textbox_description = wx.TextCtrl(first, -1, pos=(10, 25), size=(210, 30))
        self.textbox_amount = wx.TextCtrl(first, -1, pos=(255, 25), size=(60, 30))
        self.textbox_value = wx.TextCtrl(first, -1, pos=(375, 25), size=(60, 30))
        
        self.textbox_value.Bind(wx.EVT_CHAR, core.check_money)
        self.textbox_amount.Bind(wx.EVT_CHAR, core.check_number)
        
        self.textbox_value.SetValue("0,00")
        wx.StaticText(first, -1, u'Quantidade:', pos=(255, 5))
        wx.StaticText(first, -1, u'R$', pos=(360, 32))
        wx.StaticText(first, -1, u'Valor unitário:', pos=(375, 5))
        
        last = wx.Panel(self, -1, size=(480, 60), pos=(10, 105), style=wx.SUNKEN_BORDER)
        last.SetBackgroundColour(core.default_background_color)
        last_ = wx.Panel(last, pos=(80, 10), size=(320, 40), style=wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Check.png', wx.BITMAP_TYPE_PNG),
                                     u'Finalizar', pos=(0, 0), size=(100, 40))
        finish.Bind(wx.EVT_BUTTON, self.ask_end)
        restart = GenBitmapTextButton(last_, -1,
                                      wx.Bitmap(core.directory_paths['icons'] + 'Reset.png', wx.BITMAP_TYPE_PNG),
                                      u'Recomeçar', pos=(100, 0), size=(120, 40))
        restart.Bind(wx.EVT_BUTTON, self.ask_clean)
        cancel = GenBitmapTextButton(last_, -1,
                                     wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                                     u"sair", pos=(220, 0), size=(100, 40))
        cancel.Bind(wx.EVT_BUTTON, self.ask_exit) 

    def recover_waste(self):
        planet = shelve.open(self.argv[0])
        self.textbox_description.SetValue(planet["wastes"][self.argv[1]]['description'])
        self.textbox_value.SetValue(
            core.good_show("money", str(planet["wastes"][self.argv[1]]['unit_price'])).replace(".", ","))
        self.textbox_amount.SetValue(str(planet["wastes"][self.argv[1]]['amount']))
        planet.close()

    def ask_clean(self, event):
        """
        Confirma se o usuario quer apagar tudo
        :param event:
        :return:
        """
        dialogs.Ask(self, u"Apagar Tudo", 1)

    def ask_exit(self, event):
        pl = str(self.textbox_description.GetValue())
        po = str(self.textbox_value.GetValue())
        pk = str(self.textbox_amount.GetValue())
        if pl == '' and po == '0,00' and (pk == '' or pk == '0'):
            self.Close()
            return
        dialogs.Ask(self, u"Sair", 91)

    def ask_end(self, event):
        dialogs.Ask(self, u"Finalizar Registro", 3)

    def clean(self):
        self.textbox_description.Clear()
        self.textbox_value.Clear()
        self.textbox_value.SetValue("0,00")
        self.textbox_amount.Clear()

    def end(self):
        description = self.textbox_description.GetValue().capitalize()
        value = float(self.textbox_value.GetValue().replace(",", "."))
        amount = self.textbox_amount.GetValue()
        if len(amount) == 0:
            amount = 0
        else:
            amount = int(amount)
        total_value = value * amount
        if len(description) == 0 or value == 0 or amount == 0:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        finish_time = core.good_show("o", str(datetime.now().hour)) + ":" + core.good_show("o", str(
            datetime.now().minute)) + ":" + core.good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + core.good_show(
            "o", str(datetime.now().day))
        info = core.directory_paths['saves'] + date + ".txt"
        day_data = shelve.open(info)
        if "sales" not in day_data:
            day_data["sales"] = {}
            day_data["secount"] = 0
            day_data["edit"] = {}
            day_data["spent"] = {}
            day_data["spcount"] = 0
            day_data["closure"] = []
            day_data["wastes"] = {}
            day_data["wcount"] = 0
        if not self.argv:
            key = day_data["wcount"] + 1
            asw = day_data["wastes"]
            asw[key] = {'time': finish_time,
                        'edit': 0,
                        'description': description,
                        'unit_price': value,
                        'amount': amount,
                        'value': total_value}
            day_data["wastes"] = asw
            day_data["wcount"] = key
        else:
            day_data.close()
            day_data = shelve.open(self.argv[0])
            key = self.argv[1]
            hour = self.argv[2]
            asw = day_data["edit"]
            asw[finish_time] = day_data["wastes"][key]
            asw[finish_time]['key'] = key
            asw[finish_time]['argv'] = 1
            day_data["edit"] = asw
            adw = day_data["wastes"]
            asw[key] = {'time': hour,
                        'edit': 1,
                        'description': description,
                        'unit_price': value,
                        'amount': amount,
                        'value': total_value}
            day_data["wastes"] = adw
        self.clean()
        day_data.close()
        dialogs.Confirmation(self, u"Sucesso", 3)

    def exit(self):
        self.Close()
