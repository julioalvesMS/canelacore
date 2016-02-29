#!/usr/bin/env python
# -*- coding: utf-8 -*-


import wx
import core


class FrequencyPanel(wx.Panel):
    checkbox_on_start = None
    checkbox_on_close = None
    checkbox_on_time = None

    spinbox_on_time_hour = None
    spinbox_on_time_minutes = None

    _enabled = True

    class FrequencySelections(object):

        def __init__(self):
            self.options = list()
            self.time = u''

    def __init__(self, parent, pos, description=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pos=pos, style=wx.TAB_TRAVERSAL)

        self.checkbox_on_start = wx.CheckBox(self, wx.ID_ANY, u'Ao iniciar o Programa')
        self.checkbox_on_close = wx.CheckBox(self, wx.ID_ANY, u'Ao Fechar o programa')

        panel_on_time = wx.Panel(self, wx.ID_ANY)
        self.checkbox_on_time = wx.CheckBox(panel_on_time, wx.ID_ANY, u'Em um determinado horário: ')

        panel_spin = wx.Panel(panel_on_time, wx.ID_ANY)
        self.spinbox_on_time_hour = wx.SpinCtrl(panel_spin, wx.ID_ANY, size=(50, -1), min=0, max=23, initial=12,
                                                style=wx.TE_CENTRE)
        self.spinbox_on_time_minutes = wx.SpinCtrl(panel_spin, wx.ID_ANY, size=(50, -1), min=0, max=59, initial=30,
                                                   style=wx.TE_CENTRE)
        static_on_time = wx.StaticText(panel_spin, wx.ID_ANY, u':')

        sizer_spin = wx.FlexGridSizer(1, 3, 0, 5)
        sizer_spin.Add(self.spinbox_on_time_hour)
        sizer_spin.Add(static_on_time)
        sizer_spin.Add(self.spinbox_on_time_minutes)
        panel_spin.SetSizer(sizer_spin)

        sizer_on_time = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_on_time.Add(self.checkbox_on_time)
        sizer_on_time.Add(panel_spin)
        panel_on_time.SetSizer(sizer_on_time)

        sizer = wx.FlexGridSizer(1, 3, 5, 20)
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableCol(2, 1)
        sizer.Add(self.checkbox_on_start)
        sizer.Add(self.checkbox_on_close)
        sizer.Add(panel_on_time)
        self.SetSizer(sizer)

        self.SetSize((680, 30))

    def Disable(self, event=None):
        self.checkbox_on_close.Disable()
        self.checkbox_on_start.Disable()
        self.checkbox_on_time.Disable()
        self.spinbox_on_time_hour.Disable()
        self.spinbox_on_time_minutes.Disable()
        self._enabled = False

    def Enable(self, event=None):
        self.checkbox_on_close.Enable()
        self.checkbox_on_start.Enable()
        self.checkbox_on_time.Enable()
        self.spinbox_on_time_hour.Enable()
        self.spinbox_on_time_minutes.Enable()
        self._enabled = True

    def IsEnabled(self, event=None):
        return self._enabled

    def change_enable(self, event=None):
        if self.IsEnabled():
            self.Disable()
        else:
            self.Enable()

    def set_selections(self, selections):
        """
        Atualiza os dados da frequencia do Painel
        :param FrequencySelections selections:
        """

        self.checkbox_on_start.SetValue(core.ON_START in selections.options)
        self.checkbox_on_close.SetValue(core.ON_CLOSE in selections.options)
        self.checkbox_on_time.SetValue(core.ON_TIME in selections.options)

        time = selections.time.split(u':')
        if len(time):
            self.spinbox_on_time_hour.SetValue(int(time[0]))
            self.spinbox_on_time_minutes.SetValue(int(time[1]))

        return selections

    def get_selections(self):
        """
        Obtém os dados da frequencia do Painel
        :return FrequencySelections:
        """

        selections = self.FrequencySelections()

        if self.checkbox_on_start.GetValue():
            selections.options.append(core.ON_START)
        if self.checkbox_on_close.GetValue():
            selections.options.append(core.ON_CLOSE)
        if self.checkbox_on_time.GetValue():
            selections.options.append(core.ON_TIME)
        hour = core.format_2_digits(self.spinbox_on_time_hour.GetValue())
        minutes = core.format_2_digits(self.spinbox_on_time_minutes.GetValue())
        selections.time = u'%s:%s' % (hour, minutes)

        return selections

    def get_string_selections(self):
        selections = self.get_selections()

        string = u'%s %s' % (u'-'.join(core.convert_list(selections.options, str)), selections.time)

        return string

    @staticmethod
    def get_selections_from_string(string):
        """
        Obtém os dados da frequencia a partir de uma string
        :param str string: string de seleções
        :return FrequencySelections:
        """

        selections = FrequencyPanel.FrequencySelections()

        frequencies = string.split()

        time_pos = -1
        frequency_pos = -1

        for i in range(len(frequencies)):
            if u':' in frequencies[i]:
                time_pos = i
            else:
                frequency_pos = i

        if time_pos != -1:
            selections.time = frequencies[time_pos]

        if frequency_pos != -1:
            selections.options = core.convert_list(frequencies[frequency_pos].split(u'-'), int)

        return selections
