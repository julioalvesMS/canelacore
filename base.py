#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import threading
from datetime import datetime
from random import randint

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton

import clients
import core
import daily_report
import delivery
import dialogs
import inventory
import monthly_report
import record_editor
import sale
import settings
import teste
import expense
import waste
import database
import categories

__author__ = 'Julio'


class Base(wx.Frame):

    backup_enabled = False
    backup_running = False

    logo = None
    panel_logo = None
    background_image = None

    def __init__(self, parent=None, title=u'Canela Core'):
        """
        Construtor
        :param parent: frame pai
        :param title: Titulo do Frame
        """
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX |
                          wx.CLIP_CHILDREN | wx.TAB_TRAVERSAL)

        self.setup_gui()

        core.setup_environment()

        # desabilitado em faze de desenvolvimento

        # # Faz o Backup e verifica entregas
        # self.bool_b = False
        # self.backup(None)
        
        self.timer_delivery = wx.Timer(self)
        self.notification_control = {}
        self.Bind(wx.EVT_TIMER, self.delivery_check, self.timer_delivery)
        self.delivery_check(None)

        self.Show()
        self.tray = BaseTray(self)

    def setup_gui(self):
        self.Bind(wx.EVT_CLOSE, self.ask_exit)
        self.SetSize(wx.Size(805, 647))
        self.Centre()
        part1 = wx.Panel(self, pos=(130, 325), size=(540, 60), style=wx.SIMPLE_BORDER)
        part2 = wx.Panel(self, pos=(160, 390), size=(480, 60), style=wx.SIMPLE_BORDER)
        part3 = wx.Panel(self, pos=(220, 455), size=(360, 60), style=wx.SIMPLE_BORDER)
        part4 = wx.Panel(self, pos=(550, 535), size=(220, 50), style=wx.SIMPLE_BORDER)
        part5 = wx.Panel(self, pos=(35, 535), size=(150, 50), style=wx.SIMPLE_BORDER)
        self.panel_logo = wx.Panel(self, pos=(263, 45), size=(274, 274), style=wx.SIMPLE_BORDER)
        a = GenBitmapTextButton(part1, 11,
                                wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                u"Registrar Vendas", (0, 0), size=(180, 60))
        b = GenBitmapTextButton(part1, 13,
                                wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                u"Registrar Gastos", (180, 0), size=(180, 60))
        c = GenBitmapTextButton(part1, 17,
                                wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG),
                                u"Registrar Desperdícios", (360, 0), size=(180, 60))
        d = GenBitmapTextButton(part2, 14, wx.Bitmap(core.directory_paths['icons'] + 'Money.png', wx.BITMAP_TYPE_PNG),
                                u"Fechamento", (0, 0), size=(120, 60))
        e = GenBitmapTextButton(part2, 12, wx.Bitmap(core.directory_paths['icons'] + 'Book.png', wx.BITMAP_TYPE_PNG),
                                u"Clientes", (120, 0), size=(120, 60))
        f = GenBitmapTextButton(part2, 19, wx.Bitmap(core.directory_paths['icons'] + 'Stock.png', wx.BITMAP_TYPE_PNG),
                                u"Estoque", (240, 0), size=(120, 60))
        g = GenBitmapTextButton(part2, 18,
                                wx.Bitmap(core.directory_paths['icons'] + 'Delivery.png', wx.BITMAP_TYPE_PNG),
                                u"Entregas", (360, 0), size=(120, 60))
        h = GenBitmapTextButton(part3, 20, wx.Bitmap(core.directory_paths['icons'] + 'Resumo.png', wx.BITMAP_TYPE_PNG),
                                u"Resumos", (0, 0), size=(120, 60))
        i = GenBitmapTextButton(part3, 15, wx.Bitmap(core.directory_paths['icons'] + 'Tools.png', wx.BITMAP_TYPE_PNG),
                                u"Recuperação", (120, 0), size=(120, 60))
        j = GenBitmapTextButton(part3, 16, wx.Bitmap(core.directory_paths['icons'] + 'Save.png', wx.BITMAP_TYPE_PNG),
                                u"Backup", (240, 0), size=(120, 60))
        k = GenBitmapTextButton(self, 21, wx.Bitmap(core.directory_paths['icons'] + 'system-users.png', wx.BITMAP_TYPE_PNG), u"Teste", (0, 0), size=(180, 60))
        GenBitmapTextButton(part4, 98, wx.Bitmap(core.directory_paths['icons'] + 'Down.png', wx.BITMAP_TYPE_PNG),
                            u"Minimizar", (0, 0), size=(120, 50))
        GenBitmapTextButton(part4, 99, wx.Bitmap(core.directory_paths['icons'] + 'Exit.png', wx.BITMAP_TYPE_PNG),
                            u"Sair", (120, 0), size=(100, 50))
        GenBitmapTextButton(part5, 42, wx.Bitmap(core.directory_paths['icons'] + 'Settings.png', wx.BITMAP_TYPE_PNG),
                            u"Configurações", (0, 0), size=(150, 50))
        self.Bind(wx.EVT_BUTTON, self.open_new_sale, id=11)
        self.Bind(wx.EVT_BUTTON, self.open_client_manager, id=12)
        self.Bind(wx.EVT_BUTTON, self.open_new_expense, id=13)
        self.Bind(wx.EVT_BUTTON, self.open_daily_report, id=14)
        self.Bind(wx.EVT_BUTTON, self.open_edition_manager, id=15)
        self.Bind(wx.EVT_BUTTON, self.backup, id=16)
        self.Bind(wx.EVT_BUTTON, self.open_new_waste, id=17)
        self.Bind(wx.EVT_BUTTON, self.open_delivery_manager, id=18)
        self.Bind(wx.EVT_BUTTON, self.open_inventory_manager, id=19)
        self.Bind(wx.EVT_BUTTON, self.verify_credentials, id=20)
        self.Bind(wx.EVT_BUTTON, self.open_teste_window, id=21)
        self.Bind(wx.EVT_BUTTON, self.open_settings, id=42)
        self.Bind(wx.EVT_BUTTON, self.hide_to_tray, id=98)
        self.Bind(wx.EVT_BUTTON, self.ask_exit, id=99)
        a.SetBackgroundColour('#C2E6F8')
        b.SetBackgroundColour('#C2E6F8')
        c.SetBackgroundColour('#C2E6F8')
        d.SetBackgroundColour('#6EFF70')
        e.SetBackgroundColour('#6EFF70')
        f.SetBackgroundColour('#6EFF70')
        g.SetBackgroundColour('#6EFF70')
        h.SetBackgroundColour('#FFDF85')
        i.SetBackgroundColour('#FFDF85')
        j.SetBackgroundColour('#FFDF85')

        # Prepara os backgrounds do base
        backs = []
        for root, dirs, files in os.walk(core.directory_paths['backgrounds']):
            for i in files:
                if i[-3:] in ['png', 'jpg']:
                    backs.append(root + core.slash + i)
        self.background_image = wx.Bitmap(backs[randint(0, len(backs) - 1)])
        self.logo = wx.Bitmap(core.directory_paths['custom'] + 'logo-canela-santa1.jpg')
        wx.EVT_PAINT(self, self.OnPaint)
        self.SetIcon(wx.Icon(core.general_icon, wx.BITMAP_TYPE_ICO))
        # Faz o menu
        files = wx.Menu()
        files.Append(57, u'&Reabrir\tF5')
        files.Append(58, u'&Esconder\tCtrl+H')
        files.Append(59, u'&Sair\tCtrl+Q')
        tasks = wx.Menu()
        # tasks.Append(61, u'&Buscar atualizações')
        tasks.Append(62, u'&Realizar __backup__')
        helps = wx.Menu()
        helps.Append(71, u'Ajuda')
        menu = wx.MenuBar()
        menu.Append(files, u'&Arquivos')
        menu.Append(tasks, u'&Tarefas')
        menu.Append(helps, u'Ajuda')
        self.SetMenuBar(menu)
        self.Bind(wx.EVT_MENU, self.ask_exit, id=59)
        self.Bind(wx.EVT_MENU, self.hide_to_tray, id=58)
        self.Bind(wx.EVT_MENU, self.reopen, id=57)
        self.Bind(wx.EVT_MENU, self.backup, id=62)

    def OnPaint(self, event):
        wx.PaintDC(self).DrawBitmap(self.background_image, 0, 0)
        wx.PaintDC(self.panel_logo).DrawBitmap(self.logo, 0, 0)

    def backup(self, event):    # TODO Fazer a thread fechar direito com o resto do app
        if self.backup_running or not self.backup_enabled:
            return
        back = threading.Thread(target=self.__backup__, args=[True if event else False])
        back.setDaemon(True)
        back.start()

    def __backup__(self, called=False):
        try:
            if self.backup_running:
                return
            self.backup_running = True
            tempo = core.good_show("o", str(datetime.now().hour)) + "-" + core.good_show("o", str(
                datetime.now().minute)) + "-" + core.good_show("o", str(datetime.now().second))
            date = str(datetime.now().year) + "-" + core.good_show("o", str(datetime.now().month)) + "-" + \
                core.good_show("o", str(datetime.now().day))
            lol = date + "_" + tempo
            if os.path.exists(core.directory_paths['temporary']):
                shutil.rmtree(core.directory_paths['temporary'])
            os.mkdir(core.directory_paths['temporary'])
            shutil.copytree(core.directory_paths['saves'], core.directory_paths['temporary'] + 'saves')
            shutil.copytree(core.directory_paths['inventory'], core.directory_paths['temporary'] + 'products')
            shutil.copytree(core.directory_paths['clients'], core.directory_paths['temporary'] + 'clients')
            if os.path.exists(core.directory_paths['trash']):
                shutil.copytree(core.directory_paths['trash'], core.directory_paths['.trash'])
            shutil.make_archive(core.directory_paths['backups'] + lol, "zip", core.directory_paths['temporary'])
            shutil.rmtree(core.directory_paths['temporary'], True)
            for root, dirs, files in os.walk(core.directory_paths['backups']):
                files.sort()
                files.reverse()
                p = len(files)
                while p > 20:
                    os.remove(root + core.slash + files[p - 1])
                    p -= 1
            self.timer_backup = threading.Timer(2*3600*1000, self.__backup__)
            self.timer_backup.start()
            if called:
                wx.CallAfter(self.backup_confirmation)
            self.backup_running = False
        except Exception, e:    # TODO Determinar quais exeptions podem ocorrer e dazer um melhor tratamento
            print e
            self.backup_running = False
            if called:
                back = threading.Thread(target=self.__backup__, args=[True])
            else:
                back = threading.Thread(target=self.__backup__)
            back.start()
            return

    def backup_confirmation(self):
        a = wx.MessageDialog(self, u'Backup salvo com sucesso!', u'Backup', style=wx.OK | wx.ICON_INFORMATION)
        a.ShowModal()
        a.Destroy()

    def delivery_check(self, event):
        self.timer_delivery.Stop()

        date_now, time_now = core.datetime_today()

        date_now_int = core.date2int(date_now)
        time_now_int = core.hour2int(time_now[:5])

        deliveries_db = database.DeliveriesDB()
        deliveries = deliveries_db.deliveries_list()
        deliveries_db.close()

        check_interval = 30
        for _delivery in deliveries:
            date_delivery_int = core.date2int(_delivery.date)

            if date_delivery_int < date_now_int:
                _delivery.active = False
                deliveries_db.delete_delivery(_delivery.ID)

            if _delivery.active is False:
                del self.notification_control[_delivery.ID]

            if date_delivery_int != date_now_int or _delivery.active is False:
                continue

            if _delivery.ID in self.notification_control:
                continue

            time_delivery_int = core.hour2int(_delivery.hour)
            time_remaining = time_delivery_int - time_now_int
            if time_remaining < 60:
                minutes_to_warning = 0
            else:
                minutes_to_warning = time_remaining - 60

            self.notification_control[_delivery.ID] = _delivery

            timer = threading.Timer(60*minutes_to_warning + 1, self.notify_delivery, args=[_delivery])
            timer.start()

        check_interval *= 60000
        if not check_interval:
            check_interval = 300000
        self.timer_delivery.Start(check_interval)
        
    def notify_delivery(self, data):
        """
        Notifica o usuario sobre a existencia de uma entrega a a ser realizada
        :param data: Dados da entrega
        :type data: data_types.DeliveryData
        :return: None
        :rtype: None
        """

        breaks = [60, 30, 15]

        time_now = core.datetime_today()[1][:5]
        time_now_int = core.hour2int(time_now)

        time_delivery_int = core.hour2int(data.hour)

        remaining = time_delivery_int - time_now_int

        for i in breaks:
            if remaining > i:
                timer = threading.Timer(60*i, self.notify_delivery, args=[data])
                timer.start()
                break

        dialogs.Warner(self, data)

    def hide_to_tray(self, event):
        self.Hide()

    def exit(self, event):
        self.Destroy()
        self.tray.Destroy()

    def ask_exit(self, event):
        dialogs.Ask(self, u'Sair', 90)

    def reopen(self, event):
        self.exit(None)
        Base()

    def verify_credentials(self, event):
        dialogs.PasswordBox(self)

    def open_new_sale(self, event):
        sale.Sale(self)

    def open_client_manager(self, event):
        clients.ClientManager(self)

    def open_new_expense(self, event):
        expense.Expense(self)

    def open_daily_report(self, event):
        daily_report.Report(self)

    def open_edition_manager(self, event):
        record_editor.EditionManager(self)

    def open_new_waste(self, event):
        waste.Waste(self)

    def open_delivery_manager(self, event):
        delivery.DeliveryManager(self)

    def open_inventory_manager(self, event):
        inventory.InventoryManager(self)

    def open_monthly_report(self, event):
        monthly_report.Report(self)

    def open_settings(self, event):
        settings.SettingsMenu(self)

    def open_teste_window(self, event):
        teste.Teste(self)


