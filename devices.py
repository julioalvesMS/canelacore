#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx


class BarcodeReader:

    def __init__(self, parent):
        self.timer = wx.Timer(parent)
        self.buffer = []
        self.parent = parent
        self.timer.Bind(wx.EVT_TIMER, self.skip_event)

    def reader_event(self, event):
        if not self.timer.IsRunning():
            self.buffer = []
            self.buffer.append(event)
            self.timer.Start(100)
        self.timer.Stop()

    def skip_event(self, event, function):
        pass