class BaseTray(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(core.tray_icon, wx.BITMAP_TYPE_ICO), u'Canela Santa')
        self.Bind(wx.EVT_MENU, self.bshow, id=101)
        self.Bind(wx.EVT_MENU, self.bhide, id=102)
        self.Bind(wx.EVT_MENU, self.open_new_sale, id=1031)
        self.Bind(wx.EVT_MENU, self.open_new_expense, id=1032)
        self.Bind(wx.EVT_MENU, self.open_new_waste, id=1033)
        self.Bind(wx.EVT_MENU, self.open_new_client, id=1034)
        self.Bind(wx.EVT_MENU, self.open_new_product, id=1035)
        self.Bind(wx.EVT_MENU, self.open_new_category, id=1036)
        self.Bind(wx.EVT_MENU, self.open_update_inventory, id=1037)
        self.Bind(wx.EVT_MENU, self.open_inventory_manager, id=1041)
        self.Bind(wx.EVT_MENU, self.open_category_manager, id=1042)
        self.Bind(wx.EVT_MENU, self.open_client_manager, id=1043)
        self.Bind(wx.EVT_MENU, self.open_daily_report, id=1044)
        self.Bind(wx.EVT_MENU, self.verify_credentials, id=1045)
        self.Bind(wx.EVT_MENU, self.open_edition_manager, id=1046)
        self.Bind(wx.EVT_MENU, self.open_delivery_manager, id=1047)
        self.Bind(wx.EVT_MENU, self.open_settings, id=108)
        self.Bind(wx.EVT_MENU, self.ask_exit, id=109)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.bshow)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(101, u'Abrir')
        menu.Append(102, u'Esconder')
        menu.AppendSeparator()
        menu2 = wx.Menu()
        menu2.Append(1031, u'Venda')
        menu2.Append(1032, u'Gasto')
        menu2.Append(1033, u'Desperdício')
        menu2.Append(1034, u'Cliente')
        menu2.Append(1035, u'Produto')
        menu2.Append(1036, u'Categoria')
        menu2.Append(1037, u'Entrada de Produtos')
        menu.AppendMenu(103, u'Registrar', menu2)
        menu.Append(1041, u'Estoque')
        menu.Append(1042, u'Categorias de Produtos')
        menu.Append(1043, u'Clientes')
        menu.Append(1044, u'Fechamento do Caixa')
        menu.Append(1045, u'Resumo Mensal')
        menu.Append(1046, u'Recuperação de Registros')
        menu.Append(1047, u'Entregas')
        menu.AppendSeparator()
        menu.Append(108, u'Configurações')
        menu.Append(109, u'Sair')
        return menu

    def verify_credentials(self, event):
        dialogs.PasswordBox(self.frame)

    def open_new_sale(self, event):
        sale.Sale(self.frame)

    def open_client_manager(self, event):
        clients.ClientManager(self.frame)

    def open_new_expense(self, event):
        expense.Expense(self.frame)

    def open_daily_report(self, event):
        daily_report.Report(self.frame)

    def open_edition_manager(self, event):
        record_editor.EditionManager(self.frame)

    def open_new_waste(self, event):
        waste.Waste(self.frame)

    def open_delivery_manager(self, event):
        delivery.DeliveryManager(self.frame)

    def open_inventory_manager(self, event):
        inventory.InventoryManager(self.frame)

    def open_new_client(self, event):
        clients.ClientRegister(self.frame)

    def open_monthly_report(self, event):
        monthly_report.Report(self.frame)

    def open_new_product(self, event):
        inventory.ProductRegister(self.frame)

    def open_new_category(self, event):
        categories.ProductCategoryData(self.frame)

    def open_category_manager(self, event):
        categories.ProductCategoryManager(self.frame)

    def open_update_inventory(self, event):
        inventory.UpdateInventory(self.frame)

    def open_settings(self, event):
        settings.SettingsMenu(self.frame)

    def bshow(self, event):
        if not self.frame.IsShown():
            self.frame.Show()

    def bhide(self, event):
        if self.frame.IsShown():
            self.frame.Hide()

    def ask_exit(self, event):
        dialogs.Ask(self.frame, u'Sair', 90)


'''
###TOP PRIORITY###
criar venda programada
na venda programada, se for entrega, já deixar a entrega programada

categoria no relatório de produtos
v2.0
fazer instalador
recuperação de __backup__,
salvar tudo  ou os backups no drop ou parecido
'''
