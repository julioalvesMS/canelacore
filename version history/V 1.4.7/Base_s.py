#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import os
import shutil
import calendar
import time
import codecs
import hashlib
import pickle
import threading
from datetime import datetime
from unicodedata import normalize
from string import lower, strip
from random import randint

import wx
import wx.gizmos
from wx.lib.buttons import GenBitmapTextButton


class base(wx.Frame):

    back_on = False
    logo = None

    def __init__(self, parent=None, frame_id=-1, title=u'Caixa'):
        wx.Frame.__init__(self, parent, frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)

        self.setupGui()

        #Faz o Backup e verifica entregas
        self.wd60 = {}
        self.bool_b = False
        self.backup_button(-1)
        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.deldel, self.timer2)
        self.deldel(1)
        self.up_on = False


        self.Show()
        self.hiden = base_hi(self)

    def setupGui(self):
        self.Bind(wx.EVT_CLOSE, self.ask_closer)
        self.SetSize(wx.Size(805, 647))
        self.Centre()
        part1 = wx.Panel(self, pos=(130, 325), size = (540, 60), style = wx.SIMPLE_BORDER)
        part2 = wx.Panel(self, pos=(160, 390), size = (480, 60), style = wx.SIMPLE_BORDER)
        part3 = wx.Panel(self, pos=(220, 455), size = (360, 60), style = wx.SIMPLE_BORDER)
        part4 = wx.Panel(self, pos=(550, 535), size = (220, 50), style = wx.SIMPLE_BORDER)
        part5 = wx.Panel(self, pos=(35, 535), size = (150, 50), style = wx.SIMPLE_BORDER)
        self.logo_p = wx.Panel(self, pos=(263, 45), size = (274, 274), style = wx.SIMPLE_BORDER)
        a = GenBitmapTextButton(part1, 11, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u"Registrar Vendas", (0, 0), size=(180, 60))
        b = GenBitmapTextButton(part1, 13, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u"Registrar Gastos", (180, 0), size=(180, 60))
        c = GenBitmapTextButton(part1, 17, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u"Gegistrar Desperdícios", (360, 0), size=(180, 60))
        d = GenBitmapTextButton(part2, 14, wx.Bitmap(current_dir + '\\data\\pics\\Money.png', wx.BITMAP_TYPE_PNG), u"Fechamento", (0, 0), size=(120, 60))
        e = GenBitmapTextButton(part2, 12, wx.Bitmap(current_dir + '\\data\\pics\\Book.png', wx.BITMAP_TYPE_PNG), u"Clientes", (120, 0), size=(120, 60))
        f = GenBitmapTextButton(part2, 19, wx.Bitmap(current_dir + '\\data\\pics\\Stock.png', wx.BITMAP_TYPE_PNG), u"Estoque", (240, 0), size=(120, 60))
        g = GenBitmapTextButton(part2, 18, wx.Bitmap(current_dir + '\\data\\pics\\Delivery.png', wx.BITMAP_TYPE_PNG), u"Entregas", (360, 0), size=(120, 60))
        h = GenBitmapTextButton(part3, 20, wx.Bitmap(current_dir + '\\data\\pics\\Resumo.png', wx.BITMAP_TYPE_PNG), u"Resumos", (0, 0), size=(120, 60))
        i = GenBitmapTextButton(part3, 15, wx.Bitmap(current_dir + '\\data\\pics\\Tools.png', wx.BITMAP_TYPE_PNG), u"Recuperação", (120, 0), size=(120, 60))
        j = GenBitmapTextButton(part3, 16, wx.Bitmap(current_dir + '\\data\\pics\\Save.png', wx.BITMAP_TYPE_PNG), u"Backup", (240, 0), size=(120, 60))
        #k = GenBitmapTextButton(self, 21, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u"Programar Venda", (0, 0), size=(180, 60))
        GenBitmapTextButton(part4, 98, wx.Bitmap(current_dir + '\\data\\pics\\Down.png', wx.BITMAP_TYPE_PNG), u"Minimizar", (0, 0), size=(120, 50))
        GenBitmapTextButton(part4, 99, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair", (120, 0), size=(100, 50))
        GenBitmapTextButton(part5, 42, wx.Bitmap(current_dir + '\\data\\pics\\Settings.png', wx.BITMAP_TYPE_PNG), u"Configurações", (0, 0), size=(150, 50))
        self.Bind(wx.EVT_BUTTON, self.win2, id=11)
        self.Bind(wx.EVT_BUTTON, self.win3, id=12)
        self.Bind(wx.EVT_BUTTON, self.win4, id=13)
        self.Bind(wx.EVT_BUTTON, self.win5, id=14)
        self.Bind(wx.EVT_BUTTON, self.win6, id=15)
        self.Bind(wx.EVT_BUTTON, self.backup_button, id=16)
        self.Bind(wx.EVT_BUTTON, self.win7, id=17)
        self.Bind(wx.EVT_BUTTON, self.win8, id=18)
        self.Bind(wx.EVT_BUTTON, self.win9, id=19)
        self.Bind(wx.EVT_BUTTON, self.verify, id=20)
        #self.Bind(wx.EVT_BUTTON, self.win15, id=21)
        self.Bind(wx.EVT_BUTTON, self.win14, id=42)
        self.Bind(wx.EVT_BUTTON, self.hider, id=98)
        self.Bind(wx.EVT_BUTTON, self.ask_closer, id=99)
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

        #Prepara os backgrounds do base
        backs = []
        for root, dirs, files in os.walk('data\\back'):
            for i in files:
                if i[-3:] in ['png', 'jpg']:
                    backs.append(current_dir + '\\' + root + '\\' + i)
        self.bitmap = wx.Bitmap(backs[randint(0, len(backs)-1)])
        self.logo = wx.Bitmap(current_dir + '\\data\\custom-logo\\logo-canela-santa1.jpg')
        wx.EVT_PAINT(self, self.OnPaint)
        self.SetIcon(general_icon)
        #Faz o menu
        files = wx.Menu()
        files.Append(57, u'&Reabrir\tF5')
        files.Append(58, u'&Esconder\tCtrl+H')
        files.Append(59, u'&Sair\tCtrl+Q')
        tasks = wx.Menu()
        #tasks.Append(61, u'&Buscar atualizações')
        tasks.Append(62, u'&Realizar backup')
        helps = wx.Menu()
        helps.Append(71, u'Ajuda')
        menu = wx.MenuBar()
        menu.Append(files, u'&Arquivos')
        menu.Append(tasks, u'&Tarefas')
        menu.Append(helps, u'Ajuda')
        self.SetMenuBar(menu)
        self.Bind(wx.EVT_MENU, self.ask_closer, id=59)
        self.Bind(wx.EVT_MENU, self.hider, id=58)
        self.Bind(wx.EVT_MENU, self.reopen, id=57)
        self.Bind(wx.EVT_MENU, self.backup_button, id=62)


    def OnPaint(self, event):
        wx.PaintDC(self).DrawBitmap(self.bitmap, 0, 0)
        wx.PaintDC(self.logo_p).DrawBitmap(self.logo, 0, 0)

    def backup_button(self, event):
        if self.back_on:
            return
        self.backuper = threading.Thread(target=self.backup, args=[True])
        self.backuper.daemon = True
        self.backuper.start()

    def backup(self, p1=False):
        try:
            if self.back_on:
                return
            self.back_on = True
            tempo= good_show("o", str(datetime.now().hour)) + "-" + good_show("o", str(datetime.now().minute)) + "-" + good_show("o", str(datetime.now().second))
            date = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
            lol = date + "_" +tempo
            if not os.path.exists('saves'):
                os.mkdir('saves')
            if not os.path.exists('products'):
                os.mkdir('products')
            if not os.path.exists('clients'):
                os.mkdir('clients')
            if os.path.exists('btemp'):
                shutil.rmtree('btemp')
            os.mkdir('btemp')
            shutil.copytree('saves', 'btemp/saves')
            shutil.copytree('products', 'btemp/products')
            shutil.copytree('clients', 'btemp/clients')
            if os.path.exists('#Trash'):
                shutil.copytree('#Trash', 'btemp/#Trash')
            shutil.make_archive("backup/" + lol, "zip", 'btemp')
            shutil.rmtree('btemp', True)
            for root, dirs, files in os.walk("backup"):
                files.sort()
                files.reverse()
                p = len(files)
                while p > 100:
                    os.remove(root + "/" + files[p-1])
                    p -= 1
            self.timer1 = threading.Timer(1800000.0, self.backup)
            self.timer1.daemon = True
            self.timer1.start()
            if p1:
                wx.CallAfter(self.backup_confirmation)
            self.back_on = False
        except:
            self.back_on = False
            if p1:
                self.backuper = threading.Thread(target=self.backup, args=True)
            else:
                self.backuper = threading.Thread(target=self.backup)
            self.backuper.daemon = True
            self.backuper.start()
            return

    def backup_confirmation(self):
        a = wx.MessageDialog(self, u'Backup salvo com sucesso!', 'Backup', style=wx.OK | wx.ICON_INFORMATION)
        a.ShowModal()
        a.Destroy()


    def deldel(self, event):
        self.timer2.Stop()
        today1 = datetime_int(2, str(datetime.now().year) + '-' + good_show("o", str(datetime.now().month)) + '-' + good_show("o", str(datetime.now().day)))
        today = datetime_int(1, good_show("o", str(datetime.now().hour)) + good_show("o", str(datetime.now().minute)))
        nextt = 5
        if not os.path.exists('saves'):
            os.mkdir('saves')
        try:
            gas = shelve.open(current_dir + '\\saves\\deliverys.txt')
        except:
            if os.path.exists(current_dir + '\\saves\\deliverys.txt'):
                os.remove(current_dir + '\\saves\\deliverys.txt')
            time.sleep(10)
            self.deldel(event)
        for i in gas:
            dt = i.split()
            date1 = dt[0]
            air = shelve.open(current_dir + '\\saves\\' + date1 + '.txt')
            bend = air['sales'][gas[i][0]]
            date = bend['date']
            if int(date_reverse(date.replace('/', '-')).replace('-', '')) < int(str(datetime.now().month) + good_show("o", str(datetime.now().day))):
                date = date + '/' + str(datetime.now().year+1)
            else:
                date = date + '/' + str(datetime.now().year)
            try:
                fire = datetime_int(2, date)
                tempo= bend['hour']
                water = datetime_int(1,tempo)
                if 0 < water-today-60 < nextt:
                    nextt = today-water-60
                elif 0 < water-today-30 < nextt:
                    nextt = today-water-30
                elif 0 < water-today-15 < nextt:
                    nextt = today-water-15
                elif 0 < water-today < nextt:
                    nextt = today-water
                elif i not in self.wd60:
                    self.wd60[i] = [False, False, False]
                if gas[i][1]:
                    ter = datetime_int(1, int(gas[i][2]))
                    if today-ter >= 10:
                        del gas[i]
                        del self.wd60[i]
                if fire < today1 or (fire == today1 and today >= (water + 60)) or gas[i][1]:
                    del gas[i]
                    del self.wd60[i]
                elif fire == today1 and water-today <= 15 and not self.wd60[i][2]:
                    adr = s_acentos(r_acentos(bend['city']) + ' - ' + r_acentos(bend['adress']))
                    rec = s_acentos(r_acentos(bend['receiver']))
                    potter = [time, adr, rec, gas[i][0], date1, 3]
                    warner(self, -1, u'Aviso!', potter)
                    self.wd60[i] = [True, True, True]
                elif fire == today1 and water-today <= 30 and not self.wd60[i][1]:
                    adr = s_acentos(r_acentos(bend['city']) + ' - ' + r_acentos(bend['adress']))
                    rec = s_acentos(r_acentos(bend['receiver']))
                    potter = [time, adr, rec, gas[i][0], date1, 2]
                    warner(self, -1, u'Aviso!', potter)
                    self.wd60[i] = [True, True, False]
                elif fire == today1 and water-today <= 60 and not self.wd60[i][0]:
                    adr = s_acentos(r_acentos(bend['city']) + ' - ' + r_acentos(bend['adress']))
                    rec = s_acentos(r_acentos(bend['receiver']))
                    potter = [time, adr, rec, gas[i][0], date1, 1]
                    warner(self, -1, u'Aviso!', potter)
                    self.wd60[i] = [True, False, False]
                air.close()
            except:
                del gas[i]
                if i in self.wd60:
                    del self.wd60[i]
        gas.close()
        nextt *= 60000
        if not nextt:
            nextt = 300000
        self.timer2.Start(nextt)

    def hider(self, event):
        self.Hide()

    def closer(self):
        self.Destroy()
        self.hiden.Destroy()

    def ask_closer(self, event):
        ask(self, -1, u'Sair', 99, 99)

    def reopen(self, event):
        self.closer()
        base(None)

    def verify(self, event):
        pass_box(self)

    def win2(self, event):
        sell(self)

    def win3(self, event):
        clients(self)

    def win4(self, event):
        expenses(self)

    def win5(self, event):
        report(self)

    def win6(self, event):
        redit(self)

    def win7(self, event):
        wasted(self)

    def win8(self, event):
        delivery(self)

    def win9(self, event):
        stock(self)

    def win11(self, event):
        resumo(self)

    def win14(self, event):
        settings(self)

    def win15(self, event):
        ProgramedSales(self)


class base_hi(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(current_dir + '\\bronze2.ico', wx.BITMAP_TYPE_ICO), u'Canela Santa')
        self.Bind(wx.EVT_MENU, self.win2, id=1031)
        self.Bind(wx.EVT_MENU, self.win4, id=1032)
        self.Bind(wx.EVT_MENU, self.win3, id=1042)
        self.Bind(wx.EVT_MENU, self.win5, id=1043)
        self.Bind(wx.EVT_MENU, self.win6, id=1045)
        self.Bind(wx.EVT_MENU, self.win7, id=1033)
        self.Bind(wx.EVT_MENU, self.win12, id=1035)
        self.Bind(wx.EVT_MENU, self.win13, id=1036)
        self.Bind(wx.EVT_MENU, self.win8, id=1046)
        self.Bind(wx.EVT_MENU, self.win9, id=1041)
        self.Bind(wx.EVT_MENU, self.win10, id=1034)
        self.Bind(wx.EVT_MENU, self.verify, id=1044)
        self.Bind(wx.EVT_MENU, self.bshow, id=101)
        self.Bind(wx.EVT_MENU, self.bhide, id=102)
        self.Bind(wx.EVT_MENU, self.win14, id=108)
        self.Bind(wx.EVT_MENU, self.ask_closer, id=109)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.bshow)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(101, u'Abrir')
        menu.Append(102, u'Esconder')
        menu.AppendSeparator()
        menu2 = wx.Menu()
        menu2.Append(1031, u'Registrar venda')
        menu2.Append(1032, u'Registrar gasto')
        menu2.Append(1033, u'Registrar desperdício')
        menu2.Append(1034, u'Cadastrar cliente')
        menu2.Append(1035, u'Cadastrar produto')
        menu2.Append(1036, u'Entrada de produtos')
        menu.AppendMenu(103, u'Registrar', menu2)
        menu.Append(1041, u'Estoque')
        menu.Append(1042, u'Clientes')
        menu.Append(1043, u'Fechamento do Caixa')
        menu.Append(1044, u'Resumo mensal')
        menu.Append(1045, u'Recuperação de registros')
        menu.Append(1046, u'Entregas')
        menu.AppendSeparator()
        menu.Append(108, u'Configurações')
        menu.Append(109, u'Sair')
        return menu

    def verify(self, event):
        pass_box(self.frame)

    def win2(self, event):
        sell(self.frame)
    def win3(self, event):
        clients(self.frame)
    def win4(self, event):
        expenses(self.frame)
    def win5(self, event):
        report(self.frame)
    def win6(self, event):
        redit(self.frame)
    def win7(self, event):
        wasted(self.frame)
    def win8(self, event):
        delivery(self.frame)
    def win9(self, event):
        stock(self.frame)
    def win10(self, event):
        new_client(self.frame)
    def win11(self, event):
        resumo(self.frame)
    def win12(self, event):
        new_product(self.frame)
    def win13(self, event):
        stock_change(self.frame)
    def win14(self, event):
        settings(self.frame)

    def bshow(self, event):
        if not self.frame.IsShown():
            self.frame.Show()

    def bhide(self, event):
        if self.frame.IsShown():
            self.frame.Hide()

    def ask_closer(self, event):
        ask(self.frame, -1, u'Sair', 99, 100)


class sell(wx.Frame):
    def __init__(self, parent, frame_id=-1, title=u'Vendas', mode=None, delmode=0, future=None):
        if not mode:
            mode = []
        wx.Frame.__init__(self, parent, frame_id, title, style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetPosition(wx.Point(200, 25))
        self.SetSize(wx.Size(925, 700))
        self.SetIcon(general_icon)
        self.parent = parent
        self.mode = mode
        self.delmode = delmode
        self.future = future
        self.SetBackgroundColour('#D6D6D6')
        #result
        result = wx.Panel(self, 21, pos=(5, 5), size=(450, 605), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        result.SetBackgroundColour('#D6D6D6')
        self.selling = wx.ListCtrl(result, 210, pos=(10, 10), size=(430, 400), style=wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES | wx.LC_HRULES)
        self.selling.InsertColumn(2100, u"Descrição", width=180)
        self.selling.InsertColumn(2101, u"Quantidade")
        self.selling.InsertColumn(2102, u"Preço Unit.")
        self.selling.InsertColumn(2103, u"Preço")
        self.total_sell=0.0
        self.tax=0.0
        self.disccount=0.0
        wx.StaticText(result, -1, u"Total:  R$" , (312, 417))
        self.totval = wx.TextCtrl(result, -1, good_show("money", str(self.total_sell).replace(".", ",")), (370, 410), size = (60,30), style = wx.TE_READONLY)
        self.totval.SetBackgroundColour("#C0C0C0")
        self.totval.Refresh()
        wx.StaticText(result, -1, u"Forma de Pagamento:", (10, 420))
        self.pay1 = wx.RadioButton(result, 211, u"Dinheiro", (15, 440))
        self.pay2 = wx.RadioButton(result, 211, u"Cartão", (15, 470))
        self.pay3 = wx.RadioButton(result, 211, u"Outra", (15, 500))
        self.pay3_ = wx.TextCtrl(result, -1, pos = (80, 500), size=(120,30))
        self.pay3_.SetBackgroundColour("#C0C0C0")
        self.pay3_.Refresh()
        self.turn1(1)
        self.pay1.Bind(wx.EVT_RADIOBUTTON, self.turn1)
        self.pay2.Bind(wx.EVT_RADIOBUTTON, self.turn1)
        self.pay3.Bind(wx.EVT_RADIOBUTTON, self.turn1)
        self.pay1.SetValue(True)
        wx.StaticText(result, -1, u"Desconto:  R$", (285, 450))
        self.disc = wx.TextCtrl(result, 212, pos = (370, 443), size = (60,30))
        self.disc.SetValue("0,00")
        self.disc.Bind(wx.EVT_CHAR, self.disc_check)
        self.discount = self.disc.GetValue()
        wx.StaticText(result, -1, u"Taxas:  R$", (310, 483))
        self.taxbox = wx.TextCtrl(result, 42, str(self.tax).replace(".", ","), (370, 476), size = (60,30))
        self.taxbox.Bind(wx.EVT_CHAR, self.tax_check, id=42)
        self.taxbox.SetValue("0,00")
        self.check_total()
        wx.StaticText(result, -1, u"Total da Venda:  R$", (255, 530))
        self.final = wx.TextCtrl(result, 214, str(good_show("money", str(self.final_price).replace(".", ","))), (370, 523), size = (60,30), style = wx.TE_READONLY)
        self.final.SetBackgroundColour("#C0C0C0")
        self.final.Refresh()
        wx.StaticLine(result, -1, (285,515), (150,1))
        if self.mode:
            self.trigo = shelve.open(self.mode[0])
            for i in self.trigo["sales"][self.mode[1]]['descriptions']:
                ps = self.trigo["sales"][self.mode[1]]['descriptions'].index(i)
                kill = "R$ " + good_show("money", str(self.trigo["sales"][self.mode[1]]['unit_prices'][ps]).replace(".", ","))
                hug = "R$ " + good_show("money", str(self.trigo["sales"][self.mode[1]]['prices'][ps]).replace(".", ","))
                self.selling.Append((i, self.trigo["sales"][mode[1]]['amounts'][ps], kill, hug))
            self.taxbox.SetValue(good_show("money", str(self.trigo["sales"][self.mode[1]]['tax']).replace(".", ",")))
            self.disc.SetValue(good_show("money", str(self.trigo["sales"][self.mode[1]]['discount']).replace(".", ",")))
            boot = self.trigo["sales"][self.mode[1]]['payment']
            if boot == u"Dinheiro": self.pay1.SetValue(True)
            elif boot == u"Cartão": self.pay2.SetValue(True)
            else:
                self.pay3.SetValue(True)
                self.pay3_.Unbind(wx.EVT_CHAR)
                self.pay3_.Bind(wx.EVT_CHAR, self.all_char)
                self.pay3_.SetBackgroundColour(wx.NullColour)
                self.pay3_.SetValue(boot)
            self.check_total()
            self.totval.SetValue(good_show('money', str(self.total_sell).replace(".", ",")))
            self.final.SetValue(good_show('money', str(self.final_price).replace(".", ",")))
            self.trigo.close()
        if delmode == 1:
            self.taxbox.SetBackgroundColour('#C0C0C0')
            self.taxbox.Disable()
            self.disc.SetBackgroundColour('#C0C0C0')
            self.disc.Disable()
            self.pay3_.SetBackgroundColour('#C0C0C0')
            self.pay3_.Disable()
            if not self.pay1.GetValue(): self.pay1.Disable()
            if not self.pay2.GetValue(): self.pay2.Disable()
            if not self.pay3.GetValue(): self.pay3.Disable()
        #product
        self.product = wx.Panel(self, 22, pos=(460, 5), size=(450, 275), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.product.SetBackgroundColour('#D6D6D6')
        if delmode == 0:
            self.prod_ = wx.Panel(self.product, size=(300, 40), pos=(100, 225), style = wx.SIMPLE_BORDER)
            self.plus = GenBitmapTextButton(self.prod_, 220, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u"Adicionar", pos = (0, 0), size = (100,40))
            self.plus.Bind(wx.EVT_BUTTON, self.add_item, id=220)
            self.edit = GenBitmapTextButton(self.prod_, 221, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (100, 0), size = (100, 40))
            self.edit.Bind(wx.EVT_BUTTON, self.editer, id=221)
            self.remov = GenBitmapTextButton(self.prod_, 222, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (200, 0), size = (100,40))
            self.remov.Bind(wx.EVT_BUTTON, self.remove_item, id=222)
        wx.StaticText(self.product, -1, u"Adicionar Produto", pos=(160, 8)).SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.description = wx.SearchCtrl(self.product, 223, pos=(10, 25), size = (430,30))
        self.description.Bind(wx.EVT_TEXT, self.searcher, id=223)
        self.description.ShowSearchButton(False)
        self.description.SetDescriptiveText(u'Descrição do produto')
        self.oplist = wx.ListCtrl(self.product, -1, pos=(10, 60), size=(430, 115), style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.SIMPLE_BORDER)
        self.oplist.InsertColumn(0, u'Descrição', width=230)
        self.oplist.InsertColumn(1, u'Preço')
        self.oplist.InsertColumn(2, u'Estoque')
        self.oplist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.filler)
        self.starter()
        wx.StaticText(self.product, -1, u"Preço Unitário: R$", pos = (10, 192))
        self.price = wx.TextCtrl(self.product, 224, pos = (120, 185), size = (60,30))
        self.price.Bind(wx.EVT_CHAR, self.unit_check, id=224)
        self.price.SetValue("0,00")
        wx.StaticText(self.product, -1, u"Quantidade:", pos = (225, 192))
        self.amount = wx.TextCtrl(self.product, 225, pos = (300, 185), size = (40,30))
        self.amount.Bind(wx.EVT_CHAR, self.check_num, id = 225)
        if delmode==1:
            self.description.SetBackgroundColour('#C6C6C6')
            self.description.Disable()
            self.oplist.SetBackgroundColour('#C6C6C6')
            self.oplist.DeleteAllItems()
            self.oplist.Disable()
            self.price.Disable()
            self.amount.Disable()
        #client
        client = wx.Panel(self, 23, pos = (460, 285), size = (450, 325), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        client.SetBackgroundColour('#D6D6D6')
        wx.StaticText(client, -1, u"Nome do cliente: ", pos = (10, 5))
        self.client_name = wx.TextCtrl(client, -1, pos = (5, 25), size = (300,25))
        wx.StaticText(client, -1, u"ID: ", pos = (350, 5))
        self.client_id = wx.TextCtrl(client, -1, pos = (345, 25), size = (70,25))
        self.client_id.Bind(wx.EVT_CHAR, self.check_num)
        if delmode ==0:
            client_ = wx.Panel(client, -1, pos = (10,60), size = (400,40), style = wx.SIMPLE_BORDER)
            cold = GenBitmapTextButton(client_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Book.png', wx.BITMAP_TYPE_PNG), u'Selecionar Cliente', pos = (0,0), size = (150,40))
            cnew = GenBitmapTextButton(client_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Novo Cliente', pos = (150,0), size = (150,40))
            cno = GenBitmapTextButton(client_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Cancel.png', wx.BITMAP_TYPE_PNG), u'Limpar', pos = (300,0), size = (100,40))
            cold.Bind(wx.EVT_BUTTON, self.win3)
            cnew.Bind(wx.EVT_BUTTON, self.win10)
            cno.Bind(wx.EVT_BUTTON, self.c_cancel)
        self.delivery = wx.CheckBox(client, 213, u"Entrega?", (10, 110))
        self.delivery.Bind(wx.EVT_CHECKBOX, self.turn2)
        wx.StaticText(client, -1, u"Nome do recebente:", pos = (10, 130))
        self.del_rec = wx.TextCtrl(client, -1, pos = (10, 150), size = (350, 25))
        wx.StaticText(client, -1, u"Endereço da entrega:", pos = (10, 180))
        self.del_adr = wx.TextCtrl(client, -1, pos = (10, 200), size = (350, 25))
        wx.StaticText(client, -1, u"Telefone \ndo cliente:", pos = (10, 240))
        self.del_tel1 = wx.TextCtrl(client, -1, pos = (80, 240), size = (120,25))
        wx.StaticText(client, -1, u"Cidade:", pos = (215, 247))
        self.del_city = wx.TextCtrl(client, -1, pos = (260, 240), size = (100,25))
        wx.StaticText(client, -1, u"Data:", pos = (10, 287))
        self.del_date = wx.TextCtrl(client, -1, pos = (50, 280), size = (60,25))
        wx.StaticText(client, -1, u"Horário:", pos = (150, 287))
        self.del_hour = wx.TextCtrl(client, -1, pos = (200, 280), size = (60,25))
        self.turn2(1)
        if self.mode:
            self.tigre = shelve.open(self.mode[0])
            self.client_name.SetValue(self.tigre['sales'][mode[1]]['client_name'])
            self.client_id.SetValue(self.tigre['sales'][mode[1]]['client_id'])
            if self.tigre["sales"][self.mode[1]]['delivery']:
                self.delivery.SetValue(True)
                self.turn2(1)
                self.del_rec.SetValue(self.tigre["sales"][mode[1]]['receiver'])
                self.del_adr.SetValue(self.tigre["sales"][mode[1]]['adress'])
                self.del_tel1.SetValue(str(self.tigre["sales"][mode[1]]['tel1']))
                self.del_city.SetValue(self.tigre["sales"][mode[1]]['city'])
                self.del_date.SetValue(str(self.tigre["sales"][mode[1]]['date']))
                self.del_hour.SetValue(str(self.tigre["sales"][mode[1]]['hour']))
            self.tigre.close()
        if delmode==1:
            self.client_name.Disable()
            self.client_id.Disable()
            self.delivery.Disable()
            self.del_rec.SetBackgroundColour('#C0C0C0')
            self.del_rec.SetWindowStyle(wx.TE_READONLY)
            self.del_adr.SetBackgroundColour('#C0C0C0')
            self.del_adr.SetWindowStyle(wx.TE_READONLY)
            self.del_tel1.SetBackgroundColour('#C0C0C0')
            self.del_tel1.SetWindowStyle(wx.TE_READONLY)
            self.del_city.SetBackgroundColour('#C0C0C0')
            self.del_city.SetWindowStyle(wx.TE_READONLY)
            self.del_date.SetBackgroundColour('#C0C0C0')
            self.del_date.SetWindowStyle(wx.TE_READONLY)
            self.del_hour.SetBackgroundColour('#C0C0C0')
            self.del_hour.SetWindowStyle(wx.TE_READONLY)

        #last
        last = wx.Panel(self, 24, pos = (5, 615), size = (905, 50), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        last.SetBackgroundColour('#D6D6D6')
        if delmode==0:
            last_ = wx.Panel(last, pos = (292,5), size = (320,40), style = wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(last_, 240, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u"Finalizar",pos = (0, 0), size = (100,40))
            finish.Bind(wx.EVT_BUTTON, self.ask3, id = 240)
            restart = GenBitmapTextButton(last_, 241, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u"Recomeçar", pos=(100, 0), size = (120,40))
            restart.Bind(wx.EVT_BUTTON, self.ask1, id = 241)
            cancel = GenBitmapTextButton(last_, 242, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair", pos=(220, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.ask2, id = 242)
        elif delmode==1:
            last_ = wx.Panel(last, pos = (352,5), size = (200,40), style = wx.SIMPLE_BORDER)
            cancel = GenBitmapTextButton(last_, 242, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (0, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.closer)
            edit = GenBitmapTextButton(last_, 243, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u"Editar",pos = (100, 0), size = (100,40))
            edit.Bind(wx.EVT_BUTTON, self.win2_)

        self.Show()

    def win2_(self, event):
        sell(self.GetParent(), mode=self.mode)
        self.Close()
    def win3(self, event):
        clients(self, select=1)
    def win10(self, event):
        new_client(self)

    def c_cancel(self, event):
        self.client_name.Clear()
        self.client_id.Clear()

    def add_item(self, event):
        if not self.description.GetValue() or self.price.GetValue()=='0,00' or not self.amount.GetValue():
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        else:
            a = self.price.GetValue().replace(",",".")
            trem = int(self.amount.GetValue()) * float(a)
            hug = "R$ "+ good_show('money',str(trem))
            kill = "R$ " + good_show('money',str(float(a)))
            self.selling.Append(((self.description.GetValue().capitalize()), self.amount.GetValue(), kill, hug))
            self.amount.Clear()
            self.price.Clear()
            self.description.Clear()
            self.check_total()
            self.totval.SetValue(good_show('money', str(self.total_sell)))
            self.final.SetValue(good_show('money', str(self.final_price)))
            self.price.SetValue("0,00")

    def remove_item(self, event):
        if self.selling.GetFocusedItem()==-1:
            return
        self.selling.DeleteItem(self.selling.GetFocusedItem())
        self.check_total()
        self.totval.SetValue(good_show('money', str(self.total_sell)))
        self.final.SetValue(good_show('money', str(self.final_price)))

    def editer(self, event):
        self.item = self.selling.GetFocusedItem()
        if not self.item==-1:
            self.description.SetValue(self.selling.GetItemText(self.item, 0))
            self.price.SetValue(self.selling.GetItemText(self.item, 2).replace('R$ ', ''))
            self.amount.SetValue(self.selling.GetItemText(self.item, 1))
            self.plus.Destroy()
            self.edit.Destroy()
            self.remov.Destroy()
            self.prod_.Destroy()
            self.prod_ = wx.Panel(self.product, size = (200,40), pos = (200,225), style = wx.SIMPLE_BORDER)
            self.eplus = GenBitmapTextButton(self.prod_, 220, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u"Salvar", pos = (0, 0), size = (100,40))
            self.eplus.Bind(wx.EVT_BUTTON, self.edit_item)
            self.eremov = GenBitmapTextButton(self.prod_, 222, wx.Bitmap(current_dir + '\\data\\pics\\Cancel.png', wx.BITMAP_TYPE_PNG), u'Cancelar', pos = (100, 0), size = (100,40))
            self.eremov.Bind(wx.EVT_BUTTON, self.edit_cancel)

    def edit_item(self, event):
        if not self.description.GetValue() or self.price.GetValue()=='0,00' or not self.amount.GetValue() or self.selling.GetFocusedItem()==-1:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        else:
            trem = int(self.amount.GetValue()) * float(self.price.GetValue().replace(',', '.'))
            hug = "R$ "+ good_show('money', str(trem))
            kill = "R$ " + good_show('money', self.price.GetValue().replace(',', '.'))
            self.selling.SetStringItem(self.item, 0, self.description.GetValue())
            self.selling.SetStringItem(self.item, 1, self.amount.GetValue())
            self.selling.SetStringItem(self.item, 2, kill)
            self.selling.SetStringItem(self.item, 3, hug)
            self.amount.Clear()
            self.price.Clear()
            self.description.Clear()
            self.check_total()
            self.totval.SetValue(good_show('money', str(self.total_sell)))
            self.final.SetValue(good_show('money', str(self.final_price)))
            self.edit_cancel(event)

    def edit_cancel(self, event):
        self.description.Clear()
        self.price.SetValue('0,00')
        self.amount.Clear()
        self.eplus.Destroy()
        self.eremov.Destroy()
        self.prod_.Destroy()
        self.prod_ = wx.Panel(self.product, size = (300,40), pos = (100,225), style = wx.SIMPLE_BORDER)
        self.plus = GenBitmapTextButton(self.prod_, 220, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u"Adicionar", pos = (0, 0), size = (100,40))
        self.plus.Bind(wx.EVT_BUTTON, self.add_item, id = 220)
        self.edit = GenBitmapTextButton(self.prod_, 221, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (100, 0), size = (100, 40))
        self.edit.Bind(wx.EVT_BUTTON, self.editer, id = 221)
        self.remov = GenBitmapTextButton(self.prod_, 222, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (200, 0), size = (100,40))
        self.remov.Bind(wx.EVT_BUTTON, self.remove_item, id = 222)

    def closer(self, event):
        self.Close()

    def starter(self):
        self.pls = {}
        for root, dirs, files in os.walk('products'):
            if not root is 'products':
                try:
                    s = shelve.open(current_dir + '\\%s\\%s_infos.txt' %(root, root[9:]))
                    self.pls[root[9:]] = {}
                    x=0
                    for i in s:
                        self.pls[root[9:]][i] = s[i]
                        x+=1
                    s.close()
                    if not x:
                        shutil.rmtree(root)
                        del self.pls[root[9:]]
                except:
                    pass
        self.searcher(-1)

    def searcher(self, event):
        self.oplist.DeleteAllItems()
        self.praia = []
        self.mar = {}
        tex = self.description.GetValue()
        num = len(tex)
        for o in self.pls:
            try:
                fri = []
                for a in self.pls[o]['description'].split():
                    fri.append(lower(r_acentos(a[:num])))
                fri.append(lower(r_acentos(self.pls[o]['description'][:num])))
                if ((r_acentos(lower(tex))) in fri) or (tex == o):
                    self.mar[self.pls[o]['description']] = [o, good_show('money', str(self.pls[o]['price'])).replace('.',','), self.pls[o]['amount']]
                    self.praia.append(self.pls[o]['description'])
            except:
                pass
        self.praia.sort()
        for g in self.praia:
            self.oplist.Append((g, self.mar[g][1], self.mar[g][2]))

    def filler(self, event):
        j = self.oplist.GetFocusedItem()
        self.price.SetValue(self.oplist.GetItem(j, 1).GetText())
        self.description.SetFocus()
        self.description.SetValue(self.oplist.GetItemText(j))
        self.amount.SetFocus()

    def check_num(self, event):
        try:
            if len(event.GetEventObject().GetValue()):
                int(event.GetEventObject().GetValue())
            num = [48,49,50,51,52,53,54,55,56,57]
            pre = [8,9,127,314,316]
            pro = event.GetKeyCode()
            if pro in pre:
                event.Skip()
            elif pro in num:
                if event.GetEventObject() is self.client_id:
                    if len(self.client_id.GetValue())>=6:
                        self.client_id.SetValue(self.client_id.GetValue()[:6])
                        return
                event.Skip()
            elif pro==13:
                self.enter(event)
        except:
            event.GetEventObject().SetValue('')

    def enter(self, event):
        pro = event.GetKeyCode()
        if pro==13:
            self.add_item(event)

    def check_money(self, box, event):
        num = [48,49,50,51,52,53,54,55,56,57]
        dex = [8,127,314,316, 9]
        pro = event.GetKeyCode()
        rhyme = box.GetValue().replace(",", ".")
        try:
            if pro == dex[2] or pro == dex[3] or pro == dex[4]:
                event.Skip()
            elif pro == dex[0] or pro == dex[1]:
                wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
                box.SetValue(good_show("money", str(wer).replace(".", ",")))
                if box==self.taxbox or box==self.disc:
                    self.check_total()
                    self.totval.SetValue(good_show("money", str(self.total_sell).replace(".", ",")))
                    self.final.SetValue(good_show("money", str(self.final_price).replace(".", ",")))
            elif pro in num:
                if len(box.GetValue())==14:
                    box.SetValue('0,00')
                    return
                wes = float(rhyme)*10 + float(chr(pro))/100
                box.SetValue(good_show("money", str(wes).replace(".", ",")))
                if box==self.taxbox or box==self.disc:
                    self.check_total()
                    self.totval.SetValue(good_show("money", str(self.total_sell).replace(".", ",")))
                    self.final.SetValue(good_show("money", str(self.final_price).replace(".", ",")))
        except:
            box.SetValue("0,00")
            if box==self.taxbox or box==self.disc:
                self.check_total()
                self.totval.SetValue(good_show("money", str(self.total_sell).replace(".", ",")))
                self.final.SetValue(good_show("money", str(self.final_price).replace(".", ",")))

    def disc_check(self, event):
        self.check_money(self.disc, event)

    def tax_check(self, event):
        self.check_money(self.taxbox, event)

    def unit_check(self, event):
        self.check_money(self.price, event)
        self.enter(event)

    def check_total(self):
        z=0
        w = self.selling.GetItemCount()
        for i in range(0,w):
            ploft = self.selling.GetItem(i, 3).GetText()
            a = ploft.replace(",", ".").replace("R$ ", "")
            z+=float(a)
        self.discount = self.disc.GetValue().replace(",", ".")
        if self.discount=="":
            self.discount=float(0)
        else:
            self.discount=float(self.discount)
        self.tax = self.taxbox.GetValue().replace(",", ".")
        if self.tax=="":
            self.tax=float(0)
        else:
            self.tax=float(self.tax)
        self.total_sell = float(z)
        self.final_price = float(self.total_sell + self.tax - self.discount)

    def all_char(self, event):
        event.Skip()

    def hour_check(self, event):
        num = [48,49,50,51,52,53,54,55,56,57]
        dex = [8,127,314,316,9]
        pro = event.GetKeyCode()
        rhyme = self.del_hour.GetValue().replace(":", ".")
        if pro == dex[2] or pro == dex[3] or pro == dex[4]:
            event.Skip()
        elif pro == dex[0] or pro == dex[1]:
            wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
            wer2 = str(wer).replace(".", ":")
            self.del_hour.SetValue(good_show("hour", wer2))
        elif pro in num:
            wes = float(rhyme)*10 + float(chr(pro))/100
            if wes<24:
                wer2 = str(wes).replace(".", ":")
                self.del_hour.SetValue(good_show("hour", wer2))

    def date_check(self, event):
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        dex = [8, 127, 314, 316, 9]
        pro = event.GetKeyCode()
        rhyme = self.del_date.GetValue().replace("/", ".")
        if pro == dex[2] or pro == dex[3] or pro == dex[4]:
            event.Skip()
        elif pro == dex[0] or pro == dex[1]:
            wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
            self.del_date.SetValue(good_show("date", str(wer).replace(".", "/")))
        elif (pro in num) and float(rhyme) < 3.12:
            wes = float(rhyme)*10 + float(chr(pro))/100
            self.del_date.SetValue(good_show("date", str(wes).replace(".", "/")))

    def turn2(self, event):
        self.delivery_status = self.delivery.GetValue()
        if self.delivery.GetValue():
            self.del_rec.Unbind(wx.EVT_CHAR)
            self.del_rec.Bind(wx.EVT_CHAR, self.all_char)
            self.del_rec.SetBackgroundColour(wx.NullColour)
            self.del_rec.ClearBackground()
            self.del_adr.Unbind(wx.EVT_CHAR)
            self.del_adr.Bind(wx.EVT_CHAR, self.all_char)
            self.del_adr.SetBackgroundColour(wx.NullColour)
            self.del_adr.ClearBackground()
            self.del_tel1.Unbind(wx.EVT_CHAR)
            self.del_tel1.Bind(wx.EVT_CHAR, self.all_char)
            self.del_tel1.SetBackgroundColour(wx.NullColour)
            self.del_tel1.Bind(wx.EVT_CHAR, telcode)
            self.del_tel1.ClearBackground()
            self.del_city.Unbind(wx.EVT_CHAR)
            self.del_city.Bind(wx.EVT_CHAR, self.all_char)
            self.del_city.SetBackgroundColour(wx.NullColour)
            self.del_city.SetValue(u"Itatiba")
            self.del_city.ClearBackground()
            self.del_date.Unbind(wx.EVT_CHAR)
            self.del_date.Bind(wx.EVT_CHAR, self.date_check)
            self.del_date.SetBackgroundColour(wx.NullColour)
            a = str(datetime.now().month)
            if len(a)==1: a = '0' + a
            self.del_date.SetValue(good_show("date", ("%s/%s" %(datetime.now().day, a))))
            self.del_date.ClearBackground()
            self.del_hour.Unbind(wx.EVT_CHAR)
            self.del_hour.Bind(wx.EVT_CHAR, self.hour_check)
            self.del_hour.SetBackgroundColour(wx.NullColour)
            self.del_hour.SetValue("00:00")
            self.del_hour.ClearBackground()

        else:
            self.del_rec.Bind(wx.EVT_CHAR, no_char)
            self.del_rec.Clear()
            self.del_rec.SetBackgroundColour("#C0C0C0")
            self.del_adr.Bind(wx.EVT_CHAR, no_char)
            self.del_adr.Clear()
            self.del_adr.SetBackgroundColour("#C0C0C0")
            self.del_adr.ClearBackground()
            self.del_tel1.Bind(wx.EVT_CHAR, no_char)
            self.del_tel1.Clear()
            self.del_tel1.SetBackgroundColour("#C0C0C0")
            self.del_tel1.ClearBackground()
            self.del_city.Bind(wx.EVT_CHAR, no_char)
            self.del_city.Clear()
            self.del_city.SetBackgroundColour("#C0C0C0")
            self.del_city.ClearBackground()
            self.del_date.Bind(wx.EVT_CHAR, no_char)
            self.del_date.Clear()
            self.del_date.SetBackgroundColour("#C0C0C0")
            self.del_date.ClearBackground()
            self.del_hour.Bind(wx.EVT_CHAR, no_char)
            self.del_hour.Clear()
            self.del_hour.SetBackgroundColour("#C0C0C0")
            self.del_hour.ClearBackground()

    def turn1(self, event):
        if self.pay3.GetValue():
            self.pay3_.Unbind(wx.EVT_CHAR)
            self.pay3_.Bind(wx.EVT_CHAR, self.all_char)
            self.pay3_.SetBackgroundColour(wx.NullColour)
            self.pay3_.ClearBackground()
        else:
            self.pay3_.Unbind(wx.EVT_CHAR)
            self.pay3_.Bind(wx.EVT_CHAR, no_char)
            self.pay3_.Clear()
            self.pay3_.SetBackgroundColour("#C0C0C0")
            self.pay3_.ClearBackground()

    def ask1(self, event):
        ask(self, -1, u"Apagar Tudo", 1, 1)

    def ask2(self, event):
        if self.selling.GetItemCount()==0 and not self.delivery.GetValue():
            self.Close()
            return
        ask(self, -1, u"Sair", 2, 1)

    def ask3(self, event):
        ask(self, -1, u"Finalizar Venda", 3, 1)

    def clean(self):
        self.selling.DeleteAllItems()
        self.amount.Clear()
        self.price.Clear()
        self.disc.Clear()
        self.taxbox.Clear()
        self.description.Clear()
        self.taxbox.SetValue("0,00")
        self.disc.SetValue("0,00")
        self.price.SetValue("0,00")
        self.delivery.SetValue(False)
        self.turn2(False)
        self.pay1.SetValue(True)
        self.turn1(False)
        self.check_total()
        self.totval.SetValue(good_show("money", str(self.total_sell).replace(".", ",")))
        self.final.SetValue(good_show("money", str(self.final_price).replace(".", ",")))
        self.searcher(1)

    def end_sell(self):
        w = self.selling.GetItemCount()
        if w==0:
            a = wx.MessageDialog(self, u'Você não adicionou nenhum produto!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        if not os.path.exists('saves'):
            os.mkdir('saves')
        self.descriptions = []
        self.amounts = []
        self.unit_prices = []
        self.prices = []
        for i in range(0, w):
            ploft1 = self.selling.GetItem(i, 0).GetText()
            self.descriptions.append(ploft1)
            ploft2 = self.selling.GetItem(i, 1).GetText()
            self.amounts.append(int(ploft2))
            ploft3 = self.selling.GetItem(i, 2).GetText()
            a = float(ploft3.replace(",", ".").replace("R$ ", ""))
            self.unit_prices.append(a)
            ploft4 = self.selling.GetItem(i, 3).GetText()
            b = float(ploft4.replace(",", ".").replace("R$ ", ""))
            self.prices.append(b)
        self.check_total()
        self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        if self.pay1.GetValue(): self.payment = u"Dinheiro"
        if self.pay2.GetValue(): self.payment = u"Cartão"
        if self.pay3.GetValue(): self.payment = self.pay3_.GetValue()
        self.cliname = self.client_name.GetValue()
        self.cliid = self.client_id.GetValue()
        while len(self.cliid)<6:
            self.cliid = '0' + self.cliid
        self.recval = self.del_rec.GetValue()
        self.adrval = self.del_adr.GetValue()
        self.cityval = self.del_city.GetValue()
        self.tel1val = self.del_tel1.GetValue()
        self.dateval = self.del_date.GetValue()
        self.hourval = self.del_hour.GetValue()
        if self.delivery_status:
            for r in self.recval,self.adrval,self.cityval,self.tel1val,self.dateval,self.hourval:
                if len(r)==0 or r=='00:00':
                    a = wx.MessageDialog(self, u'Dados insulficientes para registro de entrega!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
                    a.ShowModal()
                    a.Destroy()
                    return
        self.info = current_dir + "\\saves\\" + date + ".txt"
        self.day_sell = shelve.open(self.info)
        if "sales" not in self.day_sell:
            self.day_sell["sales"] = {}
            self.day_sell["secount"] = 0
            self.day_sell["edit"] = {}
            self.day_sell["spent"] = {}
            self.day_sell["spcount"] = 0
            self.day_sell["closure"] = []
            self.day_sell["wastes"] = {}
            self.day_sell["wcount"] = 0
        if not self.mode:
            key = self.day_sell["secount"] + 1
            asn = self.day_sell["sales"]
            asn[key] = {'time': self.finish_time,
                        'edit': 0,
                        'descriptions': self.descriptions,
                        'amounts': self.amounts,
                        'unit_prices': self.unit_prices,
                        'prices': self.prices,
                        'sold': self.total_sell,
                        'discount': self.discount,
                        'tax': self.tax,
                        'value': self.final_price,
                        'payment': self.payment,
                        'client_name': self.cliname,
                        'client_id': self.cliid,
                        'delivery': self.delivery_status,
                        'receiver': self.recval,
                        'adress': self.adrval,
                        'tel1': self.tel1val,
                        'city': self.cityval,
                        'date': self.dateval,
                        'hour': self.hourval}
            self.day_sell["sales"] = asn
            self.day_sell["secount"] = key
            if self.delivery_status:
                self.deliverys = shelve.open(current_dir + "\\saves\\deliverys.txt")
                asrk = str(date) + ' ' + str(self.finish_time)
                self.deliverys[asrk] = [key, False, '']
                self.deliverys.close()
        else:
            self.day_sell.close()
            self.day_sell = shelve.open(self.mode[0])
            key = self.mode[1]
            hour = self.mode[2]
            asn = self.day_sell["sales"]
            nsa = self.day_sell["edit"]
            old = self.day_sell["sales"][key]
            nsa[self.finish_time] = self.day_sell["sales"][key]
            nsa[self.finish_time]['key'] = key
            nsa[self.finish_time]['mode'] = 1
            self.day_sell["edit"] = nsa
            asn[key] = {'time': hour,
                        'edit': 1,
                        'descriptions': self.descriptions,
                        'amounts': self.amounts,
                        'unit_prices': self.unit_prices,
                        'prices': self.prices,
                        'sold': self.total_sell,
                        'discount': self.discount,
                        'tax': self.tax,
                        'value': self.final_price,
                        'payment': self.payment,
                        'client_name': self.cliname,
                        'client_id': self.cliid,
                        'delivery': self.delivery_status,
                        'receiver':self.recval,
                        'adress': self.adrval,
                        'tel1': self.tel1val,
                        'city': self.cityval,
                        'date': self.dateval,
                        'hour': self.hourval}
            self.day_sell['sales'] = asn
            if self.delivery_status:
                self.deliverys = shelve.open(current_dir + "\\saves\\deliverys.txt")
                asrk = self.mode[0].split("\\")[-1][:-4] + ' ' + str(hour)
                if asrk in self.deliverys:
                    tf = self.deliverys[asrk][1]
                else:
                    tf = False
                self.deliverys[str(asrk)] = [key, tf, '']
                self.deliverys.close()
        if self.mode:
            for f in old['descriptions']:
                g=0
                k = old['descriptions'].index(f)
                l = old['unit_prices'][k]
                m = old['amounts'][k]
                for ids in self.pls:
                    if lower(f) == lower(self.pls[ids]['description']) and l == self.pls[ids]['price']:
                        q = current_dir + '\\products\\%s\\%s_infos.txt' %(ids, ids)
                        s = shelve.open(q)
                        try:
                            v = int(s['amount'].replace(' ',''))
                            if v<0:
                                s['amount'] = 0
                            else:
                                s['amount'] = v + m
                        except:
                            pass
                        s.close()
                        g=1
                        break
                if g==1:
                    w = current_dir + '\\products\\%s\\%s_sales.txt' %(ids, ids)
                    tu = self.mode[0].split('\\')
                    r = str('%s_%s' %(tu[-1][:-4], self.mode[2].replace(':','-')))
                    d = shelve.open(w)
                    des = d
                    if r in des:
                        del des[r]
                    d = des
                    d.close()
            if old['client_id']:
                if old['client_id'] in os.listdir('clients'):
                    try:
                        w = current_dir + '\\clients\\%s\\%s_deals.txt' %(old['client_id'],old['client_id'])
                        tu = self.mode[0].split('\\')
                        r = str('%s_%s' %(tu[1][:-4], self.mode[2].replace(':','-')))
                        d = shelve.open(w)
                        qu = d
                        if r in qu:
                            del qu[r]
                        d = qu
                        d.close()
                    except:
                        pass
        for f in self.descriptions:
            g=0
            k = self.descriptions.index(f)
            l = self.unit_prices[k]
            m = self.amounts[k]
            for ids in self.pls:
                if lower(f)==lower(self.pls[ids]['description']) and l==self.pls[ids]['price']:
                    q = current_dir + '\\products\\%s\\%s_infos.txt' %(ids, ids)
                    s = shelve.open(q)
                    try:
                        v = int(s['amount'].replace(' ',''))
                        if v-m<0:
                            s['amount'] = 0
                        else:
                            s['amount'] = v - m
                    except:
                        pass
                    s.close()
                    g=1
                    break
            if g==1:
                w = current_dir + '\\products\\%s\\%s_sales.txt' %(ids, ids)
                r = '%s_%s' % (date, self.finish_time.replace(':', '-'))
                d = shelve.open(w)
                x = asn[key]
                x['key'] = key
                d[r] = x
                d.close()
        if self.cliid:
            try:
                int(self.cliid)
                if self.cliid in os.listdir('clients'):
                    w = current_dir + '\\clients\\%s\\%s_deals.txt' %(self.cliid, self.cliid)
                    r = '%s_%s' % (date, self.finish_time.replace(':', '-'))
                    d = shelve.open(w)
                    x = asn[key]
                    x['key'] = key
                    d[r] = x
                    d.close()
            except:
                pass
        self.clean()
        self.day_sell.close()
        if not self.mode:
            confirmation(self, -1, u"Sucesso", 1)
        else:
            if type(self.GetParent()) is report:
                self.GetParent().run()
            self.Close()


class ProgramedSales(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Agendamento de vendas'):
        wx.Frame.__init__(self, parent,frame_id, title, size=(900, 430), pos = (250, 100), style =wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(general_icon)
        self.pilot = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.pdel = wx.gizmos.TreeListCtrl(self.pilot, -1, pos=(10, 10), size=(710, 360), style = wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES|wx.LC_HRULES)
        self.pdel.InsertColumn(0, u"Data", width=120)
        self.pdel.InsertColumn(1, u"", width=120)
        self.pdel.InsertColumn(2, u"Endereço", width=300)
        self.pdel.InsertColumn(3, u"Para", width=190)
        self.final = wx.Panel(self, -1, size=(140, 380), pos=(750, 10), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        tell = wx.Button(self.final, -1, u'Mostrar mais', pos=(20, 150), size=(100, 30))
        tell.Bind(wx.EVT_BUTTON, self.win2_)
        wx.StaticText(self.final, -1, u"Entregas entre:", pos = (5,10))
        wx.StaticText(self.final, -1, "e:", pos = (5,70))
        self.finalb = wx.Panel(self.final, pos = (10,220), size = (120,120), style = wx.SIMPLE_BORDER)
        ready = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png'), u"Concluída", pos = (0,0), size = (120,40))
        ready.Bind(wx.EVT_BUTTON, self.ready)
        up = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png'), u"Atualizar", pos = (0,40), size = (120,40))
        up.Bind(wx.EVT_BUTTON, self.gogogo)
        down = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png'), u'Sair', pos = (0,80), size = (120,40))
        down.Bind(wx.EVT_BUTTON, self.closer)
        self.gogogo(1)
        self.Show()

    def win2_(self, event):
        red = self.pdel.GetFocusedItem()
        if red==-1:
            return
        avatar = self.pdel.GetItemText(red)
        earth = shelve.open(current_dir + '\\saves\\' + self.maresia[avatar][0] + '.txt')
        brown = earth['sales'][self.maresia[avatar][1]]['time']
        sell(self, mode=[(current_dir + "\\saves\\" + self.maresia[avatar][0] + '.txt'), self.maresia[avatar][1], brown], delmode=1)
        earth.close()

    def ready(self, event):
        red = self.pdel.GetFocusedItem()
        if red==-1:
            return
        date = self.pdel.GetItemText(red)
        tempo= self.pdel.GetItemText(red, 1)
        adr = self.pdel.GetItemText(red, 2)
        nam = self.pdel.GetItemText(red, 3)
        paco = shelve.open(current_dir + '\\saves\\deliverys.txt')
        for a in self.maresia:
            if date==self.maresia[a][1] and tempo==self.maresia[a][2] and adr==self.maresia[a][3] and nam==self.maresia[a][4]:
                tempo= str(datetime.now().hour) + ':' + str(datetime.now().minute)
                if paco[a][1]:
                    paco[a] = [date, False, tempo]
                else:
                    paco[a] = [date, True, tempo]
        paco.close()
        self.starter(event)

    def starter(self, event):
        self.pdel.DeleteAllItems()
        gas = shelve.open(current_dir + '\\saves\\deliverys.txt')
        e1 = self.alpha.GetValue()
        w1 = self.zetta.GetValue()
        earth = datetime_int(2,self.fall[self.son.index(e1)])
        water = datetime_int(2,self.fall[self.son.index(w1)])
        emax = max((earth,water))
        emin = min((earth,water))
        for i in gas:
            fire = datetime_int(2,self.maresia[i][1])
            if emin<=fire<=emax:
                tyr = self.pdel.Append((self.maresia[i][1], self.maresia[i][2], self.maresia[i][3], self.maresia[i][4]))
                if gas[i][1]: self.pdel.SetItemTextColour(tyr, '#ADADAD')
        gas.close()

    def gogogo(self, event):
        today1 = datetime_int(2, str(datetime.now().year) + '-' + good_show("o", str(datetime.now().month)) + '-' + good_show("o", str(datetime.now().day)))
        gas=shelve.open(current_dir + '\\saves\\deliverys.txt')
        self.maresia = {}
        for i in gas:
            key = gas[i][0]
            date1, time1 = i.split()
            air = shelve.open(current_dir + '\\saves\\' + date1 + '.txt')
            adr = s_acentos(str(air['sales'][key]['city']) + ' - ' + str(air['sales'][key]['adress']))
            rec  = s_acentos(r_acentos(air['sales'][key]['receiver']))
            tempo= str(air['sales'][key]['hour'])
            date = str(air['sales'][key]['date'])
            if int(date_reverse(date.replace('/', '-')).replace('-', '')) < int(str(datetime.now().month) + good_show("o", str(datetime.now().day))):
                date = date + '/' + str(datetime.now().year+1)
            else:
                date = date + '/' + str(datetime.now().year)
            self.maresia[i] = [key, date, tempo, adr, rec]
            air.close()
        water = today1
        for i in gas:
            date = self.maresia[i][1]
            fire = datetime_int(2, date)
            if fire < today1:
                g = gas
                del g[i]
                gas = g
            elif fire > water:
                water = fire
        b = today1
        self.fall = []
        while b <= water:
            self.fall.append(datetime_int(3, b))
            b += 1
        self.fall.sort()
        self.gon = []
        self.son = []
        for i in self.fall:
            self.gon.append(i)
            nert = i[8:10] + '/' + i[5:7] + '/' + i[:4]
            self.son.append(nert)
        self.alpha = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 30), style=wx.CB_READONLY)
        self.alpha.Bind(wx.EVT_COMBOBOX, self.starter)
        self.alpha.SetValue(self.son[0])
        self.zetta = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 90), style=wx.CB_READONLY)
        self.zetta.Bind(wx.EVT_COMBOBOX, self.starter)
        self.zetta.SetValue(self.son[len(self.son)-1])
        gas.close()
        self.starter(event)

    def closer(self,event):
        self.Close()


class clients(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Clientes', select=0):
        wx.Frame.__init__(self, parent,frame_id, title, style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetPosition(wx.Point(100, 100))
        self.SetSize(wx.Size(1200, 550))
        self.parent = parent
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.pilot = wx.Panel(self, pos=(10, 10), size=(1180, 100))
        if select:
            sele = GenBitmapTextButton(self.pilot, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u'Selecionar', pos = (50, 40), size = (100, 40), style = wx.SIMPLE_BORDER)
            sele.SetBackgroundColour('#D6D6D6')
            sele.Bind(wx.EVT_BUTTON, self.select_entry)
        self.pilot_ = wx.Panel(self.pilot, -1, size=(400, 40), pos=(200, 40), style=wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(self.pilot_, -1, wx.Bitmap(current_dir + '\\data\\pics\\user-info.png', wx.BITMAP_TYPE_PNG), u'Ver Mais', pos = (0, 0), size = (100, 40))
        see.SetBackgroundColour('#D6D6D6')
        see.Bind(wx.EVT_BUTTON, self.see_entry)
        plus = GenBitmapTextButton(self.pilot_, -1, wx.Bitmap(current_dir + '\\data\\pics\\contact-new.png', wx.BITMAP_TYPE_PNG), u'Novo', pos = (100, 0), size = (100, 40))
        plus.SetBackgroundColour('#D6D6D6')
        plus.Bind(wx.EVT_BUTTON, self.win10)
        edi = GenBitmapTextButton(self.pilot_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (200, 0), size = (100, 40))
        edi.SetBackgroundColour('#D6D6D6')
        edi.Bind(wx.EVT_BUTTON, self.edit_entry)
        era = GenBitmapTextButton(self.pilot_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (300, 0), size = (100, 40))
        era.SetBackgroundColour('#D6D6D6')
        era.Bind(wx.EVT_BUTTON, self.ask1)
        self.seatex = wx.SearchCtrl(self.pilot, -1, pos = (650,45), size = (200,30), style = wx.TE_PROCESS_ENTER)
        self.seatex.SetDescriptiveText(u'Busca por nome')
        self.seatex.ShowCancelButton(True)
        self.seatex.SetCancelBitmap(wx.Bitmap(current_dir + '\\data\\pics\\Erase2.png', wx.BITMAP_TYPE_PNG))
        fin = wx.BitmapButton(self.pilot, -1, wx.Bitmap(current_dir + '\\data\\pics\\edit_find.png'), pos = (855, 42), size = (35, 35))
        fin.Bind(wx.EVT_BUTTON, self.searcher)
        self.seatex.Bind(wx.EVT_TEXT_ENTER, self.searcher)
        self.seatex.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.searcher)
        self.seatex.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.sclean)
        self.pilot__ = wx.Panel(self.pilot, size = (240,40), pos = (900,40), style = wx.SIMPLE_BORDER)
        quir = GenBitmapTextButton(self.pilot__, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png'), u'Sair', pos = (120, 0), size = (120, 40))
        quir.SetBackgroundColour('#D6D6D6')
        quir.Bind(wx.EVT_BUTTON, self.closer)
        rep = GenBitmapTextButton(self.pilot__, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png'), u'Atualizar', pos = (0, 0), size = (120, 40))
        rep.SetBackgroundColour('#D6D6D6')
        rep.Bind(wx.EVT_BUTTON, self.power_on)
        self.other = wx.Panel(self, -1, pos = (10, 110), size = (1180,410))
        self.clilist = wx.ListCtrl(self.other, -1, pos = (5, 5), size = (1170,390), style = wx.LC_VRULES|wx.LC_HRULES|wx.SIMPLE_BORDER|wx.LC_REPORT)
        self.clilist.InsertColumn(0, u'Nome do cliente', width = 400)
        self.clilist.InsertColumn(1, u'ID', width = 50)
        self.clilist.InsertColumn(2, u'Telefone', width = 200)
        self.clilist.InsertColumn(3, u'e-mail', width = 200)
        self.clilist.InsertColumn(4, u'Endereço', width = 315)
        if select == 0:
            self.clilist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.see_entry)
        else:
            self.clilist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.select_entry)
        self.starting = False
        self.power_on(1)
        self.Show()

    def power_on(self, event):
        if not self.starting:
            return
        turn = threading.Thread(target=self._power_on, args=True)
        turn.daemon = True
        turn.start()

    def _power_on(self):

        self.clilist.DeleteAllItems()
        self.seatex.Clear()
        self.praia = []
        self.mar = {}
        for root, dirs, files in os.walk('clients'):
            if root != 'clients':
                try:
                    o = shelve.open(current_dir + '\\' + root + '\\' +  root.split('\\')[1] + '_infos.txt')
                    if not o['tel1']:
                        if o['tel2']: tel = o['tel2']
                        else:
                            tel = '(__)____-____'
                    else: tel = o['tel1']
                    if o['adress'] and o['city'] and o['state']!='--':
                        ad = o['city'] + ' - ' + o['state'] + ', ' + o['adress']
                    else:
                        ad = '_____-__,_________ '
                    self.mar[o['name']] = [str(int(root.split('\\')[1])), tel, o['email'], ad]
                    self.praia.append(o['name'])
                    o.close()
                except:
                    pass
        self.praia.sort()
        for g in self.praia:
            self.clilist.Append((g, self.mar[g][0], self.mar[g][1], self.mar[g][2], self.mar[g][3]))

    def del_entry(self, event):
        it = self.clilist.GetFocusedItem()
        if it==-1:
            return
        e_id = self.clilist.GetItem(it, 1).GetText()
        rtime = good_show("o", str(datetime.now().hour)) + "-" + good_show("o", str(datetime.now().minute)) + "-" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        dt = '%s_%s' %(rdate, rtime)
        while len(e_id)<6:
            e_id = '0' + e_id
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/clients'):
            os.mkdir('#Trash/clients')
        if not os.path.exists('#Trash/clients/deleted'):
            os.mkdir('#Trash/clients/deleted')
        if not os.path.exists('#Trash/clients/deleted/' + e_id):
            os.mkdir('#Trash/clients/deleted/' + e_id)
        shutil.copytree('clients/' + e_id, '#Trash/clients/deleted/%s/%s' %(e_id,dt))
        dirs = os.listdir('clients')
        for i in dirs:
            if int(i)==int(e_id):
                shutil.rmtree('clients/' + i)
        self.power_on(1)

    def edit_entry(self, event):
        po = self.clilist.GetFocusedItem()
        if po == -1:
            return
        lo = self.clilist.GetItem(po, 1).GetText()
        ko = self.clilist.GetItemText(po)
        old_client(self, -1, ko, lo, 1)

    def see_entry(self, event):
        po = self.clilist.GetFocusedItem()
        if po ==-1:
            return
        lo = self.clilist.GetItem(po, 1).GetText()
        ko = self.clilist.GetItemText(po)
        old_client(self, -1, ko, lo, 0)

    def select_entry(self, event):
        g = self.clilist.GetFocusedItem()
        if g == -1:
            return
        name = self.clilist.GetItemText(g, 0)
        client_id = self.clilist.GetItemText(g, 1)
        while len(id) < 6:
           client_id = '0' +client_id
        self.parent.client_name.SetValue(name)
        self.parent.client_id.SetValue(id)
        self.Close()

    def searcher(self, event):
        self.clilist.DeleteAllItems()
        self.praia = []
        self.mar = {}
        for root, dirs, files in os.walk('clients'):
            if root != 'clients':
                try:
                    o = shelve.open(current_dir + "\\" + root + '\\' +  root.split('\\')[1] + '_infos.txt')
                    tex = lower(self.seatex.GetValue())
                    num = len(tex)
                    fri = []
                    for a in o['name'].split():
                        fri.append(lower(a[:num]))
                    if (tex in fri) or (tex == str(int(root.split('\\')[1]))):
                        if not o['tel1']:
                            if o['tel2']: tel = o['tel2']
                            else:
                                tel = '(__)____-____'
                        else: tel = o['tel1']
                        if o['adress'] and o['city'] and o['state']!='--':
                            ad = o['city'] + ' - ' + o['state'] + ', ' + o['adress']
                        else:
                            ad = '_____-__,_________ '
                        self.mar[o['name']] = [str(int(root.split('\\')[1])), tel, o['email'], ad]
                        self.praia.append(o['name'])
                    o.close()
                except:
                    pass
        self.praia.sort()
        for g in self.praia:
            self.clilist.Append((g, self.mar[g][0], self.mar[g][1], self.mar[g][2], self.mar[g][3]))

    def sclean(self, event):
        self.seatex.Clear()
        self.power_on(event)

    def ask1(self, event):
        ask(self, -1, u'Apagar Cliente', 4, 7)

    def win10(self, event):
        new_client(self)

    def closer(self, event):
        self.Close()


class new_client(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Cadastro de Clientes'):
        wx.Frame.__init__(self, parent,frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        self.SetSize(wx.Size(500, 585))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.Centre()
        self.infos = wx.Panel(self, -1, pos = (0,0), size = (500,500), style = wx.TAB_TRAVERSAL)
        wx.StaticText(self.infos, -1, u'Nome do cliente:', pos = (190,10))
        self.cname = wx.TextCtrl(self.infos, -1, pos = (190, 30), size = (300, 30))
        wx.StaticText(self.infos, -1, u'Sexo:', pos = (190,70))
        self.csex = wx.ComboBox(self.infos, -1, choices = [u'Feminino', u'Maculino'], pos = (190, 90), size = (120, 30), style = wx.CB_READONLY)
        self.csex.SetValue(u'Feminino')
        wx.StaticText(self.infos, -1, u'Data de Nascimento:', pos = (340,70))
        self.cbirth = wx.TextCtrl(self.infos, -1, pos = (340, 90), size = (120, 30))
        self.cbirth.SetValue(u'__/__/____')
        self.cbirth.Bind(wx.EVT_CHAR, dmy)
        wx.StaticText(self.infos, -1, u'Telefone 1:', pos = (190,130))
        self.ctel1 = wx.TextCtrl(self.infos, -1, pos = (190, 150), size = (120, 30))
        self.ctel1.Bind(wx.EVT_CHAR, telcode)
        wx.StaticText(self.infos, -1, u'Telefone 2:', pos = (340,130))
        self.ctel2 = wx.TextCtrl(self.infos, -1, pos = (340, 150), size = (120, 30))
        self.ctel2.Bind(wx.EVT_CHAR, telcode)
        wx.StaticText(self.infos, -1, u'e-mail:', pos = (10,190))
        self.cmail = wx.TextCtrl(self.infos, -1, pos = (10, 210), size = (300, 30))
        wx.StaticText(self.infos, -1, u'CPF:', pos = (340,190))
        self.ccpf = wx.TextCtrl(self.infos, -1, pos = (340, 210), size = (120, 30))
        self.ccpf.Bind(wx.EVT_CHAR, cpfcode)
        wx.StaticText(self.infos, -1, u'Estado:', pos = (10,250))
        self.cstate = wx.ComboBox(self.infos, -1, choices = brstates, pos = (10, 270), size = (60, 30), style = wx.CB_READONLY)
        self.cstate.SetValue('SP')
        wx.StaticText(self.infos, -1, u'Cidade:', pos = (100,250))
        self.ccity = wx.TextCtrl(self.infos, -1, pos = (100, 270), size = (150, 30))
        self.ccity.SetValue(u'Itatiba')
        wx.StaticText(self.infos, -1, u'Bairro:', pos = (280,250))
        self.chood = wx.TextCtrl(self.infos, -1, pos = (280, 270), size = (150, 30))
        wx.StaticText(self.infos, -1, u'Endereço:', pos = (10,310))
        self.cadress = wx.TextCtrl(self.infos, -1, pos = (10, 330), size = (300, 30))
        wx.StaticText(self.infos, -1, u'Observações:', pos = (10,370))
        self.cobs = wx.TextCtrl(self.infos, -1, pos = (10, 390), size = (480, 100), style = wx.TE_MULTILINE)
        self.ima = wx.Panel(self.infos, -1, size = (150,150), pos = (10,25), style = wx.SIMPLE_BORDER)
        self.ima.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.ima, self.OnPaint)
        self.last = wx.Panel(self, -1, pos = (0, 500), size = (500, 50))
        self.last_ = wx.Panel(self.last, pos=(90,5),size=(320,40), style = wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u"Finalizar",pos = (0, 0), size = (100,40))
        finish.Bind(wx.EVT_BUTTON, self.ask1)
        restart = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u"Recomeçar", pos = (100, 0), size = (120,40))
        restart.Bind(wx.EVT_BUTTON, self.ask2)
        cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (220, 0), size = (100,40))
        cancel.Bind(wx.EVT_BUTTON, self.ask3)

        self.Show()

    def ask1(self, event):
        ask(self, -1, u'Finalizar Cadastro', 3, 6)

    def ask2(self, event):
        ask(self, -1, u'Recomeçar', 1, 6)

    def ask3(self, event):
        if self.cname.GetValue():
            ask(self, -1, u'Sair', 2, 6)
        else:
            self.Close()

    def clean(self):
        self.cname.SetValue(u'')
        self.csex.SetValue(u'Feminino')
        self.cbirth.SetValue(u'__/__/____')
        self.ctel1.SetValue(u'')
        self.ctel2.SetValue(u'')
        self.cmail.SetValue(u'')
        self.ccpf.SetValue(u'')
        self.cstate.SetValue(u'SP')
        self.ccity.SetValue(u'Itatiba')
        self.chood.SetValue(u'')
        self.cadress.SetValue(u'')
        self.cobs.SetValue(u'')

    def end(self):
        if not self.cname.GetValue():
            a = wx.MessageDialog(self, u'É necessário o nome, para o cadastro', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
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
            if int(i)>last_id:
                last_id = int(i)
        new_id = last_id + 1
        idstr = str(new_id)
        while len(idstr)<6:
            idstr = '0'+idstr
        os.mkdir('clients/' + idstr)
        rtime = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        po = (current_dir + '\\clients\\' + idstr + '\\' + idstr + '_infos.txt')
        s = shelve.open(po)
        xname = self.cname.GetValue()
        while xname[0]==' ':
            xname = xname[1:]
        names = xname.split()
        for i in range(0,len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['name'] = namef
        s['sex'] = self.csex.GetValue()
        s['birth'] = self.cbirth.GetValue()
        s['email'] = self.cmail.GetValue()
        s['cpf'] = self.ccpf.GetValue()
        s['tel1'] = self.ctel1.GetValue()
        s['tel2'] = self.ctel2.GetValue()
        s['state'] = self.cstate.GetValue()
        s['city'] = self.ccity.GetValue()
        s['hood'] = self.chood.GetValue()
        s['adress'] = self.cadress.GetValue()
        s['obs'] = self.cobs.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        self.clean()
        parent = self.GetParent()
        if type(parent) is clients:
            parent.power_on(1)
        if type(parent) is sell:
            parent.client_name.SetValue(namef)
            parent.client_id.SetValue(idstr)
            self.Close()
            return
        confirmation(self, -1, u'Sucesso', 4)

    def OnPaint(self, event):
        wx.PaintDC(self.ima).DrawBitmap(wx.Bitmap(current_dir + '\\data\\pics\\stock_person.png'), 0, 0)


class old_client(wx.Frame):
    def __init__(self, parent,frame_id, title, key, mode = 0):
        wx.Frame.__init__(self, parent,frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        self.SetSize(wx.Size(850, 585))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.Centre()
        self.mode = mode
        key = str(key)
        while len(key)<6:
            key = '0' + key
        self.key = key
        self.title = title
        self.parent = parent
        self.infos = wx.Panel(self, -1, pos = (0,0), size = (500,500), style = wx.TAB_TRAVERSAL)
        wx.StaticText(self.infos, -1, u'Nome do cliente:', pos = (190,10))
        self.cname = wx.TextCtrl(self.infos, -1, pos = (190, 30), size = (300, 30))
        wx.StaticText(self.infos, -1, u'Sexo:', pos = (190,70))
        if mode==1:
            self.csex = wx.ComboBox(self.infos, -1, choices = [u'Feminino', u'Maculino'], pos = (190, 90), size = (120, 30), style = wx.CB_READONLY)
        elif mode==0:
            self.csex = wx.TextCtrl(self.infos, -1, pos = (190, 90), size = (100, 30))
        wx.StaticText(self.infos, -1, u'Data de Nascimento:', pos = (340,70))
        self.cbirth = wx.TextCtrl(self.infos, -1, pos = (340, 90), size = (120, 30))
        self.cbirth.SetValue('__/__/____')
        self.cbirth.Bind(wx.EVT_CHAR, dmy)
        wx.StaticText(self.infos, -1, u'Telefone 1:', pos = (190,130))
        self.ctel1 = wx.TextCtrl(self.infos, -1, pos = (190, 150), size = (120, 30))
        self.ctel1.Bind(wx.EVT_CHAR, telcode)
        wx.StaticText(self.infos, -1, u'Telefone 2:', pos = (340,130))
        self.ctel2 = wx.TextCtrl(self.infos, -1, pos = (340, 150), size = (120, 30))
        self.ctel2.Bind(wx.EVT_CHAR, telcode)
        wx.StaticText(self.infos, -1, u'e-mail:', pos = (10,190))
        self.cmail = wx.TextCtrl(self.infos, -1, pos = (10, 210), size = (300, 30))
        wx.StaticText(self.infos, -1, u'CPF:', pos = (340,190))
        self.ccpf = wx.TextCtrl(self.infos, -1, pos = (340, 210), size = (120, 30))
        self.ccpf.Bind(wx.EVT_CHAR, cpfcode)
        wx.StaticText(self.infos, -1, u'Estado:', pos = (10,250))
        if mode==1:
            self.cstate = wx.ComboBox(self.infos, -1, choices = brstates, pos = (10, 270), size = (60, 30), style = wx.CB_READONLY)
        elif mode==0:
            self.cstate = wx.TextCtrl(self.infos, -1, pos = (10, 270), size = (60, 30))
        wx.StaticText(self.infos, -1, u'Cidade:', pos = (100,250))
        self.ccity = wx.TextCtrl(self.infos, -1, pos = (100, 270), size = (150, 30))
        wx.StaticText(self.infos, -1, u'Bairro:', pos = (280,250))
        self.chood = wx.TextCtrl(self.infos, -1, pos = (280, 270), size = (150, 30))
        wx.StaticText(self.infos, -1, u'Endereço:', pos = (10,310))
        self.cadress = wx.TextCtrl(self.infos, -1, pos = (10, 330), size = (300, 30))
        wx.StaticText(self.infos, -1, u'Observações:', pos = (10,370))
        self.cobs = wx.TextCtrl(self.infos, -1, pos = (10, 390), size = (480, 100), style = wx.TE_MULTILINE)
        self.ima = wx.Panel(self.infos, -1, size = (150,150), pos = (10,25), style = wx.SIMPLE_BORDER)
        self.ima.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.ima, self.OnPaint)
        self.last = wx.Panel(self, -1, pos = (0, 500), size = (500, 50))
        if mode==1:
            self.last_ = wx.Panel(self.last, pos=(90, 5), size=(320, 40), style = wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u"Salvar", pos=(0, 0), size = (100, 40))
            finish.Bind(wx.EVT_BUTTON, self.ask1)
            restart = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u"Recomeçar", pos=(100, 0), size = (120,40))
            restart.Bind(wx.EVT_BUTTON, self.ask2)
            cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (220, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.ask3)
        elif mode==0:
            self.last_ = wx.Panel(self.last, pos=(150,5),size=(200,40), style = wx.SIMPLE_BORDER)
            edipo = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u"Editar", pos = (0, 0), size = (100,40))
            edipo.Bind(wx.EVT_BUTTON, self.turnm)
            cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (100, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.ask3)
        self.side = wx.Panel(self, -1, pos = (500, 10), size = (340, 530), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.ky = wx.TextCtrl(self.side, -1, pos = (10,10), size = (320, 100), style = wx.TE_MULTILINE|wx.NO_BORDER)
        self.ky.SetBackgroundColour('#D6D6D6')
        if mode==1:
            bp1 = wx.Panel(self.side, -1, pos = (20,120), size = (300,40), style = wx.SIMPLE_BORDER)
            sunbind = GenBitmapTextButton(bp1, -1, wx.Bitmap(current_dir + '\\data\\pics\\list-remove.png', wx.BITMAP_TYPE_PNG), u'Desconectar Venda', pos = (120, 0), size = (180, 40))
            sunbind.Bind(wx.EVT_BUTTON, self.ask4)
            ssee = GenBitmapTextButton(bp1, -1, wx.Bitmap(current_dir + '\\data\\pics\\edit_find.png', wx.BITMAP_TYPE_PNG), u'Ver Mais', pos = (0, 0), size = (120, 40))
            ssee.Bind(wx.EVT_BUTTON, self.time_eye)
        elif mode==0:
            bp1 = wx.Panel(self.side, -1, pos = (110,120), size = (120,40), style = wx.SIMPLE_BORDER)
            ssee = GenBitmapTextButton(bp1, -1, wx.Bitmap(current_dir + '\\data\\pics\\edit_find.png', wx.BITMAP_TYPE_PNG), u'Ver Mais', pos = (0, 0), size = (120, 40))
            ssee.Bind(wx.EVT_BUTTON, self.time_eye)
        self.bou = wx.ListCtrl(self.side, -1, pos=(10, 170), size = (320,350), style = wx.LC_VRULES|wx.LC_HRULES|wx.LC_REPORT|wx.SIMPLE_BORDER)
        self.bou.InsertColumn(0, u'Data/Horário', width=180)
        self.bou.InsertColumn(1, u'Valor', width=140)
        self.clean()
        if mode==0:
            self.cname.Disable()
            self.cname.SetBackgroundColour('#C6C6C6')
            self.csex.Disable()
            self.csex.SetBackgroundColour('#C6C6C6')
            self.cbirth.Disable()
            self.cbirth.SetBackgroundColour('#C6C6C6')
            self.ctel1.Disable()
            self.ctel1.SetBackgroundColour('#C6C6C6')
            self.ctel2.Disable()
            self.ctel2.SetBackgroundColour('#C6C6C6')
            self.cmail.Disable()
            self.cmail.SetBackgroundColour('#C6C6C6')
            self.ccpf.Disable()
            self.ccpf.SetBackgroundColour('#C6C6C6')
            self.cstate.Disable()
            self.cstate.SetBackgroundColour('#C6C6C6')
            self.ccity.Disable()
            self.ccity.SetBackgroundColour('#C6C6C6')
            self.chood.Disable()
            self.chood.SetBackgroundColour('#C6C6C6')
            self.cadress.Disable()
            self.cadress.SetBackgroundColour('#C6C6C6')
            self.cobs.Disable()
        self.Show()

    def ask1(self, event):
        ask(self, -1, u'Finalizar Cadastro', 3, 6)

    def ask2(self, event):
        ask(self, -1, u'Recomeçar', 1, 6)

    def ask3(self, event):
        if self.mode:
            ask(self, -1, u'Sair', 2, 6)
        elif not self.mode:
            self.Close()

    def ask4(self, event):
        ask(self, -1, u'Desconectar', 6, 6)

    def turnm(self, event):
        old_client(self.parent, -1, self.title, self.key, 1)
        self.Close()

    def time_eye(self, event):
        t = self.bou.GetFocusedItem()
        if t==-1:
            return
        tex = self.bou.GetItemText(t,0)
        j = shelve.open(current_dir + '\\clients\\'+self.key+'\\'+self.key+'_deals.txt')
        r = j[self.mar[tex]]
        j.close()
        sell(self, -1, tex, [(current_dir + '\\saves\\' +self.mar[tex][:10] + '.txt'),r['key'],r['time']], 1)

    def unbinder(self):
        t = self.bou.GetFocusedItem()
        if t==-1:
            return
        tex = self.bou.GetItemText(t,0)
        j = shelve.open(current_dir + '\\clients\\'+self.key+'\\'+self.key+'_deals.txt')
        r = j[self.mar[tex]]
        del j[self.mar[tex]]
        s = shelve.open(current_dir + '\\saves\\' +self.mar[tex][:10] + '.txt')
        v = s['sales'][r['key']]
        if v['client_id']==self.key:
            v['client_name'] = ''
            v['client_id'] = ''
            u = s['sales']
            u[r['key']] = v
            s['sales'] = u
        s.close()
        j.close()
        self.the_eye()

    def the_eye(self):
        self.bou.DeleteAllItems()
        s = shelve.open(current_dir + '\\clients\\' + self.key + '\\' + self.key + '_infos.txt')
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
        self.mar = {}
        y = shelve.open(current_dir + '\\clients\\' + self.key + '\\' +self.key + '_deals.txt')
        for o in y:
            dt = o.split('_')
            dt[1] = dt[1].replace('-', ':')
            der = dt[0].split('-')
            der.reverse()
            dt[0] = '/'.join(der)
            fdt = '   '.join(dt)
            self.mar[fdt] = o
            self.bou.Append((fdt,'R$ ' + good_show('money', y[o]['value'])))
            sn += 1
            tv += y[o]['value']
            if u'Dinheiro' == y[o]['payment']:
                mc += 1
                mv += y[o]['value']
            elif u'Cartão' == y[o]['payment']:
                cc += 1
                cv += y[o]['value']
        y.close()
        self.ky.SetValue(u'Cliente desde ' + cat + u'\nJá gastou R$ %s na Canela Santa através de %i compras, das quais %i, no valor de R$ %s, foram pagas em dinheiro e %i, no valor de R$ %s, foram pagas no cartão.' %(good_show('money', str(tv)).replace('.', ','), sn, mc, good_show('money', str(mv)).replace('.', ','), cc, good_show('money', str(cv)).replace('.', ',')))

    def clean(self):
        p = shelve.open(current_dir + '\\clients\\' + self.key + '\\' + self.key + '_infos.txt')
        self.cname.SetValue(p['name'])
        self.csex.SetValue(p['sex'])
        self.cbirth.SetValue(p['birth'])
        self.ctel1.SetValue(p['tel1'])
        self.ctel2.SetValue(p['tel2'])
        self.cmail.SetValue(p['email'])
        self.cstate.SetValue(p['state'])
        self.ccity.SetValue(p['city'])
        self.chood.SetValue(p['hood'])
        self.cadress.SetValue(p['adress'])
        self.cobs.SetValue(p['obs'])
        self.the_eye()
        p.close()

    def end(self):
        if not self.cname.GetValue():
            a = wx.MessageDialog(self, u'É necessário o nome para o cadastro', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        rtime = good_show("o", str(datetime.now().hour)) + "-" + good_show("o", str(datetime.now().minute)) + "-" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        dt = '%s_%s' %(rdate, rtime)
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/clients'):
            os.mkdir('#Trash/clients')
        if not os.path.exists('#Trash/clients/edited'):
            os.mkdir('#Trash/clients/edited')
        if not os.path.exists('#Trash/clients/edited/' + self.key):
            os.mkdir('#Trash/clients/edited/' + self.key)
        shutil.copytree('clients/' + self.key, '#Trash/clients/edited/%s/%s' %(self.key,dt))
        po = (current_dir + '\\clients\\' + self.key + '\\' + self.key + '_infos.txt')
        s = shelve.open(po)
        xname = self.cname.GetValue()
        while xname[0]==' ':
            xname = xname[1:]
        names = xname.split()
        for i in range(0,len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['name'] = namef
        s['name'] = self.cname.GetValue()
        s['sex'] = self.csex.GetValue()
        s['birth'] = self.cbirth.GetValue()
        s['email'] = self.cmail.GetValue()
        s['tel1'] = self.ctel1.GetValue()
        s['tel2'] = self.ctel2.GetValue()
        s['cpf'] = self.ccpf.GetValue()
        s['state'] = self.cstate.GetValue()
        s['city'] = self.ccity.GetValue()
        s['hood'] = self.chood.GetValue()
        s['adress'] = self.cadress.GetValue()
        s['obs'] = self.cobs.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        if type(self.GetParent()) is clients:
            self.GetParent().power_on(1)
        self.Close()

    def OnPaint(self, event):
        wx.PaintDC(self.ima).DrawBitmap(wx.Bitmap(current_dir + '\\data\\pics\\stock_person.png'), 0, 0)


class stock(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Estoque'):
        wx.Frame.__init__(self, parent,frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.SetPosition(wx.Point(100,100))
        self.SetSize(wx.Size(1200,550))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.pilot = wx.Panel(self, pos = (10, 10), size = (1180,100))
        self.butts = wx.Panel(self.pilot, pos = (75,40), size = (500,40), style = wx.SIMPLE_BORDER)
        see = GenBitmapTextButton(self.butts, -1, wx.Bitmap(current_dir + '\\data\\pics\\Tools.png', wx.BITMAP_TYPE_PNG), u'Ver Mais', pos = (0, 0), size = (100, 40))
        see.SetBackgroundColour('#D6D6D6')
        see.Bind(wx.EVT_BUTTON, self.see_entry)
        plus = GenBitmapTextButton(self.butts, -1, wx.Bitmap(current_dir + '\\data\\pics\\contact-new.png', wx.BITMAP_TYPE_PNG), u'Novo', pos = (100, 0), size = (100, 40))
        plus.SetBackgroundColour('#D6D6D6')
        plus.Bind(wx.EVT_BUTTON, self.win12)
        mplus = GenBitmapTextButton(self.butts, -1, wx.Bitmap(current_dir + '\\data\\pics\\Box_download.png', wx.BITMAP_TYPE_PNG), u'Entrada', pos = (200, 0), size = (100, 40))
        mplus.SetBackgroundColour('#D6D6D6')
        mplus.Bind(wx.EVT_BUTTON, self.win13)
        edi = GenBitmapTextButton(self.butts, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (300, 0), size = (100, 40))
        edi.SetBackgroundColour('#D6D6D6')
        edi.Bind(wx.EVT_BUTTON, self.edit_entry)
        era = GenBitmapTextButton(self.butts, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (400, 0), size = (100, 40))
        era.SetBackgroundColour('#D6D6D6')
        era.Bind(wx.EVT_BUTTON, self.ask1)
        self.seatex = wx.SearchCtrl(self.pilot, -1, pos = (650,45), size = (200,30), style = wx.TE_PROCESS_ENTER)
        self.seatex.SetDescriptiveText(u'Busca por nome')
        self.seatex.ShowCancelButton(True)
        self.seatex.SetCancelBitmap(wx.Bitmap(current_dir + '\\data\\pics\\Erase2.png', wx.BITMAP_TYPE_PNG))
        fin = wx.BitmapButton(self.pilot, -1, wx.Bitmap(current_dir + '\\data\\pics\\edit_find.png'), pos = (855, 42), size = (35, 35))
        fin.Bind(wx.EVT_BUTTON, self.searcher)
        self.seatex.Bind(wx.EVT_TEXT_ENTER, self.searcher)
        self.seatex.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.searcher)
        self.seatex.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.sclean)
        self.b2 = wx.Panel(self.pilot, pos = (900,40), size = (240,40), style = wx.SIMPLE_BORDER)
        quir = GenBitmapTextButton(self.b2, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png'), u'Sair', pos = (120, 0), size = (120, 40))
        quir.SetBackgroundColour('#D6D6D6')
        quir.Bind(wx.EVT_BUTTON, self.closer)
        rep = GenBitmapTextButton(self.b2, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png'), u'Atualizar', pos = (0, 0), size = (120, 40))
        rep.SetBackgroundColour('#D6D6D6')
        rep.Bind(wx.EVT_BUTTON, self.power_on)
        self.other = wx.Panel(self, -1, pos = (10, 110), size = (1180,410))
        self.clilist = wx.ListCtrl(self.other, -1, pos = (5, 5), size = (1170,390), style = wx.LC_VRULES|wx.LC_HRULES|wx.SIMPLE_BORDER|wx.LC_REPORT)
        self.clilist.InsertColumn(0, u'Descrição do produto', width = 400)
        self.clilist.InsertColumn(1, u'ID', width = 50)
        self.clilist.InsertColumn(2, u'Categoria', width = 150)
        self.clilist.InsertColumn(3, u'Preço', width = 200)
        self.clilist.InsertColumn(4, u'Estoque', width = 100)
        self.clilist.InsertColumn(5, u'Vendidos', width = 100)
        self.clilist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.see_entry)
        self.power_on(1)
        self.Show()

    def power_on(self, event):
        self.clilist.DeleteAllItems()
        self.seatex.Clear()
        self.praia = []
        self.mar = {}
        for root, dirs, files in os.walk('products'):
            if root != 'products':
                try:
                    o = shelve.open(current_dir + '\\' + root + '\\' +  root.split('\\')[1] + '_infos.txt')
                    self.mar[o['description']] = [str(int(root.split('\\')[1])), o['type'], 'R$ ' + good_show('money', str(o['price'])).replace('.',','), o['amount']]
                    self.praia.append(o['description'])
                    o.close()
                except:
                    pass
        self.praia.sort()
        for g in self.praia:
            self.clilist.Append((g, self.mar[g][0], self.mar[g][1], self.mar[g][2], self.mar[g][3]))

    def del_entry(self, event):
        it = self.clilist.GetFocusedItem()
        if it==-1:
            return
        e_id = self.clilist.GetItem(it, 1).GetText()
        rtime = good_show("o", str(datetime.now().hour)) + "-" + good_show("o", str(datetime.now().minute)) + "-" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        dt = '%s_%s' %(rdate, rtime)
        while len(e_id)<6:
            e_id = '0' + e_id
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/products'):
            os.mkdir('#Trash/products')
        if not os.path.exists('#Trash/products/deleted'):
            os.mkdir('#Trash/products/deleted')
        if not os.path.exists('#Trash/products/deleted/' + e_id):
            os.mkdir('#Trash/products/deleted/' + e_id)
        shutil.copytree('products/' + e_id, '#Trash/products/deleted/%s/%s' %(e_id,dt))
        dirs = os.listdir('products')
        for i in dirs:
            try:
                if int(i)==int(e_id):
                    shutil.rmtree('products/' + i)
            except:
                pass
        self.power_on(1)

    def edit_entry(self, event):
        po = self.clilist.GetFocusedItem()
        if po == -1:
            return
        lo = self.clilist.GetItem(po, 1).GetText()
        ko = self.clilist.GetItemText(po)
        old_product(self, -1, ko, lo, 1)

    def see_entry(self, event):
        po = self.clilist.GetFocusedItem()
        if po ==-1:
            return
        lo = self.clilist.GetItem(po, 1).GetText()
        ko = self.clilist.GetItemText(po)
        old_product(self, -1, ko, lo, 0)

    def searcher(self, event):
        self.clilist.DeleteAllItems()
        self.praia = []
        self.mar = {}
        for root, dirs, files in os.walk('products'):
            if root != 'products':
                try:
                    o = shelve.open(current_dir + '\\' + root + '\\' +  root.split('\\')[1] + '_infos.txt')
                    tex = lower(self.seatex.GetValue())
                    num = len(tex)
                    fri = []
                    for a in o['description'].split():
                        fri.append(lower(a[:num]))
                    fri.append(lower(o['description'][:num]))
                    for a in o['type'].split():
                        fri.append(lower(a[:num]))
                    fri.append(lower(o['type'][:num]))
                    if (tex in fri) or (tex == str(int(root.split('\\')[1]))):
                        self.mar[o['description']] = [str(int(root.split('\\')[1])), o['type'], 'R$ ' + good_show('money', str(o['price'])).replace('.',','), o['amount']]
                        self.praia.append(o['description'])
                    o.close()
                except:
                    pass
        self.praia.sort()
        for g in self.praia:
            self.clilist.Append((g, self.mar[g][0], self.mar[g][1], self.mar[g][2], self.mar[g][3]))

    def sclean(self, event):
        self.seatex.Clear()
        self.power_on(event)

    def ask1(self, event):
        ask(self, -1, u'Apagar Produto', 4, 9)

    def win12(self, event):
        new_product(self)

    def win13(self,event):
        stock_change(self)

    def closer(self, event):
        self.Close()


class new_product(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Cadastro de Produtos'):
        wx.Frame.__init__(self, parent,frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        self.SetSize(wx.Size(500, 410))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.parent = parent
        self.Centre()
        self.infos = wx.Panel(self, -1, pos=(0, 0), size = (500, 320), style = wx.TAB_TRAVERSAL)
        wx.StaticText(self.infos, -1, u'Descrição do produto:', pos=(190, 10))
        self.pdesc = wx.TextCtrl(self.infos, -1, pos=(190, 30), size=(300, 30))
        wx.StaticText(self.infos, -1, u'Preço:', pos=(190, 70))
        self.pprice = wx.TextCtrl(self.infos, -1, pos=(190, 90), size=(100, 30))
        self.pprice.Bind(wx.EVT_CHAR, check_money)
        wx.StaticText(self.infos, -1, u'Estoque:', pos=(340, 70))
        self.pamount = wx.TextCtrl(self.infos, -1, pos=(340, 90), size = (100, 30))
        wx.StaticText(self.infos, -1, u'Categoria:', pos=(190, 130))
        self.ptype = wx.ComboBox(self.infos, -1, pos=(190, 150), size = (150,30))
        wx.StaticText(self.infos, -1, u'Fornecedor:', pos = (350,130))
        self.psupplier = wx.TextCtrl(self.infos, -1, pos = (350, 150), size = (140, 30))
        wx.StaticText(self.infos, -1, u'Observações:', pos = (10,190))
        self.pobs = wx.TextCtrl(self.infos, -1, pos = (10, 210), size = (480, 100), style = wx.TE_MULTILINE)
        self.ima = wx.Panel(self.infos, -1, size = (150,150), pos = (10,25), style = wx.SIMPLE_BORDER)
        self.ima.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.ima, self.OnPaint)
        self.clean()
        self.Bind(wx.EVT_CHAR, self.bpress)
        self.last = wx.Panel(self, -1, pos = (0, 325), size = (500, 50))
        self.last_ = wx.Panel(self.last, pos=(90,5),size=(320,40), style = wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u"Finalizar",pos = (0, 0), size = (100,40))
        finish.Bind(wx.EVT_BUTTON, self.ask1)
        restart = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u"Recomeçar", pos = (100, 0), size = (120,40))
        restart.Bind(wx.EVT_BUTTON, self.ask2)
        cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (220, 0), size = (100,40))
        cancel.Bind(wx.EVT_BUTTON, self.ask3)
        self.Show()

    def bpress(self, event):
        if event.GetKeyCode()==13:
            self.end()

    def ask1(self, event):
        ask(self, -1, u'Finalizar Cadastro', 3, 8)

    def ask2(self, event):
        ask(self, -1, u'Recomeçar', 1, 8)

    def ask3(self, event):
        if self.pdesc.GetValue():
            ask(self, -1, u'Sair', 2, 8)
        else:
            self.Close()

    def clean(self):
        self.pdesc.SetValue('')
        self.pprice.SetValue('R$ 0,00')
        self.pamount.SetValue('')
        self.ptype.SetValue('')
        self.psupplier.SetValue('')
        self.pobs.SetValue('')
        if not os.path.exists('products'):
            os.mkdir('products')
        if not os.path.exists('products/category.txt'):
            f = codecs.open('products/category.txt', 'w+', 'utf-8')
        else:
            f = codecs.open('products/category.txt', 'r', 'utf-8')
        cat = f.readlines()
        l = ''.join(cat).replace('\n','').replace('\r','\r')
        cat = l.split('\\\\')
        self.ptype.SetItems(cat)
        self.ptype.Destroy()
        self.ptype = wx.ComboBox(self.infos, -1, choices = cat, pos = (190,150), size = (150,30))
        f.close()

    def end(self):
        if not self.pdesc.GetValue():
            a = wx.MessageDialog(self, u'É necessária uma descrição!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        if not os.path.exists('products'):
            os.mkdir('products')
        dirs = os.listdir('products')
        if os.path.exists('#Trash/products/deleted'):
            dirs += os.listdir('#Trash/products/deleted')
        if os.path.exists('#Trash/products/edited'):
            dirs += os.listdir('#Trash/products/edited')
        w = self.ptype.GetItems()
        for a in range(0,len(w)):
            w[a] = r_acentos(lower(w[a]))
        if r_acentos(lower(self.ptype.GetValue())) not in w:
            li = []
            if os.path.exists('products/category.txt'):
                f = codecs.open('products/category.txt', 'r', 'utf-8')
                li = f.readlines()
                f.close()
            f = codecs.open('products/category.txt', 'w', 'utf-8')
            li.append(self.ptype.GetValue().capitalize())
            li.sort()
            f.write('\\\\'.join(li))
            f.close()
        last_id = 0
        for i in dirs:
            try:
                if int(i)>last_id:
                    last_id = int(i)
            except:
                pass
        new_id = last_id + 1
        idstr = str(new_id)
        while len(idstr)<6:
            idstr = '0'+idstr
        os.mkdir('products/' + idstr)
        rtime = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        po = (current_dir + '\\products\\' + idstr + '\\' + idstr + '_infos.txt')
        s = shelve.open(po)
        names = strip(self.pdesc.GetValue()).split()
        for i in range(0,len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['description'] = namef
        s['price'] = float(self.pprice.GetValue().replace(',','.').replace('R$ ',''))
        s['amount'] = self.pamount.GetValue()
        s['type'] = self.ptype.GetValue()
        s['supplier'] = self.psupplier.GetValue()
        s['obs'] = self.pobs.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        self.clean()
        confirmation(self, -1, 'Sucesso', 5)

    def OnPaint(self, event):
        wx.PaintDC(self.ima).DrawBitmap(resize_bitmap(wx.Bitmap(current_dir + '\\data\\custom-logo\\logo-canela-santa.jpg'), self.ima.GetSizeTuple()[0], self.ima.GetSizeTuple()[1]), 0, 0)


class old_product(wx.Frame):
    def __init__(self, parent,frame_id, title, key, mode = 0):
        wx.Frame.__init__(self, parent,frame_id, title, style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        self.SetSize(wx.Size(500, 410))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        key = str(key)
        while len(key)<6:
            key = '0' + key
        self.key = key
        self.mode = mode
        self.parent = parent
        self.title = title
        self.Centre()
        self.infos = wx.Panel(self, -1, pos = (0,0), size = (500,320), style = wx.TAB_TRAVERSAL)
        wx.StaticText(self.infos, -1, u'Descrição do produto:', pos = (190,10))
        self.pdesc = wx.TextCtrl(self.infos, -1, pos = (190, 30), size = (300, 30))
        wx.StaticText(self.infos, -1, u'Preço:', pos = (190,70))
        self.pprice = wx.TextCtrl(self.infos, -1, pos = (190, 90), size = (100, 30))
        self.pprice.Bind(wx.EVT_CHAR, self.check_money)
        wx.StaticText(self.infos, -1, u'Estoque:', pos = (340,70))
        self.pamount = wx.TextCtrl(self.infos, -1, pos = (340, 90), size = (100, 30))
        wx.StaticText(self.infos, -1, u'Categoria:', pos = (190,130))
        if mode:
            self.ptype = wx.ComboBox(self.infos, -1, pos = (190,150), size = (150,30))
        else:
            self.ptype = wx.TextCtrl(self.infos, -1, pos = (190,150), size = (150,30))
            self.ptype.Disable()
        wx.StaticText(self.infos, -1, u'Fornecedor:', pos = (350,130))
        self.psupplier = wx.TextCtrl(self.infos, -1, pos = (350, 150), size = (140, 30))
        wx.StaticText(self.infos, -1, u'Observações:', pos = (10,190))
        self.pobs = wx.TextCtrl(self.infos, -1, pos = (10, 210), size = (480, 100), style = wx.TE_MULTILINE)
        self.ima = wx.Panel(self.infos, -1, size = (150,150), pos = (10,25), style = wx.SIMPLE_BORDER)
        self.ima.SetBackgroundColour('#ffffff')
        wx.EVT_PAINT(self.ima, self.OnPaint)
        self.Bind(wx.EVT_CHAR, self.bpress)
        self.last = wx.Panel(self, -1, pos = (0, 325), size = (500, 50))
        if mode == 0:
            self.last_ = wx.Panel(self.last, pos=(150,5),size=(200,40), style = wx.SIMPLE_BORDER)
            edipo = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u"Editar", pos = (0, 0), size = (100,40))
            edipo.Bind(wx.EVT_BUTTON, self.turnm)
            cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (100, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.ask3)
            self.ptype.SetBackgroundColour('#C6C6C6')
            self.pdesc.Disable()
            self.pdesc.SetBackgroundColour('#C6C6C6')
            self.pprice.Disable()
            self.pprice.SetBackgroundColour('#C6C6C6')
            self.pamount.Disable()
            self.pamount.SetBackgroundColour('#C6C6C6')
            self.psupplier.Disable()
            self.psupplier.SetBackgroundColour('#C6C6C6')
            self.pobs.Disable()
        elif mode == 1:
            self.last_ = wx.Panel(self.last, pos=(90,5),size=(320,40), style = wx.SIMPLE_BORDER)
            finish = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u"Finalizar",pos = (0, 0), size = (100,40))
            finish.Bind(wx.EVT_BUTTON, self.ask1)
            restart = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u"Recomeçar", pos = (100, 0), size = (120,40))
            restart.Bind(wx.EVT_BUTTON, self.ask2)
            cancel = GenBitmapTextButton(self.last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"Sair",pos = (220, 0), size = (100,40))
            cancel.Bind(wx.EVT_BUTTON, self.ask3)
        self.clean()

        self.Show()

    def bpress(self, event):
        if event.GetKeyCode()==13:
            self.end()

    def ask1(self, event):
        ask(self, -1, u'Finalizar Cadastro', 3, 8)

    def ask2(self, event):
        ask(self, -1, u'Recomeçar', 1, 8)

    def ask3(self, event):
        if self.mode==1:
            ask(self, -1, u'Sair', 2, 8)
        elif self.mode==0:
            self.Close()

    def check_money(self, event):
        num = [48,49,50,51,52,53,54,55,56,57]
        dex = [8,127,314,316, 9]
        pro = event.GetKeyCode()
        box = self.pprice
        rhyme = box.GetValue().replace(",", ".")[3:]
        try:
            if pro == dex[2] or pro == dex[3] or pro == dex[4]:
                event.Skip()
            elif pro == dex[0] or pro == dex[1]:
                wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
                box.SetValue('R$ ' + good_show("money", str(wer).replace(".", ",")))
            elif pro in num:
                if len(box.GetValue())==14:
                    box.SetValue('R$ 0,00')
                    return
                wes = float(rhyme)*10 + float(chr(pro))/100
                box.SetValue('R$ ' + good_show("money", str(wes).replace(".", ",")))
        except:
            box.SetValue("R$ 0,00")

    def clean(self):
        s = shelve.open(current_dir + '\\products\\' + self.key + '\\' + self.key + '_infos.txt')
        self.pdesc.SetValue(s['description'])
        self.pprice.SetValue('R$ ' + good_show('money', str(s['price'])).replace('.',','))
        self.pamount.SetValue(str(s['amount']))
        self.psupplier.SetValue(s['supplier'])
        self.pobs.SetValue(s['obs'])
        if self.mode==1:
            if not os.path.exists('products'):
                os.mkdir('products')
            if not os.path.exists('products/category.txt'):
                f = codecs.open('products/category.txt', 'w+', 'utf-8')
            else:
                f = codecs.open('products/category.txt', 'r', 'utf-8')
            cat = f.readlines()
            l = ''.join(cat).replace('\n','').replace('\r','\r')
            cat = l.split('\\\\')
            self.ptype.SetItems(cat)
            f.close()
        self.ptype.SetValue(s['type'])

    def turnm(self, event):
        old_product(self.parent, -1, self.title, self.key, 1)
        self.Close()

    def end(self):
        if not self.pdesc.GetValue():
            a = wx.MessageDialog(self, u'É necessária uma descrição!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        idstr = self.key
        rtime = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        dt = '%s_%s' %(rdate, rtime.replace(':','-'))
        if not os.path.exists('#Trash'):
            os.mkdir('#Trash')
        if not os.path.exists('#Trash/products'):
            os.mkdir('#Trash/products')
        if not os.path.exists('#Trash/products/edited'):
            os.mkdir('#Trash/products/edited')
        if not os.path.exists('#Trash/products/edited/' + idstr):
            os.mkdir('#Trash/products/edited/' + idstr)
        w = self.ptype.GetItems()
        for a in range(0,len(w)):
            w[a] = r_acentos(lower(w[a]))
        if r_acentos(lower(self.ptype.GetValue())) not in w:
            li = []
            if os.path.exists('products/category.txt'):
                f = codecs.open('products/category.txt', 'r', 'utf-8')
                li = f.readlines()
                f.close()
            f = codecs.open('products/category.txt', 'w', 'utf-8')
            li.append(self.ptype.GetValue().capitalize())
            li.sort()
            f.write('\\\\'.join(li))
            f.close()
        shutil.copytree('products/' + idstr, '#Trash/products/edited/%s/%s' %(idstr, dt))
        po = (current_dir + '\\products\\' + idstr + '\\' + idstr + '_infos.txt')
        s = shelve.open(po)
        names = strip(self.pdesc.GetValue()).split()
        for i in range(0,len(names)):
            names[i] = names[i].capitalize()
        namef = ' '.join(names)
        s['description'] = namef
        s['price'] = float(self.pprice.GetValue().replace(',','.').replace('R$ ',''))
        s['amount'] = self.pamount.GetValue()
        s['type'] = self.ptype.GetValue()
        s['supplier'] = self.psupplier.GetValue()
        s['obs'] = self.pobs.GetValue()
        s['time'] = rtime
        s['date'] = rdate
        s.close()
        self.clean()
        if type(self.parent) is stock:
            self.parent.power_on(1)
        self.Close()

    def OnPaint(self, event):
        wx.PaintDC(self.ima).DrawBitmap(resize_bitmap(wx.Bitmap(current_dir + '\\data\\custom-logo\\logo-canela-santa.jpg'), self.ima.GetSizeTuple()[0], self.ima.GetSizeTuple()[1]), 0, 0)


class stock_change(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Entrada de Produtos'):
        wx.Frame.__init__(self,parent,frame_id, title, size = (850,650),style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL)
        self.Centre()
        self.parent = parent
        self.SetIcon(general_icon)
        self.fill()
        bottom = wx.Panel(self,-1,size=(390,50),pos=(230,560),style=wx.SIMPLE_BORDER)
        add = GenBitmapTextButton(bottom,-1,wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Registrar produtos', size = (150,50),pos=(0,0))
        reset = GenBitmapTextButton(bottom,-1,wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Recomeçar', size = (120,50),pos=(150,0))
        cancel = GenBitmapTextButton(bottom,-1,wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u'Sair', size = (120,50),pos=(270,0))
        add.Bind(wx.EVT_BUTTON, self.add)
        reset.Bind(wx.EVT_BUTTON, self.clean)
        cancel.Bind(wx.EVT_BUTTON, self.cancel)
        self.SetBackgroundColour('#D6D6D6')
        self.Show()

    def fill(self):
        self.new = []
        for i in range(10):
            if i >= 5:
                x = 435
                y = (i-5)*110 + 10
            else:
                x = 15
                y = i*110 + 10
            panel = wx.Panel(self, -1, size=(400, 100), pos=(x, y), style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
            pnm = wx.TextCtrl(panel, -1, size=(300, 30), pos=(95, 5))
            pam = wx.TextCtrl(panel, -1, size=(100, 30), pos=(95, 60))
            pct = wx.TextCtrl(panel, -1, size=(100, 30), pos=(285, 60))
            pam.Bind(wx.EVT_CHAR, self.check_num)
            pct.Bind(wx.EVT_CHAR, check_money)
            pct.SetValue('R$ 0,00')
            self.new.append([pnm,pam,pct])
            panel.SetBackgroundColour('#D6D6D6')
            a = wx.StaticText(panel, -1, u'Descrição:', pos = (21,12))
            b = wx.StaticText(panel, -1, u'Quantidade:', pos = (25,67))
            c = wx.StaticText(panel, -1, u'Preço:', pos = (240,67))

    def add(self,event):
        prods = []
        for i in self.new:
            a=i[0].GetValue()
            b=i[1].GetValue()
            if a and b:
                b=int(b)
                d=i[2].GetValue()
                c=float(d.replace('R$ ','').replace(',','.'))
                if a and b and c:
                    prods.append([a,b,c,d])
        if not prods:
            a = wx.MessageDialog(self, u'Nenhum produto adicionado!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        if not os.path.exists('products'):
            os.mkdir('products')
        dirs = os.listdir('products')
        if os.path.exists('#Trash/products/deleted'):
            dirs += os.listdir('#Trash/products/deleted')
        if os.path.exists('#Trash/products/edited'):
            dirs += os.listdir('#Trash/products/edited')
        last_id = 0
        for i in dirs:
            try:
                if int(i)>last_id:
                    last_id = int(i)
            except:
                pass
        if type(self.parent) is not stock:
            self.mar = {}
            for root, dirs, files in os.walk('products'):
                if root != 'products':
                    try:
                        o = shelve.open(current_dir + '\\' + root + '\\' +  root.split('\\')[1] + '_infos.txt')
                        self.mar[o['description']] = [str(int(root.split('\\')[1])), o['type'], 'R$ ' + good_show('money', str(o['price'])).replace('.',','), o['amount']]
                        o.close()
                    except:
                        pass
        else:
            self.mar = self.parent.mar
        for k in prods:
            names = strip(k[0]).split()
            for i in range(0,len(names)):
                names[i] = names[i].capitalize()
            namef = ' '.join(names)
            if namef not in self.mar:
                new_id = last_id + 1
                idstr = str(new_id)
                while len(idstr)<6:
                    idstr = '0'+idstr
                os.mkdir('products/' + idstr)
                rtime = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
                rdate = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
                po = (current_dir + '\\products\\' + idstr + '\\' + idstr + '_infos.txt')
                s = shelve.open(po)
                s['description'] = namef
                s['price'] = k[2]
                s['amount'] = k[1]
                s['type'] = ''
                s['supplier'] = ''
                s['obs'] = ''
                s['time'] = rtime
                s['date'] = rdate
                s.close()
                last_id=new_id
                self.mar[namef] = [new_id, '', k[3], k[2]]
            else:
                if self.mar[namef][2]==k[3]:
                    idstr = str(self.mar[namef][0])
                    while len(idstr)<6:
                        idstr = '0'+idstr
                    po = (current_dir + '\\products\\' + idstr + '\\' + idstr + '_infos.txt')
                    s = shelve.open(po)
                    s['amount'] +=k[1]
                    s.close()
        confirmation(self, -1, u'Sucesso', 6)
        self.clean(1)

    def clean(self,event):
        for a in self.new:
            for b in a:
                b.Clear()

    def check_num(self,event):
        try:
            box = event.GetEventObject()
            text = box.GetValue()
            if len(text) and text!='-':
                int(box.GetValue())
            num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
            pre = [8, 9, 127, 314, 316]
            pro = event.GetKeyCode()
            if pro in pre:
                event.Skip()
            elif pro in num:
                if len(text):
                    if not (text[0] == '-' and not box.GetInsertionPoint()):
                        event.Skip()
                else:
                    event.Skip()
            elif pro==45:
                if (not text[0] == '-' and not box.GetInsertionPoint()):
                    event.Skip()
        except:
            event.GetEventObject().SetValue('')

    def cancel(self,event):
        self.Close()


class expenses(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Gastos', mode=None, kind=1, month=''):
        if not mode:
            mode = []
        wx.Frame.__init__(self, parent,frame_id, title, size = (500,200),style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.Centre()
        self.SetIcon(general_icon)
        self.mode = mode
        self.kind = kind
        self.month = month
        self.SetBackgroundColour('#D6D6D6')
        #first
        first = wx.Panel(self, -1, size = (480, 85), pos = (10,10), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        first.SetBackgroundColour('#D6D6D6')
        wx.StaticText(first, -1, u"Descrição:", pos = (10,5))
        self.tex1 = wx.TextCtrl(first, -1, pos = (10,25), size = (300,30))
        self.tex1.Bind(wx.EVT_CHAR, self.all)
        wx.StaticText(first, -1, u"Valor:" , pos = (370,5))
        wx.StaticText(first, -1, u"R$", pos = (355,32))
        self.tex2 = wx.TextCtrl(first, -1, pos = (370,25), size = (80,30))
        self.tex2.Bind(wx.EVT_CHAR, self.check_money)
        self.tex2.SetValue("0,00")
        if mode:
            self.planet = shelve.open(self.mode[0])
            if kind==1:
                self.tex1.SetValue(self.planet["spent"][mode[1]]['description'])
                self.tex2.SetValue(good_show("money", str(self.planet["spent"][mode[1]]['value'])).replace(".",","))
            elif kind==2:
                self.tex1.SetValue(self.planet["spent"][mode[1]]['description'])
                self.tex2.SetValue(good_show("money", str(self.planet["spent"][mode[1]]['value'])).replace(".",","))
            elif kind==3:
                self.tex1.SetValue(self.planet["winning"][mode[1]]['description'])
                self.tex2.SetValue(good_show("money", str(self.planet["winning"][mode[1]]['value'])).replace(".",","))
            self.planet.close()

        #last
        last = wx.Panel(self, -1, size = (480, 60), pos = (10,105), style = wx.SUNKEN_BORDER)
        last.SetBackgroundColour('#D6D6D6')
        last_ = wx.Panel(last, pos=(80,10),size=(320,40), style = wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u'Finalizar', pos = (0, 0), size = (100,40))
        finish.Bind(wx.EVT_BUTTON, self.ask3)
        restart = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Recomeçar', pos = (100, 0), size = (120,40))
        restart.Bind(wx.EVT_BUTTON, self.ask1)
        cancel = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"sair",pos = (220, 0), size = (100,40))
        cancel.Bind(wx.EVT_BUTTON, self.ask2)

        self.Show()

    def ask1(self, event):
        ask(self, -1, u"Apagar Tudo", 1, 2)

    def ask2(self, event):
        pl = str(self.tex1.GetValue())
        po = str(self.tex2.GetValue())
        if pl=='' and po=='0,00':
            self.Close()
            return
        ask(self, -1, u"Sair", 2, 2)

    def ask3(self, event):
        if self.kind in (1,2):
            ask(self, -1, u"Registrar Gasto", 3, 2)
        elif self.kind==3:
            ask(self, -1, u"Registrar Ganho", 3, 11)

    def check_money(self, event):
        num = [48,49,50,51,52,53,54,55,56,57]
        dex = [8,127,314,316, 9]
        pro = event.GetKeyCode()
        rhyme = self.tex2.GetValue().replace(",", ".")
        try:
            if pro == dex[2] or pro == dex[3] or pro == dex[4]:
                event.Skip()
            elif pro == dex[0] or pro == dex[1]:
                wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
                self.tex2.SetValue(good_show("money", str(wer).replace(".", ",")))
            elif pro in num:
                if len(self.tex2.GetValue())==14:
                    self.tex2.SetValue('0,00')
                    return
                wes = float(rhyme)*10 + float(chr(pro))/100
                self.tex2.SetValue(good_show("money", str(wes).replace(".", ",")))
            self.enter(event)
        except:
            self.tex2.SetValue("0,00")

    def enter(self, event):
        pro = event.GetKeyCode()
        if pro==13:
            self.ask3(event)

    def all(self,event):
        if event.GetKeyCode()==13:
            self.enter(event)
        else:
            event.Skip()

    def clean(self):
        self.tex1.Clear()
        self.tex2.Clear()
        self.tex2.SetValue("0,00")

    def end(self):
        descri = self.tex1.GetValue().capitalize()
        val = float(self.tex2.GetValue().replace(",", "."))
        if len(descri) == 0 or val == 0:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style=wx.OK | wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        if self.kind == 1:
            if not self.mode:
                self.info = current_dir + "\\saves\\" + date + ".txt"
                self.day_sell = shelve.open(self.info)
                if "sales" not in self.day_sell:
                    self.day_sell["sales"] = {}
                    self.day_sell["secount"] = 0
                    self.day_sell["edit"] = {}
                    self.day_sell["spent"] = {}
                    self.day_sell["spcount"] = 0
                    self.day_sell["closure"] = []
                    self.day_sell["wastes"] = {}
                    self.day_sell["wcount"] = 0
                key = self.day_sell["spcount"] + 1
                asw = self.day_sell["spent"]
                asw[key] = {'time':self.finish_time,
                            'edit':0,
                            'description':descri,
                            'value':val}
                self.day_sell["spent"] = asw
                self.day_sell["spcount"] = key
            else:
                self.day_sell = shelve.open(self.mode[0])
                key = self.mode[1]
                hour = self.mode[2]
                asw = self.day_sell["edit"]
                asw[self.finish_time] = self.day_sell["spent"][key]
                asw[self.finish_time]['key'] = key
                asw[self.finish_time]['mode'] = 1
                self.day_sell["edit"] = asw
                adw = self.day_sell["spent"]
                adw[key] = {'time':hour,
                            'edit':1,
                            'description':descri,
                            'value':val}
                self.day_sell["spent"] = adw
            self.clean()
            self.day_sell.close()
            if not self.mode:
                confirmation(self, -1, u"Sucesso", 2)
            else:
                self.GetParent().run()
                self.Close()
        elif self.kind == 2:
            cp = self.GetParent()
            if not self.mode:
                inf = current_dir + '\\saves\\' + self.month + '.txt'
                pao = shelve.open(inf)
                if 'spent' not in pao:
                    pao['spent'] = {}
                    pao['spcount'] = 0
                    pao['winning'] = {}
                    pao['wicount'] = 0
                    pao['edit'] = {}
                key = 1 + pao['spcount']
                aw = pao['spent']
                aw[key] = {'time':self.finish_time,
                           'date':date,
                           'edit':0,
                           'description':descri,
                           'value':val}
                pao['spent'] = aw
                pao['spcount'] = key
                pao.close()
            else:
                pao = shelve.open(self.mode[0])
                key = self.mode[1]
                hour = self.mode[2]
                asw = pao["edit"]
                asw[self.finish_time] = pao["spent"][key]
                asw[self.finish_time]['key'] = key
                asw[self.finish_time]['mode'] = 1
                pao["edit"] = asw
                adw = pao["spent"]
                adw[key] = {'time': hour,
                            'date': adw[key]['date'],
                            'edit': 1,
                            'description': descri,
                            'value': val}
                pao["spent"] = adw
                pao.close()
            self.clean()
            if not self.mode:
                confirmation(self, -1, u"Sucesso", 7)
            else:
                self.GetParent().fill_32(1)
                self.Close()
        elif self.kind == 3:
            if not self.mode:
                inf = current_dir + '\\saves\\' + self.month + '.txt'
                pao = shelve.open(inf)
                if 'spent' not in pao:
                    pao['spent'] = {}
                    pao['spcount'] = 0
                    pao['winning'] = {}
                    pao['wicount'] = 0
                    pao['edit'] = {}
                key = 1 + pao['wicount']
                aw = pao['winning']
                aw[key] = {'time': self.finish_time,
                           'date': date,
                           'edit': 0,
                           'description': descri,
                           'value': val}
                pao['winning'] = aw
                pao['wicount'] = key
                pao.close()
            else:
                pao = shelve.open(self.mode[0])
                key = self.mode[1]
                hour = self.mode[2]
                asw = pao["edit"]
                asw[self.finish_time] = pao["winning"][key]
                asw[self.finish_time]['key'] = key
                asw[self.finish_time]['mode'] = 1
                pao["edit"] = asw
                adw = pao["winning"]
                adw[key] = {'time': hour,
                            'date': adw[key]['date'],
                            'edit': 1,
                            'description': descri,
                            'value': val}
                pao["winning"] = adw
                pao.close()
            self.clean()
            if not self.mode:
                confirmation(self, -1, u"Sucesso", 7)
            else:
                self.GetParent().fill_31(1)
                self.Close()


class report(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Fechamento de Caixa'):
        wx.Frame.__init__(self, parent,frame_id, title, style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetPosition(wx.Point(75, 0))
        self.SetSize(wx.Size(1240, 720))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        #first
        self.first = wx.Panel(self, -1, pos=(10,5), size=(1220, 50), style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.first.SetBackgroundColour('#D6D6D6')
        wx.StaticText(self.first, -1, u"Fechamento de:", pos=(500, 15))
        self.starter()
        fupdate = GenBitmapTextButton(self.first, -1,wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Atualizar janela' ,pos = (750, 5), size = (140,40))
        fupdate.Bind(wx.EVT_BUTTON, self.row)
        pol = wx.Button(self.first, -1, u"Recuperação de registros", pos=(900,5), size=(-1,40))
        pol.Bind(wx.EVT_BUTTON, self.win6)
        #panel1
        self.panel1 = wx.Panel(self, -1, pos = (10,65), size = (810, 260), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.panel1.SetBackgroundColour('#D6D6D6')
        self.prods = wx.gizmos.TreeListCtrl(self.panel1, -1, pos = (10, 5), size = (620, 250), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.prods.AddColumn(u"Descrição", width = 250)
        self.prods.AddColumn(u"Quantidade")
        self.prods.AddColumn(u"Pagamento", width = 150)
        self.prods.AddColumn(u"Valor", width = 120)
        self.prods.SetMainColumn(0)
        self.panel1b = wx.Panel(self.panel1, pos = (650,50), size = (145,160), style = wx.SIMPLE_BORDER)
        plus = GenBitmapTextButton(self.panel1b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u"Nova venda", pos = (0, 0), size = (145,40))
        plus.Bind(wx.EVT_BUTTON, self.win2)
        edit = GenBitmapTextButton(self.panel1b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u"Editar venda", pos = (0, 40), size = (145,40))
        edit.Bind(wx.EVT_BUTTON, self.win2_)
        remove = GenBitmapTextButton(self.panel1b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar venda', pos = (0, 80), size = (145,40))
        remove.Bind(wx.EVT_BUTTON, self.remove1)
        update = GenBitmapTextButton(self.panel1b, -1,wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Atualizar', pos = (0, 120), size = (145,40))
        update.Bind(wx.EVT_BUTTON, self.pre_run)
        #panel2
        self.panel2 = wx.Panel(self, 53, pos = (10,335), size = (810, 170), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.panel2.SetBackgroundColour('#D6D6D6')
        self.expent = wx.gizmos.TreeListCtrl(self.panel2, -1, pos = (10,5), size = (620, 160), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.expent.AddColumn(u"Data/Horário", width = 130)
        self.expent.AddColumn(u"Descrição", width = 280)
        self.expent.AddColumn(u"Quantidade", width = 100)
        self.expent.AddColumn(u"Valor", width = 110)
        self.expent.SetMainColumn(0)
        self.panel2b = wx.Panel(self.panel2, pos = (650,5), size = (145,160), style = wx.SIMPLE_BORDER)
        splus = GenBitmapTextButton(self.panel2b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Adicionar gasto',pos = (0, 0), size = (145,40))
        splus.Bind(wx.EVT_BUTTON, self.win4)
        sedit = GenBitmapTextButton(self.panel2b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar gasto',pos = (0, 40), size = (145,40))
        sedit.Bind(wx.EVT_BUTTON, self.win4_)
        sremove = GenBitmapTextButton(self.panel2b, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar gasto',pos = (0, 80), size = (145,40))
        sremove.Bind(wx.EVT_BUTTON, self.remove2)
        supdate = GenBitmapTextButton(self.panel2b, -1,wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG),u'Atualizar', pos = (0, 120), size = (145,40))
        supdate.Bind(wx.EVT_BUTTON, self.pre_run)
        #panel3
        self.panel3 = wx.Panel(self, 54, pos = (830, 65), size = (400, 620), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.panel3.SetBackgroundColour('#D6D6D6')
        self.a1 = wx.StaticText(self.panel3, -1 , u"Total do dia", pos = (10,17))
        self.delta = wx.TextCtrl(self.panel3, -1, "0,00", pos = (315, 10), size = (70,30), style = wx.TE_READONLY)
        self.delta.SetBackgroundColour("#C0C0C0")
        part1 = wx.Panel(self.panel3, -1, pos = (5,50), size = (390, 265), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.a2 = wx.StaticText(part1, -1 , u"Total das Vendas", pos = (5,12))
        self.echo = wx.TextCtrl(part1, -1, "0,00", pos = (310, 5), size = (70,30), style = wx.TE_READONLY)
        self.echo.SetBackgroundColour("#C0C0C0")
        self.a3 = wx.StaticText(part1, -1 , u"Quantidade de vendas", pos = (5,57))
        self.hotel = wx.TextCtrl(part1, -1, "0", pos = (310, 50), size = (70,30), style = wx.TE_READONLY)
        self.hotel.SetBackgroundColour("#C0C0C0")
        self.a4 = wx.StaticText(part1, -1 , u"Total das vendas em dinheiro", pos = (5,102))
        self.india = wx.TextCtrl(part1, -1, "0,00", pos = (310, 95), size = (70,30), style = wx.TE_READONLY)
        self.india.SetBackgroundColour("#C0C0C0")
        self.a5 = wx.StaticText(part1, -1 , u"Quantidade de vendas em dinheiro", pos = (5,147))
        self.juliet = wx.TextCtrl(part1, -1, "0", pos = (310, 140), size = (70,30), style = wx.TE_READONLY)
        self.juliet.SetBackgroundColour("#C0C0C0")
        self.a6 = wx.StaticText(part1, -1 , u"Total das vendas no cartão", pos = (5,192))
        self.lima = wx.TextCtrl(part1, -1, "0,00", pos = (310, 185), size = (70,30), style = wx.TE_READONLY)
        self.lima.SetBackgroundColour("#C0C0C0")
        self.a7 = wx.StaticText(part1, -1 , u"Quantidade de vendas no cartão", pos = (5,237))
        self.oscar = wx.TextCtrl(part1, -1, "0", pos = (310, 230), size = (70,30), style = wx.TE_READONLY)
        self.oscar.SetBackgroundColour("#C0C0C0")
        part2 = wx.Panel(self.panel3, -1, pos = (5,320), size = (390,85), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.a8 = wx.StaticText(part2, -1 , u"Total de gastos", pos = (5,12))
        self.quilo = wx.TextCtrl(part2, -1, "0,00", pos = (310, 5), size = (70,30), style = wx.TE_READONLY)
        self.quilo.SetBackgroundColour("#C0C0C0")
        self.a9 = wx.StaticText(part2, -1 , u"Quantidade de gastos", pos = (5,57))
        self.tango = wx.TextCtrl(part2, -1, "0", pos = (310, 50), size = (70,30), style = wx.TE_READONLY)
        self.tango.SetBackgroundColour("#C0C0C0")
        part3 = wx.Panel(self.panel3, -1, pos = (5,410), size = (390,200), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.a10 = wx.StaticText(part3, -1 , u"Caixa do dia anterior", pos = (5,12))
        self.uniforme = wx.TextCtrl(part3, -1, "0,00", pos = (310, 5), size = (70,30))
        self.uniforme.Bind(wx.EVT_CHAR, self.box0)
        self.a11 = wx.StaticText(part3, -1 , u"Caixa ideal", pos = (5,52))
        self.wilson = wx.TextCtrl(part3, -1, "0,00", pos = (310, 45), size = (70,30), style = wx.TE_READONLY)
        self.wilson.SetBackgroundColour("#C0C0C0")
        self.a12 = wx.StaticText(part3, -1 , u"Caixa real", pos = (5,92))
        self.xray = wx.TextCtrl(part3, -1, "0,00", pos = (310, 85), size = (70,30))
        self.xray.Bind(wx.EVT_CHAR, self.box1)
        self.a13 = wx.StaticText(part3, -1 , u"Caixa de amanhã", pos = (5,132))
        self.zebra = wx.TextCtrl(part3, -1, "0,00", pos = (310, 125), size = (70,30), style = wx.TE_READONLY)
        self.zebra.SetBackgroundColour("#C0C0C0")
        self.a14 = wx.StaticText(part3, -1 , u"Dinheiro retirado", pos = (5,172))
        self.qwerty = wx.TextCtrl(part3, -1, "0,00", pos = (310, 165), size = (70,30))
        self.qwerty.Bind(wx.EVT_CHAR, self.box2)
        #last
        self.last = wx.Panel(self, 56, pos = (10,515), size = (810, 170), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.last.SetBackgroundColour('#D6D6D6')
        self.was = wx.gizmos.TreeListCtrl(self.last, -1, pos = (10,5), size = (620, 160), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.was.AddColumn(u"Descrição", width = 280)
        self.was.AddColumn(u"Quantidade", width = 100)
        self.was.AddColumn(u"Valor", width = 110)
        self.was.SetMainColumn(0)
        self.lastb = wx.Panel(self.last, pos = (650,5), size = (145,160), style = wx.SIMPLE_BORDER)
        wplus = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Adicionar registro',pos = (0, 0), size = (145,40))
        wplus.Bind(wx.EVT_BUTTON, self.win7)
        wedit = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar registro',pos = (0, 40), size = (145,40))
        wedit.Bind(wx.EVT_BUTTON, self.win7_)
        wremove = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar registro',pos = (0, 80), size = (145,40))
        wremove.Bind(wx.EVT_BUTTON, self.remove3)
        wupdate = GenBitmapTextButton(self.lastb, -1,wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG),'Atualizar', pos = (0, 120), size = (145,40))
        wupdate.Bind(wx.EVT_BUTTON, self.pre_run, wupdate)

        self.run()
        self.Show()

    def box0(self,event):
        self.check_money(self.uniforme, event)

    def box1(self,event):
        self.check_money(self.xray, event)

    def box2(self,event):
        self.check_money(self.qwerty, event)

    def remove1(self,event):
        boom = self.prods.GetSelection()
        if boom == self.prods.GetRootItem():
            return
        ask(self, -1, u"Apagar Venda", 4, 3)

    def remove2(self,event):
        boom = self.expent.GetSelection()
        if boom == self.expent.GetRootItem():
            return
        ask(self, -1, u"Apagar Gasto", 4, 3.5)

    def remove3(self,event):
        boom = self.was.GetSelection()
        if boom == self.was.GetRootItem():
            return
        ask(self, -1, u"Apagar Registro", 4, 5)

    def remover(self, box):
        boom = box.GetSelection()
        atom = box.GetItemText(boom, 0)
        if boom == box.GetRootItem():
            return
        if len(str(atom))!=8 and box==self.prods:
            boom = box.GetItemParent(boom)
            atom = box.GetItemText(boom, 0)
        self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
        if box==self.prods:
            for i in self.bravo["sales"]:
                if self.bravo["sales"][i]['time'] == atom:
                    ckey = self.bravo['sales'][i]['client_id']
                    if ckey in os.listdir('clients'):
                        try:
                            h = shelve.open(current_dir + '\\clients\\' + ckey + '\\' + ckey + '_deals.txt')
                            r =  str(self.nig[:10] + '_' + self.bravo['sales'][i]['time'].replace(':','-'))
                            del h[r]
                            h.close()
                        except:
                            pass
                    self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
                    asw = self.bravo["edit"]
                    asw[self.finish_time] = self.bravo["sales"][i]
                    asw[self.finish_time]['key'] = i
                    asw[self.finish_time]['mode'] = 2
                    self.bravo["edit"] = asw
                    hair = self.bravo["sales"]
                    del hair[i]
                    self.bravo["sales"]=hair
                    self.bravo.close()
                    self.run()
                    return
        elif box==self.expent:
            for i in self.bravo["spent"]:
                if self.bravo["spent"][i]['time'] == atom:
                    self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
                    asw = self.bravo["edit"]
                    asw[self.finish_time] = self.bravo["spent"][i]
                    asw[self.finish_time]['key'] = i
                    asw[self.finish_time]['mode'] = 2
                    self.bravo["edit"] = asw
                    hair = self.bravo["spent"]
                    del hair[i]
                    self.bravo["spent"]=hair
                    self.bravo.close()
                    self.run()
                    return
        elif box==self.was:
            for i in self.bravo["wastes"]:
                neutron = int(box.GetItemText(boom, 1))
                proton = float(box.GetItemText(boom, 2).replace('R$ ', '').replace(',','.'))
                if r_acentos(self.bravo["wastes"][i]['description']) == atom and self.bravo["wastes"][i]['amount']==neutron and self.bravo["wastes"][i]['value']==proton:
                    self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
                    asw = self.bravo["edit"]
                    asw[self.finish_time] = self.bravo["wastes"][i]
                    asw[self.finish_time]['key'] = i
                    asw[self.finish_time]['mode'] = 2
                    self.bravo["edit"] = asw
                    hair = self.bravo["wastes"]
                    del hair[i]
                    self.bravo["wastes"]=hair
                    self.bravo.close()
                    self.run()
                    return

    def check_money(self, box, event):
        num = [48,49,50,51,52,53,54,55,56,57]
        dex = [8,127,314,316, 9]
        pro = event.GetKeyCode()
        rhyme = box.GetValue().replace(",", ".")
        try:
            if pro == dex[2] or pro == dex[3] or pro == dex[4]:
                event.Skip()
            elif pro == dex[0] or pro == dex[1]:
                wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
                box.SetValue(good_show("money", str(wer).replace(".", ",")))
                if box==self.uniforme:
                    tyde = wer + float(self.india.GetValue().replace(",", "."))
                    self.wilson.SetValue(good_show("money", str(tyde).replace(".",",")))
                if (box==self.xray or box==self.uniforme) and self.xray.GetValue()!="0,00":
                    tide = wer - float(self.wilson.GetValue().replace(",","."))
                    self.zebra.SetValue(good_show("money", str(tide).replace(".", ",")))
            elif pro in num:
                if len(box.GetValue())==14:
                    box.SetValue('0,00')
                    return
                wes = float(rhyme)*10 + float(chr(pro))/100
                box.SetValue(good_show("money", str(wes).replace(".", ",")))
                if box==self.uniforme:
                    tyde = wes + float(self.india.GetValue().replace(",", "."))
                    self.wilson.SetValue(good_show("money", str(tyde).replace(".",",")))
                if box==self.xray or box==self.uniforme:
                    rter = float(self.wilson.GetValue().replace(",","."))
                    tide = float(wes) - rter
                    self.zebra.SetValue(good_show("money", str(tide).replace(".", ",")))
            if self.xray.GetValue()=="0,00":
                tide = float(self.wilson.GetValue().replace(",", ".")) - float(self.qwerty.GetValue().replace(",","."))
            else:
                tide = float(self.xray.GetValue().replace(",", ".")) - float(self.qwerty.GetValue().replace(",","."))
            if tide<0:
                tide = 0.0
            self.zebra.SetValue(good_show("money", str(tide).replace(".", ",")))
            self.saver()
        except:
            box.SetValue("0,00")
            self.saver()

    def starter(self):
        self.foxfrot = []
        self.charlie = []
        for root, dirs, files in os.walk("saves"):
            if root != "saves":
                break
            files.sort()
            files.reverse()
            for i in files:
                try:
                    if len(str(int(i.replace("-",'').replace(".txt", ""))))==8:
                        ab = i[8:10]
                        ab = ab + "/" + i[5:7]
                        ab = ab + "/" + i[0:4]
                        self.foxfrot.append(ab)
                        self.charlie.append(i)
                except:
                    pass
        self.alfa = wx.ComboBox(self.first, -1, choices = self.foxfrot, size = (130,-1), pos = (600, 10), style = wx.CB_READONLY)
        self.alfa.Bind(wx.EVT_COMBOBOX, self.pre_run)
        if len(self.foxfrot)!=0:
            self.alfa.SetValue(self.foxfrot[0])

    def pre_run(self, event):
        self.run()

    def run(self):
        if self.alfa.GetValue() != u'':
            self.clean()
            self.nig = self.charlie[self.foxfrot.index(self.alfa.GetValue())]
            self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
            root = self.prods.AddRoot("Vendas de " + self.alfa.GetValue())
            self.prods.SetItemFont(root, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.sale_total = 0.0
            self.sale_num = 0
            self.money_total = 0.00
            self.money_num = 0
            self.card_total = 0.00
            self.card_num = 0
            s = shelve.open("options.txt")
            for i in self.bravo["sales"]:
                self.sale_total +=float(self.bravo["sales"][i]['value'])
                sold = self.prods.AppendItem(root, self.bravo["sales"][i]['time'])
                self.prods.SetItemText(sold, self.bravo["sales"][i]['payment'], 2)
                self.prods.SetItemText(sold,("R$ " + good_show("money", str(self.bravo["sales"][i]['value']))), 3)
                self.prods.SetItemFont(sold, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                try:
                    for n in range(0, len(self.bravo["sales"][i]['descriptions'])):
                        pan = r_acentos(self.bravo["sales"][i]['descriptions'][n])
                        a = self.prods.AppendItem(sold, s_acentos(pan))
                        self.prods.SetItemText(a, str(self.bravo["sales"][i]['amounts'][n]), 1)
                        self.prods.SetItemText(a,("R$ " + good_show("money", str(self.bravo["sales"][i]['prices'][n]))).replace(".",","), 3)
                except:
                    pass
                if self.bravo["sales"][i]['discount']!=0:
                    web = self.prods.AppendItem(sold, u"Desconto")
                    self.prods.SetItemText(web,("R$ "+ good_show("money", str(self.bravo["sales"][i]['discount']))).replace(".",","), 3)
                if self.bravo["sales"][i]['tax']!=0:
                    bew = self.prods.AppendItem(sold, u"Taxas adicionais")
                    self.prods.SetItemText(bew,("R$ "+ good_show("money", str(self.bravo["sales"][i]['tax']))).replace(".",","), 3)
                self.sale_num+=1
                if self.bravo["sales"][i]['payment']==u"Dinheiro":
                    self.money_num+=1
                    self.money_total+=float(self.bravo["sales"][i]['value'])
                elif self.bravo["sales"][i]['payment']==u"Cartão":
                    self.card_num+=1
                    self.card_total+=float(self.bravo["sales"][i]['value'])
            s.close()
            self.prods.SetItemText(root, str(self.sale_num), 1)
            self.prods.SetItemText(root, ("R$ " + good_show("money", str(self.sale_total))).replace(".",","), 3)
            self.prods.Expand(root)

            raz = self.expent.AddRoot(self.alfa.GetValue())
            self.spent_total = 0.0
            self.spent_num = 0
            self.expent.SetItemFont(raz, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            for i in self.bravo["spent"]:
                hour = self.bravo["spent"][i]['time']
                val = float(self.bravo["spent"][i]['value'])
                paran = r_acentos(self.bravo["spent"][i]['description'])
                des = s_acentos(paran)
                self.spent_num+=1
                self.spent_total+= val
                golf = self.expent.AppendItem(raz, hour)
                self.expent.SetItemText(golf, des, 1)
                self.expent.SetItemText(golf, ("R$ " + good_show("money", str(val))).replace(".", ","), 3)
            self.expent.SetItemText(raz, "Gastos", 1)
            self.expent.SetItemText(raz, str(self.spent_num), 2)
            self.expent.SetItemText(raz, ("R$ " + good_show("money", str(self.spent_total))).replace(".", ","), 3)
            self.expent.Expand(raz)

            pain = self.was.AddRoot(u"Desperdícios de " + str(self.alfa.GetValue()))
            self.twas = 0.0
            self.cwas = 0
            self.was.SetItemFont(pain, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            for i in self.bravo["wastes"]:
                amt = int(self.bravo["wastes"][i]['amount'])
                valo = float(self.bravo["wastes"][i]['unit_price'])*amt
                desc = r_acentos(self.bravo["wastes"][i]['description'])
                self.cwas+=1
                self.twas+= valo
                king = self.was.AppendItem(pain, s_acentos(desc))
                self.was.SetItemText(king, str(amt), 1)
                self.was.SetItemText(king, ("R$ " + good_show("money", str(valo))).replace(".", ","), 2)
            self.was.SetItemText(pain, str(self.cwas), 1)
            self.was.SetItemText(pain, ("R$ " + good_show("money", str(self.twas))).replace(".", ","), 2)
            self.was.Expand(pain)

            self.delta.SetValue(good_show("money", str(self.sale_total - self.spent_total)).replace(".", ","))
            self.echo.SetValue(good_show("money", str(self.sale_total)).replace(".", ","))
            self.hotel.SetValue(str(self.sale_num))
            self.india.SetValue(good_show("money", str(self.money_total)).replace(".", ","))
            self.juliet.SetValue(str(self.money_num))
            self.lima.SetValue(good_show("money", str(self.card_total)).replace(".", ","))
            self.oscar.SetValue(str(self.card_num))
            self.quilo.SetValue(good_show("money", str(self.spent_total)).replace(".", ","))
            self.tango.SetValue(str(self.spent_num))
            try:
                if len(self.bravo["closure"])==0:
                    alpha = self.charlie[self.foxfrot.index(self.alfa.GetValue())+1]
                    zetta = shelve.open(current_dir + "\\saves\\" + alpha)
                    self.uniforme.SetValue(good_show("money", str(zetta["closure"][0])).replace(".", ","))
                    zetta.close()

                elif self.bravo["closure"][10]==0.0:

                    alpha = self.charlie[self.foxfrot.index(self.alfa.GetValue())+1]
                    zetta = shelve.open(current_dir + "\\saves\\" + alpha)
                    self.uniforme.SetValue(good_show("money", str(zetta["closure"][0])).replace(".", ","))
                    zetta.close()
                else:
                    self.uniforme.SetValue(good_show("money", str(self.bravo["closure"][10])).replace(".", ","))
            except:
                pass
            try:
                self.xray.SetValue(good_show("money", str(self.bravo["closure"][12])).replace(".", ","))
            except:
                pass
            try:
                self.qwerty.SetValue(good_show("money", str(self.bravo["closure"][14])).replace(".", ","))
            except:
                pass
            tyde = float(self.uniforme.GetValue().replace(",", ".")) + float(self.india.GetValue().replace(",", ".")) - float(self.quilo.GetValue().replace(",", "."))
            self.wilson.SetValue(good_show("money", str(tyde).replace(".", ",")))
            if self.xray.GetValue() == "0,00":
                tide = float(self.wilson.GetValue().replace(",", ".")) - float(self.qwerty.GetValue().replace(",","."))
            else:
                tide = float(self.xray.GetValue().replace(",", ".")) - float(self.qwerty.GetValue().replace(",","."))
            if tide<0:
                tide = 0.0
            self.zebra.SetValue(good_show("money", str(tide).replace(".", ",")))
            self.bravo.close()
            self.saver()
            self.completer()

    def clean(self):
        self.prods.DeleteAllItems()
        self.expent.DeleteAllItems()
        self.was.DeleteAllItems()
        self.delta.SetValue("0,00")
        self.echo.SetValue("0,00")
        self.hotel.SetValue("0")
        self.india.SetValue("0,00")
        self.juliet.SetValue("0")
        self.lima.SetValue("0,00")
        self.oscar.SetValue("0")
        self.quilo.SetValue("0,00")
        self.tango.SetValue("0")
        self.uniforme.SetValue("0,00")
        self.wilson.SetValue("0,00")
        self.xray.SetValue("0,00")
        self.zebra.SetValue("0,00")
        self.qwerty.SetValue("0,00")

    def completer(self):
        texts = [self.a1,self.a2,self.a3, self.a4, self.a5, self.a6, self.a7,
                self.a8, self.a9, self.a10, self.a11, self.a12, self.a13, self.a14]
        texas = [self.a3, self.a5, self.a7, self.a9]
        mon = self.GetTextExtent('R$')[0]
        dot = self.GetTextExtent('.')[0]
        space = 302
        for box in texts:
            wid = box.GetSize()[0]
            post = box.GetPosition()[1]
            free = space-wid
            if box in texas:
                dots = free//dot
                wx.StaticText(box.GetParent(),-1, '.'*dots, pos=(5+wid,post))
            else:
                free = free-mon
                dots = free//dot
                if box is texts[0]:
                    wx.StaticText(box.GetParent(),-1, '.'*dots + 'R$', pos=(10+wid,post))
                else:
                    wx.StaticText(box.GetParent(),-1, '.'*dots + 'R$', pos=(5+wid,post))

    def row(self, event):
        self.alfa.Destroy()
        self.starter()
        self.run()

    def saver(self):
        a1 = float(self.delta.GetValue().replace(",","."))
        b1 = float(self.echo.GetValue().replace(",","."))
        c1 = int(self.hotel.GetValue().replace(",","."))
        d1 = float(self.india.GetValue().replace(",","."))
        e1 = int(self.juliet.GetValue().replace(",","."))
        f1 = float(self.lima.GetValue().replace(",","."))
        g1 = int(self.oscar.GetValue().replace(",","."))
        h1 = float(self.quilo.GetValue().replace(",","."))
        i1 = int(self.tango.GetValue().replace(",","."))
        j1 = float(self.uniforme.GetValue().replace(",","."))
        k1 = float(self.wilson.GetValue().replace(",","."))
        l1 = float(self.xray.GetValue().replace(",","."))
        m1 = float(self.zebra.GetValue().replace(",","."))
        n1 = float(self.qwerty.GetValue().replace(",","."))
        if l1:
            a0 = l1-n1
        else:
            a0 = k1-n1
        if a0<0:
            a0 = 0.0
        self.nig = self.charlie[self.foxfrot.index(self.alfa.GetValue())]
        self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
        self.bravo["closure"] = [a0,a1,b1,c1,d1,e1,f1,g1,h1,i1,j1,k1,l1,m1,n1]
        self.bravo.close()

    def win2(self, event):
        sell(self)
    def win2_(self, event):
        red = self.prods.GetSelection()
        if self.prods.GetRootItem()==red:
            return
        white = self.prods.GetItemText(red, 0)
        self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
        for i in self.bravo["sales"]:
            if self.bravo["sales"][i]['time'] == white or self.bravo["sales"][i]['time'] == self.prods.GetItemText(self.prods.GetItemParent(red), 0):
                black = i
                sell(self, mode=[(current_dir + "\\saves\\" + self.nig), black, white])
        self.bravo.close()
    def win4(self, event):
        expenses(self)
    def win4_(self,event):
        red = self.expent.GetSelection()
        if self.expent.GetRootItem()==red:
            return
        white = self.expent.GetItemText(red, 0)
        self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
        for i in self.bravo["spent"]:
            if self.bravo["spent"][i]['time']==white:
                black = i
                expenses(self, mode=[(current_dir + "\\saves\\" + self.nig), black, white])
        self.bravo.close()
    def win6(self,event):
        redit(self, dark=self.alfa.GetValue())
    def win7(self, event):
        wasted(self)
    def win7_(self, event):
        red = self.was.GetSelection()
        if self.was.GetRootItem()==red:
            return
        white = self.was.GetItemText(red, 0)
        self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
        for i in self.bravo["wastes"]:
            thor = float(str(self.was.GetItemText(red,2)).replace('R$ ', '').replace(',','.'))
            if s_acentos(r_acentos(self.bravo["wastes"][i]['description'])) == white and self.bravo["wastes"][i]['amount']==int(self.was.GetItemText(red,1)) and thor==self.bravo["wastes"][i]['value']==float(self.was.GetItemText(red, 2).replace(',','.').replace('R$ ', '')):
                black = i
                wasted(self, mode=[(current_dir + "\\saves\\" + self.nig), black, self.bravo["wastes"][i]['time']])
        self.bravo.close()


class redit(wx.Frame):
    def __init__(self, parent, frame_id=-1, title=u'Recuperação de Registros', dark=""):
        wx.Frame.__init__(self, parent, frame_id, title, size=(1000, 430), style =wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.SetIcon(general_icon)
        self.dark = dark
        self.Centre()
        self.SetBackgroundColour('#D6D6D6')
        self.pilot = wx.Panel(self, -1, size =  (730,380), pos = (10, 10), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.plist = wx.gizmos.TreeListCtrl(self.pilot, -1, pos = (10,10), size = (710,360), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.plist.AddColumn(u"Horário", width = 120)
        self.plist.AddColumn(u"Tipo de mud.", width = 95)
        self.plist.AddColumn(u"Tipo de reg.", width = 90)
        self.plist.AddColumn(u"Descrição", width = 210)
        self.plist.AddColumn(u"Quantidade", width = 90)
        self.plist.AddColumn(u"Valor", width = 100)
        self.plist.SetMainColumn(0)
        self.final = wx.Panel(self, -1, size = (240, 380), pos = (750,10), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        wx.StaticText(self.final, -1, u"Registros de", pos = (5,80))
        rec = wx.Button(self.final, -1, u"Recuperar registro", pos = (5,200))
        rec.Bind(wx.EVT_BUTTON, self.rem)
        self.first_time()
        self.sprint(1)
        self.Show()

    def first_time(self):
        one = threading.Thread(target=self.starter, args=True)
        one.daemon = True
        one.start()

    def sprint(self, event):
        two = threading.Thread(target=self._sprint, args=True)
        two.daemon = True
        two.start()

    def starter(self):
        self.foxfrot = []
        self.charlie = []
        for root, dirs, files in os.walk("saves"):
            if root != "saves":
                break
            files.sort()
            files.reverse()
            for i in files:
                try:
                    if len(str(int(i.replace("-",'').replace(".txt", ""))))==8:
                        ab = i[8:10]
                        ab = ab + "/" + i[5:7]
                        ab = ab + "/" + i[0:4]
                        self.foxfrot.append(ab)
                        self.charlie.append(i)
                except:
                    pass
        self.alfa = wx.ComboBox(self.final, -1, choices = self.foxfrot, size = (130,-1), pos = (5, 100), style = wx.CB_READONLY)
        self.alfa.Bind(wx.EVT_COMBOBOX, self.sprint)
        self.alfa.Bind(wx.EVT_TEXT_ENTER, self.sprint)
        if len(self.foxfrot)!=0 and self.dark=="":
            self.alfa.SetValue(self.foxfrot[0])
        elif self.dark!="":
            self.alfa.SetValue(self.dark)
        self.pika = [u'Gastos, Vendas e Desperdícios', u'Produtos e Clientes']
        self.pokemon = wx.ComboBox(self.final, choices=self.pika, size=(230, -1), pos = (5, 30), style=wx.CB_READONLY|wx.TE_MULTILINE)
        self.pokemon.SetValue(self.pika[0])
        self.pokemon.Bind(wx.EVT_COMBOBOX, self.changer)
        self.pokemon.Bind(wx.EVT_TEXT_ENTER, self.changer)

    def changer(self, event):
        char = self.pokemon.GetSelection()
        if char==0:
            self.alfa.Enable()
            self.sprint(1)
        elif char==1:
            self.alfa.Disable()
            self.sprint(1)

    def _sprint(self, event):
        if str(self.alfa.GetValue())!='' and self.pokemon.GetSelection()==0:
            self.clean()
            self.nig = self.charlie[self.foxfrot.index(self.alfa.GetValue())]
            self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig)
            red = self.bravo["edit"]
            goal = self.plist.AddRoot(self.alfa.GetValue())
            self.plist.SetItemText(goal, u"Registros modificados", 3)
            count  = 0
            for i in red:
                count+=1
                a = self.plist.AppendItem(goal, i)
                self.plist.SetItemFont(a, wx.Font(9,wx.SWISS, wx.NORMAL, wx.BOLD))
                if red[i]['mode']==1:
                    self.plist.SetItemText(a, u"Editado", 1)
                elif red[i]['mode']==2:
                    self.plist.SetItemText(a, u"Apagado", 1)
                if len(red[i])==6:
                    self.plist.SetItemText(a, u"Gasto", 2)
                    self.plist.SetItemText(a, red[i]['description'], 3)
                    self.plist.SetItemText(a, ("R$ " + good_show("money", str(red[i]['value']).replace('.',','))), 5)
                elif len(red[i])==8:
                    self.plist.SetItemText(a, u"Desperdício", 2)
                    self.plist.SetItemText(a, red[i]['description'], 3)
                    self.plist.SetItemText(a, str(red[i]['amount']), 4)
                    self.plist.SetItemText(a, ("R$ " + good_show("money", str(red[i]['value']).replace('.',','))), 5)
                else:
                    self.plist.SetItemText(a, u"Venda", 2)
                    self.plist.SetItemText(a, red[i]['time'], 3)
                    count2 = 0
                    val = 0
                    for x in red[i]['descriptions']:
                        p = red[i]['descriptions'].index(x)
                        ver = float(red[i]['prices'][p])
                        count2+=1
                        val+=ver
                        b = self.plist.AppendItem(a, "---------------")
                        self.plist.SetItemText(b, x, 3)
                        self.plist.SetItemText(b, str(red[i]['amounts'][p]), 4)
                        self.plist.SetItemText(b, ("R$ " + good_show("money", str(ver)).replace('.',',')), 5)
                    if red[i]['discount']!=0:
                        ver = float(red[i]['discount'])
                        val -= ver
                        b = self.plist.AppendItem(a, "---------------")
                        self.plist.SetItemText(b, u'Desconto', 3)
                        self.plist.SetItemText(b,("R$ "+ good_show("money", str(ver))).replace(".",","), 5)
                    if red[i]['tax']!=0:
                        ver = float(red[i]['tax'])
                        val += ver
                        b = self.plist.AppendItem(a, "---------------")
                        self.plist.SetItemText(b, u'Taxas adicionais', 3)
                        self.plist.SetItemText(b,("R$ "+ good_show("money", str(ver))).replace(".",","), 5)
                    self.plist.SetItemText(a, str(count2), 4)
                    self.plist.SetItemText(a, ("R$ " + good_show("money", str(val)).replace('.',',')), 5)
            self.plist.SetItemText(goal, str(count), 4)
            self.plist.Expand(goal)
            self.plist.SetItemFont(goal, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.bravo.close()
        elif str(self.alfa.GetValue())!='' and self.pokemon.GetSelection()==1:
            self.clean()
            vb = []
            for root, dirs, files in os.walk('#Trash'):
                hu = root.split('\\')
                if len(hu)==5:
                    vb.append(root)
            fg = {}
            for g in vb:
                s = g.split('\\')
                e1 = s[4].split('_')
                tempo= e1[1].replace('-', ':')
                e2 = e1[0].split('-')
                date = e2[2] + '/' + e2[1] + '/' + e2[0]
                pcid = s[3]
                if s[2] == 'edited':
                    done = u'Editado'
                elif s[2] == 'deleted':
                    done = u'Apagado'
                if s[1] == 'clients':
                    kind = u'Cliente'
                elif s[1] == 'products':
                    kind = u'Produto'
                if date in fg:
                    hj = fg[date]
                    hj.append([time, pcid, done, kind, g])
                    fg[date] = hj
                else:
                    fg[date] = [[time, pcid, done, kind, g]]
            root = self.plist.AddRoot(u'---------')
            self.plist.SetItemText(root, u'Registros Modificados', 3)
            self.plist.SetItemFont(root, wx.Font(12,wx.SWISS, wx.NORMAL, wx.BOLD))
            count = 0
            for a in fg:
                count2 = 0
                sec = self.plist.AppendItem(root, a)
                self.plist.SetItemFont(sec, wx.Font(9,wx.SWISS, wx.NORMAL, wx.BOLD))
                for w in fg[a]:
                    count +=1
                    count2 +=1
                    ter = self.plist.AppendItem(sec, w[0])
                    self.plist.SetItemText(ter, w[3], 2)
                    self.plist.SetItemText(ter, w[2], 1)
                    self.plist.SetItemText(ter, w[1], 3)
                self.plist.SetItemText(sec, str(count2), 4)
            self.plist.SetItemText(root, str(count), 4)
            self.fg = fg
            self.plist.ExpandAll(root)

    def rem(self, event):
        boom = self.plist.GetSelection()
        key2 = str(self.plist.GetItemText(boom, 0))
        if boom == self.plist.GetRootItem() or len(key2)==10:
            return
        ask(self,-1, u"Restauração", 5, 4)

    def remover(self, event):
        boom = self.plist.GetSelection()
        atom = str(self.plist.GetItemText(boom, 2))
        key2 = str(self.plist.GetItemText(boom, 0))
        if boom == self.plist.GetRootItem() or len(key2)==10:
            return
        if len(atom)==0:
            boom = self.plist.GetItemParent(boom)
            atom = str(self.plist.GetItemText(boom, 2))
            key2 = str(self.plist.GetItemText(boom, 0))
        if self.pokemon.GetSelection()==0:
            self.bravo = shelve.open(current_dir + "\\saves\\" + self.nig, writeback=True)
            if atom == u"Venda":
                key = self.bravo["edit"][key2]['key']
                tor = self.bravo["edit"][key2]
                del tor['mode']
                ckey = self.bravo['edit'][key2]['client_id']
                if ckey in os.listdir('clients'):
                    try:
                        h = shelve.open(current_dir + '\\clients\\' + ckey + '\\' + ckey + '_deals.txt', writeback=True)
                        r =  str(self.nig[:10] + '_' + self.bravo['edit'][key2]['time'].replace(':','-'))
                        h[r] = tor
                        h.close()
                    except:
                        pass
                del tor['key']
                self.bravo["sales"][key] = tor
                hair = self.bravo["edit"]
                del hair[key2]
                self.bravo["edit"]=hair
                self.bravo.close()
                self.sprint(1)
                return
            elif atom == u"Gasto":
                key = self.bravo["edit"][key2]['key']
                rt = self.bravo["edit"][key2]
                del rt['key']
                del rt['mode']
                self.bravo["spent"][key] = rt
                hair = self.bravo["edit"]
                del hair[key2]
                self.bravo["edit"]=hair
                self.bravo.close()
                self.sprint(1)
                return
            elif atom == u"Desperdício":
                key = self.bravo["edit"][key2]['key']
                mn = self.bravo["edit"][key2]
                del mn['key']
                del mn['mode']
                self.bravo["wastes"][key] = mn
                hair = self.bravo["edit"]
                del hair[key2]
                self.bravo["edit"]=hair
                self.bravo.close()
                self.sprint(1)
                return
        elif self.pokemon.GetSelection()==1:
            for i in self.fg:
                for x in self.fg[i]:
                    if x[0]==key2:
                        s = x[4].split('\\')
                        y = s[1] + '/' + s[3]
                        if os.path.exists(y):
                            shutil.rmtree(y)
                        shutil.copytree(x[4], y)
                        shutil.rmtree(x[4])
                        self.sprint(1)
                        return

    def clean(self):
        self.plist.DeleteAllItems()


class wasted(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Desperdícios', mode=None):
        if not mode:
            mode = []
        wx.Frame.__init__(self, parent,frame_id, title, size=(500, 200), style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.Centre()
        self.SetIcon(general_icon)
        self.mode=mode
        self.SetBackgroundColour('#D6D6D6')
        #first
        first = wx.Panel(self, -1, size = (480, 85), pos = (10,10), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        first.SetBackgroundColour('#D6D6D6')
        wx.StaticText(first, -1, u"Descrição:", pos = (10,5))
        self.tex1 = wx.TextCtrl(first, -1, pos = (10,25), size = (210,30))
        self.tex1.Bind(wx.EVT_CHAR, self.all)
        wx.StaticText(first, -1, u"Quantidade:", pos = (255,5))
        self.tex3 = wx.TextCtrl(first, -1, pos = (255,25),size=(60,30))
        self.tex3.Bind(wx.EVT_CHAR, self.check_num)
        wx.StaticText(first, -1, u"Valor unitário:" , pos = (375,5))
        wx.StaticText(first, -1, "R$", pos = (360,32))
        self.tex2 = wx.TextCtrl(first, -1, pos = (375,25), size = (60,30))
        self.tex2.Bind(wx.EVT_CHAR, self.check_money)
        self.tex2.SetValue("0,00")
        if mode:
            self.planet = shelve.open(self.mode[0])
            self.tex1.SetValue(self.planet["wastes"][mode[1]]['description'])
            self.tex2.SetValue(good_show("money", str(self.planet["wastes"][mode[1]]['unit_price'])).replace(".",","))
            self.tex3.SetValue(str(self.planet["wastes"][mode[1]]['amount']))
            self.planet.close()
        #last
        last = wx.Panel(self, -1, size = (480, 60), pos = (10,105), style = wx.SUNKEN_BORDER)
        last.SetBackgroundColour('#D6D6D6')
        last_ = wx.Panel(last, pos=(80,10),size=(320,40), style = wx.SIMPLE_BORDER)
        finish = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png', wx.BITMAP_TYPE_PNG), u'Finalizar', pos = (0, 0), size = (100,40))
        finish.Bind(wx.EVT_BUTTON, self.ask3)
        restart = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Recomeçar', pos = (100, 0), size = (120,40))
        restart.Bind(wx.EVT_BUTTON, self.ask1)
        cancel = GenBitmapTextButton(last_, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u"sair",pos = (220, 0), size = (100,40))
        cancel.Bind(wx.EVT_BUTTON, self.ask2)

        self.Show()

    def check_num(self, event):
        num = [9, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 127, 314, 316]
        pro = event.GetKeyCode()
        if pro in num:
            event.Skip()
        elif pro==13:
            self.enter(event)

    def ask1(self, event):
        ask(self, -1, u"Apagar Tudo", 1, 2)

    def ask2(self, event):
        pl = str(self.tex1.GetValue())
        po = str(self.tex2.GetValue())
        pk = str(self.tex3.GetValue())
        if pl=='' and po=='0,00' and (pk=='' or pk=='0'):
            self.Close()
            return
        ask(self, -1, u"Sair", 2, 2)

    def ask3(self, event):
        ask(self, -1, u"Finalizar Registro", 3, 5)

    def check_money(self, event):
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
        dex = [8, 127, 314, 316, 9]
        pro = event.GetKeyCode()
        rhyme = self.tex2.GetValue().replace(",", ".")
        try:
            if pro == dex[2] or pro == dex[3] or pro == dex[4]:
                event.Skip()
            elif pro == dex[0] or pro == dex[1]:
                wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
                self.tex2.SetValue(good_show("money", str(wer).replace(".", ",")))
            elif pro in num:
                if len(str(self.tex2.GetValue()))==14:
                    self.tex2.SetValue('0,00')
                    return
                wes = float(rhyme)*10 + float(chr(pro))/100
                self.tex2.SetValue(good_show("money", str(wes).replace(".", ",")))
            self.enter(event)
        except:
            self.tex2.SetValue("0,00")

    def enter(self, event):
        pro = event.GetKeyCode()
        if pro==13:
            self.ask3(event)

    def all(self,event):
        if event.GetKeyCode() == 13:
            self.enter(event)
        else:
            event.Skip()

    def clean(self):
        self.tex1.Clear()
        self.tex2.Clear()
        self.tex2.SetValue("0,00")
        self.tex3.Clear()

    def end(self):
        descri = self.tex1.GetValue().capitalize()
        val = float(self.tex2.GetValue().replace(",", "."))
        amt = self.tex3.GetValue()
        if len(amt)==0: amt = 0
        else: amt = int(amt)
        tval = val*amt
        if len(descri)==0 or val==0 or amt==0:
            a = wx.MessageDialog(self, u'Dados insuficientes!', u'Error 404', style = wx.OK|wx.ICON_ERROR)
            a.ShowModal()
            a.Destroy()
            return
        self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
        date = str(datetime.now().year) + "-" + good_show("o", str(datetime.now().month)) + "-" + good_show("o", str(datetime.now().day))
        self.info = current_dir + "\\saves\\" + date + ".txt"
        self.day_sell = shelve.open(self.info)
        if "sales" not in self.day_sell:
            self.day_sell["sales"] = {}
            self.day_sell["secount"] = 0
            self.day_sell["edit"] = {}
            self.day_sell["spent"] = {}
            self.day_sell["spcount"] = 0
            self.day_sell["closure"] = []
            self.day_sell["wastes"] = {}
            self.day_sell["wcount"] = 0
        if not self.mode:
            key = self.day_sell["wcount"] + 1
            asw = self.day_sell["wastes"]
            asw[key] = {'time':self.finish_time,
                        'edit':0,
                        'description':descri,
                        'unit_price':val,
                        'amount':amt,
                        'value':tval}
            self.day_sell["wastes"] = asw
            self.day_sell["wcount"] = key
        else:
            self.day_sell.close()
            self.day_sell = shelve.open(self.mode[0])
            key = self.mode[1]
            hour = self.mode[2]
            asw = self.day_sell["edit"]
            asw[self.finish_time] = self.day_sell["wastes"][key]
            asw[self.finish_time]['key'] = key
            asw[self.finish_time]['mode'] = 1
            self.day_sell["edit"] = asw
            adw = self.day_sell["wastes"]
            asw[key] = {'time': hour,
                        'edit': 1,
                        'description': descri,
                        'unit_price': val,
                        'amount': amt,
                        'value': tval}
            self.day_sell["wastes"] = adw
        self.clean()
        self.day_sell.close()
        confirmation(self, -1, u"Sucesso", 3)


class resumo(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u"Resumo Mensal"):
        wx.Frame.__init__(self, parent,frame_id, title, size = (1200,680), style = wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.SetBackgroundColour('#D6D6D6')
        self.Centre()
        self.SetIcon(general_icon)
        self.part1 = wx.Panel(self, -1, pos=(10,10), size = (1180,280), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.tex0 = wx.TextCtrl(self.part1, -1, pos = (200,70) , size = (100,30), style = wx.TE_READONLY)
        self.tex1 = wx.TextCtrl(self.part1, -1, pos = (200,125), size = (100,30), style = wx.TE_READONLY)
        self.tex2 = wx.TextCtrl(self.part1, -1, pos = (200,180), size = (100,30), style = wx.TE_READONLY)
        self.tex3 = wx.TextCtrl(self.part1, -1, pos = (200,235), size = (100,30), style = wx.TE_READONLY)
        self.tex4 = wx.TextCtrl(self.part1, -1, pos = (500,15) , size = (100,30), style = wx.TE_READONLY)
        self.tex5 = wx.TextCtrl(self.part1, -1, pos = (500,70) , size = (100,30), style = wx.TE_READONLY)
        self.tex6 = wx.TextCtrl(self.part1, -1, pos = (500,125), size = (100,30), style = wx.TE_READONLY)
        self.tex7 = wx.TextCtrl(self.part1, -1, pos = (500,180), size = (100,30), style = wx.TE_READONLY)
        self.tex8 = wx.TextCtrl(self.part1, -1, pos = (500,235), size = (100,30), style = wx.TE_READONLY)
        self.lis1 = wx.ListCtrl(self.part1, -1, pos = (625,30) , size = (250,240), style = wx.SIMPLE_BORDER|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        self.lis2 = wx.ListCtrl(self.part1, -1, pos = (900,30) , size = (250,240), style = wx.SIMPLE_BORDER|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        self.lis1.InsertColumn(0, u'Descrição')
        self.lis1.InsertColumn(1, u'Quantidade')
        self.lis1.InsertColumn(2, u'Valor')
        self.lis2.InsertColumn(3, u'Descrição')
        self.lis2.InsertColumn(4, u'Quantidade')
        self.lis2.InsertColumn(5, u'Valor')
        wx.StaticText(self.part1, -1, u'Mês/Ano', pos = (10,22))
        wx.StaticText(self.part1, -1, u'Lucro do Mês', pos = (10,77))
        wx.StaticText(self.part1, -1, u'Total Gasto', pos = (10,132))
        wx.StaticText(self.part1, -1, u'Total Vendido', pos = (10,187))
        wx.StaticText(self.part1, -1, u'Total Perdido', pos = (10,242))
        wx.StaticText(self.part1, -1, u'Rendimento Médio por dia', pos = (310,22))
        wx.StaticText(self.part1, -1, u'Total Vendido no Cartão', pos = (310,77))
        wx.StaticText(self.part1, -1, u'Total Vendido em Dinheiro', pos = (310,132))
        wx.StaticText(self.part1, -1, u'Dia da Semana menos rentável', pos = (310,187))
        wx.StaticText(self.part1, -1, u'Dia da Semana mais rentável', pos = (310,242))
        wx.StaticText(self.part1, -1, u'Produtos de Maior Redimento', pos = (625,10)).SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        wx.StaticText(self.part1, -1, u'Produtos Mais Vendidos', pos = (900,10)).SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.tex0.SetBackgroundColour('#C6C6C6')
        self.tex1.SetBackgroundColour('#C6C6C6')
        self.tex2.SetBackgroundColour('#C6C6C6')
        self.tex3.SetBackgroundColour('#C6C6C6')
        self.tex4.SetBackgroundColour('#C6C6C6')
        self.tex5.SetBackgroundColour('#C6C6C6')
        self.tex6.SetBackgroundColour('#C6C6C6')
        self.tex7.SetBackgroundColour('#C6C6C6')
        self.tex8.SetBackgroundColour('#C6C6C6')
        self.part2 = wx.Panel(self, -1, pos = (10,295), size = (1180,60), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.part21 = wx.Panel(self.part2, -1, pos = (10,5), size = (620,50), style = wx.SIMPLE_BORDER)
        self.part22 = wx.Panel(self.part2, -1, pos = (790,5), size = (380,50), style = wx.SIMPLE_BORDER)
        button1 = GenBitmapTextButton(self.part21, -1, wx.Bitmap(current_dir + '\\data\\pics\\Report.png', wx.BITMAP_TYPE_PNG), u'Tabela de Vendas', pos = (0,0), size=(150,50))
        button2 = GenBitmapTextButton(self.part21, -1, wx.Bitmap(current_dir + '\\data\\pics\\Report.png', wx.BITMAP_TYPE_PNG), u'Tabela de Gastos', pos = (150,0), size=(150,50))
        button3 = GenBitmapTextButton(self.part21, -1, wx.Bitmap(current_dir + '\\data\\pics\\Report.png', wx.BITMAP_TYPE_PNG), u'Tabela de Produtos', pos = (300,0), size=(150,50))
        button7 = GenBitmapTextButton(self.part21, -1, wx.Bitmap(current_dir + '\\data\\pics\\Report.png', wx.BITMAP_TYPE_PNG), u'Tabela de Desperdícios', pos = (450,0), size=(170,50))
        button8 = GenBitmapTextButton(self.part2, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Recalcular', pos = (645,5), size=(130,50), style = wx.SIMPLE_BORDER)
        button4 = GenBitmapTextButton(self.part22, -1, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u'Registar Gasto', pos = (0,0), size=(130,50))
        button5 = GenBitmapTextButton(self.part22, -1, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u'Registrar Ganho', pos = (130,0), size=(130,50))
        button6 = GenBitmapTextButton(self.part22, -1, wx.Bitmap(current_dir + '\\data\\pics\\system-users.png', wx.BITMAP_TYPE_PNG), u'Observações', pos = (260,0), size=(120,50))
        button1.Bind(wx.EVT_BUTTON, self.sareport)
        button2.Bind(wx.EVT_BUTTON, self.spreport)
        button3.Bind(wx.EVT_BUTTON, self.prreport)
        button7.Bind(wx.EVT_BUTTON, self.wareport)
        button8.Bind(wx.EVT_BUTTON, self.restarter)
        button4.Bind(wx.EVT_BUTTON, self.spents)
        button5.Bind(wx.EVT_BUTTON, self.wonss)
        button6.Bind(wx.EVT_BUTTON, self.obstxt)
        button1.SetBackgroundColour('#FFDF85')
        button2.SetBackgroundColour('#FFDF85')
        button3.SetBackgroundColour('#FFDF85')
        button7.SetBackgroundColour('#FFDF85')
        button4.SetBackgroundColour('#C2E6F8')
        button5.SetBackgroundColour('#C2E6F8')
        button6.SetBackgroundColour('#C2E6F8')

        self.part3 = wx.Panel(self, pos = (10,360), size = (1180,280), style = wx.SIMPLE_BORDER)

        self.part31 = wx.Panel(self.part3, 56, pos = (10,5), size = (575, 260), style = wx.SUNKEN_BORDER)
        self.part31.SetBackgroundColour('#D6D6D6')
        self.won = wx.gizmos.TreeListCtrl(self.part31, -1, pos = (10,10), size = (400, 240), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.won.AddColumn(u"Data", width = 110)
        self.won.AddColumn(u"Descrição", width = 180)
        self.won.AddColumn(u"Valor", width = 110)
        self.won.SetMainColumn(0)
        dr = wx.StaticText(self.part31, -1, u'Ganhos\nMensais', pos=(420,10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.lasta = wx.Panel(self.part31, pos = (420,80), size = (145,160), style = wx.SIMPLE_BORDER)

        button31 = GenBitmapTextButton(self.lasta, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Adicionar', pos = (0,0), size=(145,40))
        button32 = GenBitmapTextButton(self.lasta, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (0,40), size=(145,40))
        button33 = GenBitmapTextButton(self.lasta, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (0,80), size=(145,40))
        button34 = GenBitmapTextButton(self.lasta, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Atualizar', pos = (0,120), size=(145,40))
        button31.Bind(wx.EVT_BUTTON, self.wonss)
        button32.Bind(wx.EVT_BUTTON, self.won_e)
        button33.Bind(wx.EVT_BUTTON, self.remove1)
        button34.Bind(wx.EVT_BUTTON, self.fill_31)

        self.part32 = wx.Panel(self.part3, 56, pos = (590,5), size = (575, 260), style = wx.SUNKEN_BORDER)
        self.part32.SetBackgroundColour('#D6D6D6')
        self.spent = wx.gizmos.TreeListCtrl(self.part32, -1, pos = (10,10), size = (400, 240), style = wx.SIMPLE_BORDER|wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.spent.AddColumn(u"Data", width = 110)
        self.spent.AddColumn(u"Descrição", width = 180)
        self.spent.AddColumn(u"Valor", width = 110)
        self.spent.SetMainColumn(0)
        dr = wx.StaticText(self.part32, -1, u'Gastos\nMensais', pos=(420,10))
        dr.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.lastb = wx.Panel(self.part32, pos = (420,80), size = (145,160), style = wx.SIMPLE_BORDER)

        button41 = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Add.png', wx.BITMAP_TYPE_PNG), u'Adicionar', pos = (0,0), size=(145,40))
        button42 = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Edit.png', wx.BITMAP_TYPE_PNG), u'Editar', pos = (0,40), size=(145,40))
        button43 = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', pos = (0,80), size=(145,40))
        button44 = GenBitmapTextButton(self.lastb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png', wx.BITMAP_TYPE_PNG), u'Atualizar', pos = (0,120), size=(145,40))
        button41.Bind(wx.EVT_BUTTON, self.spents)
        button42.Bind(wx.EVT_BUTTON, self.spent_e)
        button43.Bind(wx.EVT_BUTTON, self.remove2)
        button44.Bind(wx.EVT_BUTTON, self.fill_32)

        self.pre_go()
        self.Show()

    def OnPaint(self, event):
        wx.PaintDC(self.promo).DrawBitmap(wx.Bitmap(current_dir + '\\data\\custom-logo\\cpromo1.jpg'), 0, 0)

    def clean(self):
        self.lis1.DeleteAllItems()
        self.lis2.DeleteAllItems()

    def restarter(self, event):
        rest = threading.Thread(target=self.starter, args=[1])
        rest.daemon = True
        rest.start()

    def starter(self, event):
        self.clean()
        if not os.path.exists('saves'):
            os.mkdir('saves')
        t0 = 0.0
        t1 = 0.0
        t2 = 0.0
        t3 = 0.0
        t4 = 0.0
        t5 = 0.0
        t6 = 0.0
        t7 = ''
        t8 = ''
        count = 0
        pr = {}
        we = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for root, dirs, files in os.walk('saves'):
            if root!='saves': return
            for i in files:
                try:
                    if len(i)==14 and int(i[:10].replace('-','')) and i[:7]==self.charlie[self.foxfrot.index(self.alfa.GetValue())]:
                        s = shelve.open(current_dir + '\\saves\\' + i)
                        ol = i[:10]
                        ol = ol.split('-')
                        wd = calendar.weekday(int(ol[0]),int(ol[1]),int(ol[2]))
                        for v in s['sales']:
                            k = s['sales'][v]
                            t2 += k['value']
                            if k['payment']==u'Dinheiro':
                                t6 += k['value']
                            elif k['payment']==u'Cartão':
                                t5 += k['value']
                            we[wd] += k['value']
                            for p in k['descriptions']:
                                if p not in pr:
                                    pr[p] = [0, 0.0]
                                pr[p][0] += k['amounts'][k['descriptions'].index(p)]
                                pr[p][1] += k['prices'][k['descriptions'].index(p)]
                        for u in s['spent']:
                            k = s['spent'][u]
                            t1 += k['value']
                        for y in s['wastes']:
                            k = s['wastes'][y]
                            t3 += k['value']
                        count +=1
                        s.close()
                    elif len(i)==11 and int(i[:7].replace('-','')) and i[:7]==self.charlie[self.foxfrot.index(self.alfa.GetValue())]:
                        s = shelve.open(current_dir + '\\saves\\' + i)
                        ol = i[:7]
                        ol = ol.split('-')
                        for v in s['winning']:
                            k = s['winning'][v]
                            t2 += k['value']
                        for u in s['spent']:
                            k = s['spent'][u]
                            t1 += k['value']
                except:
                    pass
        pr1 = []
        pr2 = []
        lp1 = []
        lp2 = []
        for t in range(0,11):
            m = ['',0,0.0]
            for w in pr:
                if pr[w][1]>m[2] and w not in pr1:
                    m = [w,pr[w][0],pr[w][1]]
            n = ['',0,0.0]
            for z in pr:
                if pr[z][0]>n[1] and z not in pr2:
                    n = [z,pr[z][0],pr[z][1]]
            if m[2]:
                lp1.append(m)
                pr1.append(m[0])
            if n[1]:
                lp2.append(n)
                pr2.append(n[0])
        for e in lp1:
            self.lis1.Append((e[0], e[1], good_show('money', e[2])))
        for f in lp2:
            self.lis2.Append((f[0], f[1], good_show('money', f[2])))
        t0 = (t2 - t1)
        try:
            t4 = (t2 - t1)/count
        except:
            t4 = 0.0
        if max(we):
            t7 = week[we.index(max(we))]
        else: t7 = '-------'
        if min(we): t8 = week[we.index(min(we))]
        else:
            try:
                h = we
                while not min(h):
                    h.remove(0.0)
                t8 = week[we.index(min(h))]
                if t7==t8:
                    t8 = '-------'
            except:
                t8 = '-------'
        self.tex0.SetValue('R$ ' + good_show('money', t0))
        self.tex1.SetValue('R$ ' + good_show('money', t1))
        self.tex2.SetValue('R$ ' + good_show('money', t2))
        self.tex3.SetValue('R$ ' + good_show('money', t3))
        self.tex4.SetValue('R$ ' + good_show('money', t4))
        self.tex5.SetValue('R$ ' + good_show('money', t5))
        self.tex6.SetValue('R$ ' + good_show('money', t6))
        self.tex7.SetValue(t7)
        self.tex8.SetValue(t8)
        self.fill_31(0)
        self.fill_32(1)

    def pre_go(self):
        self.foxfrot = []
        self.charlie = []
        for root, dirs, files in os.walk("saves"):
            if root != "saves":
                break
            files.sort()
            files.reverse()
            d = str(datetime.now().year) +'-'+ good_show('o', str(datetime.now().month))
            self.foxfrot.append(date_reverse(d).replace('-','/'))
            self.charlie.append(d)
            for i in files:
                try:
                    if int(i[:7].replace("-",'')) and (i[:7] not in self.charlie):
                        ab = i[5:7] + "/" + i[0:4]
                        self.foxfrot.append(ab)
                        self.charlie.append(i[:7])
                except:
                    pass
        self.alfa = wx.ComboBox(self.part1, -1, choices = self.foxfrot, size = (100,30), pos = (200, 15), style = wx.CB_READONLY)
        self.alfa.Bind(wx.EVT_COMBOBOX, self.restarter)
        if len(self.foxfrot)!=0:
            self.alfa.SetValue(self.foxfrot[0])
        self.restarter(1)

    def obstxt(self, event):
        month = self.charlie[self.foxfrot.index(self.alfa.GetValue())]
        text_box(self, month)

    def sareport(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        sheet_box(self, mode=1, month=month)

    def spreport(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        sheet_box(self, mode=2, month=month)

    def prreport(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        sheet_box(self, mode=3, month=month)

    def wareport(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        sheet_box(self, mode=4, month=month)

    def spents(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        expenses(self, kind=2, month=month)

    def spent_e(self,event):
        red = self.spent.GetSelection()
        month = self.charlie[self.alfa.GetSelection()]
        if red ==self.spent.GetRootItem() or self.spent.GetItemParent(red) is self.spent.GetRootItem():
            return
        for x in self.spent_entrys:
            if x == red:
                pong = x
                break
        key = self.spent_entrys[pong]
        bravo = shelve.open(current_dir + "\\saves\\" + month + '.txt')
        polsss = bravo['spent'][key]['time']
        expenses(self, -1, u"Editar Gasto n°"+str(key), [("saves/" + month + '.txt'), key, polsss], kind=2, month=month)
        bravo.close()

    def wonss(self, event):
        month = self.charlie[self.alfa.GetSelection()]
        expenses(self, -1, u'Ganhos', kind=3, month = month)

    def won_e(self, event):
        red = self.won.GetSelection()
        month = self.charlie[self.alfa.GetSelection()]
        if red ==self.won.GetRootItem() or self.won.GetItemParent(red) is self.won.GetRootItem():
            return
        for x in self.won_entrys:
            if x==red:
                pong = x
                break
        key = self.won_entrys[pong]
        bravo = shelve.open(current_dir + "\\saves\\" + month + '.txt')
        polsss = bravo['winning'][key]['time']
        expenses(self, -1, u"Editar Ganho n°"+str(key), [("saves/" + month + '.txt'), key, polsss], kind=3, month=month)
        bravo.close()

    def fill_31(self,event):
        self.won.DeleteAllItems()
        month = self.charlie[self.alfa.GetSelection()]
        f = shelve.open(current_dir + '\\saves\\' + month + '.txt')
        days = {}
        self.won_entrys = {}
        root = self.won.AddRoot(self.alfa.GetValue())
        self.won.SetItemText(root, u'Ganhos Mensais', 1)
        self.won.SetItemFont(root,wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        total = 0.0
        if len(f):
            for dd in f['winning']:
                i = f['winning'][dd]
                if i['date'] not in days:
                    days[i['date']] = [self.won.AppendItem(root, i['date']), 0.0]
                x = self.won.AppendItem(days[i['date']][0], i['time'][:5])
                self.won.SetItemText(x, i['description'], 1)
                self.won.SetItemText(x, 'R$ ' + good_show('money', i['value']), 2)
                self.won_entrys[x] = dd
                total+=i['value']
                days[i['date']][1]+=i['value']
            self.won.SetItemText(root, 'R$ ' + good_show('money', total), 2)
            for k in days:
                self.won.SetItemText(days[k][0], 'R$ ' + good_show('money', days[k][1]), 2)
                self.won.SetItemFont(days[k][0],wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.won.ExpandAll(root)
        f.close()

    def fill_32(self,event):
        self.spent.DeleteAllItems()
        month = self.charlie[self.alfa.GetSelection()]
        f = shelve.open(current_dir + '\\saves\\' + month + '.txt')
        days = {}
        self.spent_entrys = {}
        root = self.spent.AddRoot(self.alfa.GetValue())
        self.spent.SetItemText(root, u'Gastos Mensais', 1)
        self.spent.SetItemFont(root,wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        total = 0.0
        if len(f):
            for dd in f['spent']:
                i = f['spent'][dd]
                if i['date'] not in days:
                    days[i['date']] = [self.spent.AppendItem(root, i['date']), 0.0]
                x = self.spent.AppendItem(days[i['date']][0], i['time'][:5])
                self.spent.SetItemText(x, i['description'], 1)
                self.spent.SetItemText(x, 'R$ ' + good_show('money', i['value']), 2)
                self.spent_entrys[x] = dd
                total+=i['value']
                days[i['date']][1]+=i['value']
            self.spent.SetItemText(root, 'R$ ' + good_show('money', total), 2)
            for k in days:
                self.spent.SetItemText(days[k][0], 'R$ ' + good_show('money', days[k][1]), 2)
                self.spent.SetItemFont(days[k][0],wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.spent.ExpandAll(root)
        f.close()

    def remove1(self,event):
        boom = self.won.GetSelection()
        if boom == self.won.GetRootItem():
            return
        ask(self, -1, u"Apagar Ganho", 4, 11)

    def remove2(self,event):
        boom = self.spent.GetSelection()
        if boom == self.spent.GetRootItem():
            return
        ask(self, -1, u"Apagar Gasto", 4, 12)

    def remover(self, box):
        if box==11:
            red = self.won.GetSelection()
            month = self.charlie[self.alfa.GetSelection()]
            if red ==self.won.GetRootItem() or self.won.GetItemParent(red) is self.won.GetRootItem():
                return
            bravo = shelve.open(current_dir + "\\saves\\" + month + '.txt')
            for x in self.won_entrys:
                if x==red:
                    pong = x
                    break
            key = self.won_entrys[pong]
            self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
            asw = bravo["edit"]
            asw[self.finish_time] = bravo["winning"][key]
            asw[self.finish_time]['key'] = key
            asw[self.finish_time]['mode'] = 2
            bravo["edit"] = asw
            hair = bravo["winning"]
            del hair[key]
            bravo["winning"]=hair
            bravo.close()
            self.fill_31(1)
            return
        elif box==12:
            red = self.spent.GetSelection()
            month = self.charlie[self.alfa.GetSelection()]
            if red ==self.spent.GetRootItem() or self.spent.GetItemParent(red) is self.spent.GetRootItem():
                return
            bravo = shelve.open(current_dir + "\\saves\\" + month + '.txt')
            for x in self.spent_entrys:
                if x==red:
                    pong = x
                    break
            key = self.spent_entrys[pong]
            self.finish_time = good_show("o", str(datetime.now().hour)) + ":" + good_show("o", str(datetime.now().minute)) + ":" + good_show("o", str(datetime.now().second))
            asw = bravo["edit"]
            asw[self.finish_time] = bravo["spent"][key]
            asw[self.finish_time]['key'] = key
            asw[self.finish_time]['mode'] = 2
            bravo["edit"] = asw
            hair = bravo["spent"]
            del hair[key]
            bravo["spent"]=hair
            bravo.close()
            self.fill_32(1)
            return


class text_box(wx.Frame):
    def __init__(self, parent, month,frame_id=-1, title=u'Observações'):
        wx.Frame.__init__(self, parent,frame_id, title, size = (400,300))
        self.month = month
        self.parent = parent
        self.Centre()
        self.SetMinSize((400,300))
        self.SetIcon(general_icon)
        self.SetBackgroundColour('#D6D6D6')
        self.menu1 = wx.Menu()
        self.menu1.Append(4001, u'&Salvar\tCTRL+S')
        self.menu1.Append(4002, u'&Salvar uma Cópia\tCTRL+SHIFT+S')
        self.menu1.Append(4009, u'&Sair\tCTRL+Q')
        self.menu2 = wx.Menu()
        self.menu2.Append(4101, u'&Copiar\tCTRL+C')
        self.menu2.Append(4102, u'&Recortar\tCTRL+X')
        self.menu2.Append(4103, u'&Colar\tCTRL+V')
        self.menu2.Append(4104, u'&Apagar')
        self.menu2.AppendSeparator()
        self.menu2.Append(4105, u'&Selecionar Tudo\tCTRL+A')
        self.menu = wx.MenuBar()
        self.menu.Append(self.menu1, u'Arquivos')
        self.menu.Append(self.menu2, u'Ferramentas')
        self.SetMenuBar(self.menu)
        self.bar = wx.ToolBar(self, size = (500,50))
        self.bar.AddSimpleTool(4501, wx.Bitmap(current_dir + '\\data\\pics\\Save.png', wx.BITMAP_TYPE_PNG), u'Salvar', '')
        self.bar.AddSeparator()
        self.bar.AddSimpleTool(4502, wx.Bitmap(current_dir + '\\data\\pics\\Copy.png', wx.BITMAP_TYPE_PNG), u'Copiar', '')
        self.bar.AddSimpleTool(4503, wx.Bitmap(current_dir + '\\data\\pics\\Cut.png', wx.BITMAP_TYPE_PNG), u'Recortar', '')
        self.bar.AddSimpleTool(4504, wx.Bitmap(current_dir + '\\data\\pics\\Paste.png', wx.BITMAP_TYPE_PNG), u'Colar', '')
        self.bar.AddSimpleTool(4505, wx.Bitmap(current_dir + '\\data\\pics\\Trash.png', wx.BITMAP_TYPE_PNG), u'Apagar', '')
        self.bar.AddSeparator()
        self.bar.AddSimpleTool(4509, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u'Sair', '')
        self.box = wx.TextCtrl(self, -1, pos = (10,60), size = (400,300), style = wx.TE_MULTILINE)
        self.Bind(wx.EVT_MENU, self.saver, id=4001)
        self.Bind(wx.EVT_MENU, self.saver_c, id=4002)
        self.Bind(wx.EVT_MENU, self.closer, id=4009)
        self.Bind(wx.EVT_MENU, self.copier, id=4101)
        self.Bind(wx.EVT_MENU, self.cuter, id=4102)
        self.Bind(wx.EVT_MENU, self.paster, id=4103)
        self.Bind(wx.EVT_MENU, self.eraser, id=4104)
        self.Bind(wx.EVT_MENU, self.select, id=4105)
        self.Bind(wx.EVT_TOOL, self.saver, id=4501)
        self.Bind(wx.EVT_TOOL, self.copier, id=4502)
        self.Bind(wx.EVT_TOOL, self.cuter, id=4503)
        self.Bind(wx.EVT_TOOL, self.paster, id=4504)
        self.Bind(wx.EVT_TOOL, self.eraser, id=4505)
        self.Bind(wx.EVT_TOOL, self.closer, id=4509)
        hsi = wx.BoxSizer(wx.VERTICAL)
        hsi.Add(self.bar, 0, wx.EXPAND)
        hsi.Add(self.box, 1, wx.EXPAND)
        self.box.SetPosition(wx.Point(30,60))
        vsi = wx.BoxSizer(wx.HORIZONTAL)
        vsi.Add(self.bar, 1, wx.EXPAND)
        self.SetSizer(vsi)
        self.SetSizer(hsi)
        self.bar.Realize()
        self.sts = self.CreateStatusBar()
        self.Show()

    def saver(self, event):
        try:
            if type(self.GetParent()) is resumo:
                self.box.SaveFile('saves/%s_obs.txt' %self.month)
                self.sts.SetStatusText(u'Observação salva com sucesso')
                time.sleep(1)
                self.sts.SetStatusText('')
        except:
            self.sts.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
            time.sleep(2)
            self.sts.SetStatusText('')

    def saver_c(self, event):
        try:
            loc = wx.FileDialog(self, 'Salvar em', os.getcwd(), self.month + '_obs.txt', '*.*', wx.FD_SAVE)
            loc.ShowModal()
            loc.Destroy()
            self.box.SaveFile(loc.GetPath())
            self.sts.SetStatusText(u'Observação salva com sucesso em %s' %loc.GetPath())
            time.sleep(1)
            self.sts.SetStatusText('')
        except:
            self.sts.SetStatusText(u'ERRO - Não foi possível salvar o arquivo')
            time.sleep(2)
            self.sts.SetStatusText('')
    def copier(self, event):
        self.box.Copy()
    def cuter(self, event):
        self.box.Cut()
    def paster(self, event):
        self.box.Paste()
    def select(self, event):
        self.box.SelectAll()
    def eraser(self, event):
        p = self.box.GetSelection()
        self.box.Remove(p[0],p[1])
    def closer(self, event):
        self.Close()


class sheet_box(wx.Frame):
    def __init__(self, parent, title=u'Tabelas', mode=1, month=None):
        wx.Frame.__init__(self, parent, -1, title, size = (970,600))
        self.month = month
        self.parent = parent
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(general_icon)
        box = wx.BoxSizer(wx.VERTICAL)
        note = wx.Notebook(self, style=wx.LEFT)
        if mode==1:
            self.main1 = sheet_(note, 'won')
            self.main2 = sheet_(note, 'loss')
            self.main3 = sheet_(note, 'prod')
            self.main4 = sheet_(note, 'was')
        elif mode==2:
            self.main2 = sheet_(note, 'loss')
            self.main3 = sheet_(note, 'prod')
            self.main4 = sheet_(note, 'was')
            self.main1 = sheet_(note, 'won')
        elif mode==3:
            self.main3 = sheet_(note, 'prod')
            self.main4 = sheet_(note, 'was')
            self.main1 = sheet_(note, 'won')
            self.main2 = sheet_(note, 'loss')
        elif mode==4:
            self.main4 = sheet_(note, 'was')
            self.main1 = sheet_(note, 'won')
            self.main2 = sheet_(note, 'loss')
            self.main3 = sheet_(note, 'prod')
        note.AddPage(self.main1, u'Vendas')
        note.AddPage(self.main2, u'Gastos')
        note.AddPage(self.main3, u'Produtos')
        note.AddPage(self.main4, u'Desperdícios')
        exiter = GenBitmapTextButton(self, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png', wx.BITMAP_TYPE_PNG), u'Sair', pos = (600,-1), style = wx.SIMPLE_BORDER)
        exiter.Bind(wx.EVT_BUTTON, self.closer)
        box.Add(note, 1, wx.EXPAND|wx.ALL, 5)
        box.Add(exiter, 0, wx.ALL|wx.ALIGN_RIGHT, 15)
        self.SetSizer(box)
        note.SetSelection(mode-1)

        self.Centre()
        self.Show()

    def closer(self, event):
        self.Close()


class sheet_(wx.gizmos.TreeListCtrl):
    def __init__(self, parent, content):
        wx.gizmos.TreeListCtrl.__init__(self, parent, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT)
        self.content = content
        self.parent = parent.GetParent()
        prepaire = threading.Thread(target=self.filler)
        prepaire.daemon = True
        prepaire.start()
        self.Show()

    def filler(self):
        month = self.parent.month
        if self.content is 'prod':
            plist = {}
            for root, dirs, files in os.walk('saves'):
                if root is 'saves':
                    for i in files:
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(current_dir + '\\saves\\' + i)
                            for a in s['sales']:
                                for x in range(0, len(s['sales'][a]['descriptions'])):
                                    key = s['sales'][a]['descriptions'][x] + '\\_/' + str(s['sales'][a]['unit_prices'][x])
                                    if key in plist:
                                        plist[key][0]+=s['sales'][a]['amounts'][x]
                                        plist[key][1]+=s['sales'][a]['prices'][x]
                                        plist[key][2]+=1
                                    else:
                                        plist[key] = [s['sales'][a]['amounts'][x], s['sales'][a]['prices'][x], 1]
            self.AddColumn(u'Produto', 300)
            self.AddColumn(u'Preço Unitário', 100)
            self.AddColumn(u'Quantidade vendida', 150)
            self.AddColumn(u'Quantidade de vezes vendido', 200)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Produtos Vendidos em %s' %date_reverse(month).replace('-','/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a=0.0
            b=0
            for i in plist:
                e = i.split('\\_/')
                item = self.AppendItem(root, e[0])
                self.SetItemText(item, 'R$ ' + good_show('money', e[1]), 1)
                self.SetItemText(item, str(plist[i][0]), 2)
                self.SetItemText(item, str(plist[i][2]), 3)
                self.SetItemText(item, 'R$ ' + good_show('money', str(plist[i][1])), 4)
                a += plist[i][1]
                b += plist[i][0]
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'won':
            wlist = []
            for root, dirs, files in os.walk('saves'):
                if root is 'saves':
                    for i in files:
                        if i[:7] == month and len(i) is 11:
                            s = shelve.open(current_dir + '\\saves\\' + i)
                            for a in s['winning']:
                                wlist = [[date_reverse(month), date_reverse(s['winning'][a]['date']).replace('-','/'), s['winning'][a]['value'], '-------', s['winning'][a]['description']]] + wlist
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(current_dir + '\\saves\\' + i)
                            for a in s['sales']:
                                loo = []
                                for x in range(0, len(s['sales'][a]['descriptions'])):
                                    loo.append([s['sales'][a]['descriptions'][x], str(s['sales'][a]['amounts'][x]), str(s['sales'][a]['prices'][x])])
                                wlist.append([date_reverse(i[:10]), s['sales'][a]['time'], s['sales'][a]['value'], s['sales'][a]['payment'], loo])
            self.AddColumn(u'Data/Horário', 250)
            self.AddColumn(u'Forma de Pagamento', 150)
            self.AddColumn(u'Descrição', 250)
            self.AddColumn(u'Quantidade', 100)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Ganhos de %s' %date_reverse(month).replace('-','/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a=0.0
            b=0
            days = {}
            sat = week_end(month)
            weeks = {}
            for i in range(0, len(wlist)):
                for pol in sat:
                    if pol>=int(wlist[i][0][:2]):
                        k = sat.index(pol)+1
                        break
                if k not in weeks and type(wlist[i][4]) is list:
                    we = self.AppendItem(root, u'%i° Semana'%k)
                    self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                    weeks[k] = [we,0.0,0]
                if wlist[i][0] not in days:
                    if type(wlist[i][4]) is list:
                        item = self.AppendItem(weeks[k][0], wlist[i][0].replace('-','/'))
                    else:
                        item = self.AppendItem(root, wlist[i][0].replace('-','/'))
                    self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                    days[wlist[i][0]] = [item, 0.0,0]
                boss = days[wlist[i][0]][0]
                if type(wlist[i][4]) is list:
                    x = '-----------'
                    y = str(len(wlist[i][4]))
                    weeks[k][1] += wlist[i][2]
                    weeks[k][2] += 1
                else:
                    x = wlist[i][4]
                    y = '--'
                father = self.AppendItem(boss, wlist[i][1])
                self.SetItemFont(father, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.SetItemText(father, wlist[i][3], 1)
                self.SetItemText(father, x, 2)
                self.SetItemText(father, y, 3)
                self.SetItemText(father, 'R$ ' + good_show('money', str(wlist[i][2])), 4)
                b += 1
                a += wlist[i][2]
                days[wlist[i][0]][1] += wlist[i][2]
                days[wlist[i][0]][2] += 1
                if type(wlist[i][4]) is list:
                    for z in wlist[i][4]:
                        kid = self.AppendItem(father, '-------')
                        self.SetItemText(kid, '-------', 1)
                        self.SetItemText(kid, z[0], 2)
                        self.SetItemText(kid, z[1], 3)
                        self.SetItemText(kid, 'R$ ' + good_show('money', str(z[2])), 4)
            for j in weeks:
                self.SetItemText(weeks[j][0], str(weeks[j][2]), 3)
                self.SetItemText(weeks[j][0], 'R$ ' + good_show('money', weeks[j][1]), 4)
                self.SortChildren(weeks[j][0])
            for j in days:
                self.SetItemText(days[j][0], str(days[j][2]), 3)
                self.SetItemText(days[j][0], 'R$ ' + good_show('money', days[j][1]), 4)
                self.SortChildren(days[j][0])
            self.SetItemText(root, str(b), 3)
            self.SetItemText(root, 'R$ ' + good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'loss':
            llist = []
            for root, dirs, files in os.walk('saves'):
                if root is 'saves':
                    for i in files:
                        if i[:7] == month and len(i) is 11:
                            s = shelve.open(current_dir + '\\saves\\' + i)
                            for a in s['spent']:
                                llist.append([date_reverse(i[:7]).replace('-','/'), s['spent'][a]['time'], s['spent'][a]['value'], s['spent'][a]['description']])
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(current_dir + '\\saves\\'+i)
                            for a in s['spent']:
                                llist.append([date_reverse(i[:10]).replace('-','/'), s['spent'][a]['time'], s['spent'][a]['value'], s['spent'][a]['description']])
            self.AddColumn(u'Data/Horário', 250)
            self.AddColumn(u'Descrição', 400)
            self.AddColumn(u'Quantidade', 100)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Gastos de %s' %date_reverse(month).replace('-','/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a=0.0
            b=0
            days = {}
            sat = week_end(month)
            weeks = {}
            for i in range(0, len(llist)):
                for pol in sat:
                    if pol>=int(llist[i][0][:2]):
                        k = sat.index(pol)+1
                        break
                if k not in weeks and len(llist[i][0])==10:
                    we = self.AppendItem(root, u'%i° Semana'%k)
                    self.SetItemFont(we, wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
                    weeks[k] = [we,0.0,0]
                if llist[i][0] not in days:
                    if len(llist[i][0])==10:
                        item = self.AppendItem(weeks[k][0], llist[i][0].replace('-','/'))
                    else:
                        item = self.AppendItem(root, llist[i][0].replace('-','/'))
                    self.SetItemFont(item, wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
                    days[llist[i][0]] = [item, 0.0,0]
                boss = days[llist[i][0]][0]
                father = self.AppendItem(boss, llist[i][1])
                self.SetItemText(father, llist[i][3], 1)
                self.SetItemText(father, 'R$ ' + good_show('money', str(llist[i][2])), 3)
                b += 1
                a += llist[i][2]
                days[llist[i][0]][2] += 1
                days[llist[i][0]][1] += llist[i][2]
                if len(llist[i][0])==10:
                    weeks[k][1] += llist[i][2]
                    weeks[k][2] += 1
            for key in days:
                self.SetItemText(days[key][0], str(days[key][2]), 2)
                self.SetItemText(days[key][0], 'R$ ' + good_show('money', days[key][1]), 3)
                self.SortChildren(days[key][0])
            for j in weeks:
                self.SetItemText(weeks[j][0], str(weeks[j][2]), 2)
                self.SetItemText(weeks[j][0], 'R$ ' + good_show('money', weeks[j][1]), 3)
                self.SortChildren(weeks[j][0])
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + good_show('money', a), 3)
            self.Expand(root)
            self.SortChildren(root)
        elif self.content is 'was':
            walist = {}
            for root, dirs, files in os.walk('saves'):
                if root is 'saves':
                    for i in files:
                        if i[:7] == month and len(i) is 14:
                            s = shelve.open(current_dir + '\\saves\\' + i)
                            for a in s['wastes']:
                                key = s['wastes'][a]['description'] + '\\_/' + str(s['wastes'][a]['unit_price'])
                                if key in walist:
                                    walist[key][0]+=s['wastes'][a]['amount']
                                    walist[key][1]+=s['wastes'][a]['value']
                                    walist[key][2]+=1
                                else:
                                    walist[key] = [s['wastes'][a]['amount'], s['wastes'][a]['value'], 1]
            self.AddColumn(u'Descrição', 300)
            self.AddColumn(u'Preço Unitário',150)
            self.AddColumn(u'Quantidade',100)
            self.AddColumn(u'Quantidade de vezes',200)
            self.AddColumn(u'Valor', 150)
            root = self.AddRoot(u'Desperdícios de %s' %date_reverse(month).replace('-','/'))
            self.SetItemFont(root, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            a=0.0
            b=0
            for i in walist:
                e = i.split('\\_/')
                item = self.AppendItem(root, e[0])
                self.SetItemText(item, 'R$ ' + good_show('money', e[1]), 1)
                self.SetItemText(item, str(walist[i][0]), 2)
                self.SetItemText(item, str(walist[i][2]), 3)
                self.SetItemText(item, 'R$ ' + good_show('money', str(walist[i][1])), 4)
                a+=walist[i][1]
                b+=walist[i][0]
            self.SetItemText(root, str(b), 2)
            self.SetItemText(root, 'R$ ' + good_show('money', a), 4)
            self.Expand(root)
            self.SortChildren(root)


class delivery(wx.Frame):
    def __init__(self, parent ,frame_id=-1, title=u'Sistema de entregas'):
        wx.Frame.__init__(self, parent,frame_id, title, size=(900, 430), pos = (250, 100), style =wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(general_icon)
        self.pilot = wx.Panel(self, -1, size=(730, 380), pos=(10, 10), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.pdel = wx.ListCtrl(self.pilot, -1, pos=(10, 10), size=(710, 360), style = wx.LC_REPORT | wx.SIMPLE_BORDER | wx.LC_VRULES|wx.LC_HRULES)
        self.pdel.InsertColumn(0, u"Data", width=120)
        self.pdel.InsertColumn(1, u"Horário", width=120)
        self.pdel.InsertColumn(2, u"Endereço", width=300)
        self.pdel.InsertColumn(3, u"Para", width=190)
        self.final = wx.Panel(self, -1, size=(140, 380), pos = (750,10), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        tell = wx.Button(self.final, -1, u'Mostrar mais', pos = (20,150), size = (100,30))
        tell.Bind(wx.EVT_BUTTON, self.win2_)
        wx.StaticText(self.final, -1, u"Entregas entre:", pos = (5,10))
        wx.StaticText(self.final, -1, "e:", pos = (5,70))
        self.finalb = wx.Panel(self.final, pos = (10,220), size = (120,120), style = wx.SIMPLE_BORDER)
        ready = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Check.png'), u"Concluída", pos = (0,0), size = (120,40))
        ready.Bind(wx.EVT_BUTTON, self.ready)
        up = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Reset.png'), u"Atualizar", pos = (0,40), size = (120,40))
        up.Bind(wx.EVT_BUTTON, self.gogogo)
        down = GenBitmapTextButton(self.finalb, -1, wx.Bitmap(current_dir + '\\data\\pics\\Exit.png'), u'Sair', pos = (0,80), size = (120,40))
        down.Bind(wx.EVT_BUTTON, self.closer)
        self.gogogo(1)
        self.Show()

    def win2_(self, event):
        red = self.pdel.GetFocusedItem()
        if red==-1:
            return
        avatar = self.pdel.GetItemText(red)
        earth = shelve.open(current_dir + '\\saves\\' + self.maresia[avatar][0] + '.txt')
        brown = earth['sales'][self.maresia[avatar][1]]['time']
        sell(self, mode=[(current_dir + "\\saves\\" + self.maresia[avatar][0] + '.txt'), self.maresia[avatar][1], brown], delmode=1)
        earth.close()

    def ready(self, event):
        red = self.pdel.GetFocusedItem()
        if red==-1:
            return
        date = self.pdel.GetItemText(red)
        tempo= self.pdel.GetItemText(red, 1)
        adr = self.pdel.GetItemText(red, 2)
        nam = self.pdel.GetItemText(red, 3)
        paco = shelve.open(current_dir + '\\saves\\deliverys.txt')
        for a in self.maresia:
            if date==self.maresia[a][1] and tempo==self.maresia[a][2] and adr==self.maresia[a][3] and nam==self.maresia[a][4]:
                tempo= str(datetime.now().hour) + ':' + str(datetime.now().minute)
                if paco[a][1]:
                    paco[a] = [date, False, tempo]
                else:
                    paco[a] = [date, True, tempo]
        paco.close()
        self.starter(event)

    def starter(self, event):
        self.pdel.DeleteAllItems()
        gas = shelve.open(current_dir + '\\saves\\deliverys.txt')
        e1 = self.alpha.GetValue()
        w1 = self.zetta.GetValue()
        earth = datetime_int(2,self.fall[self.son.index(e1)])
        water = datetime_int(2,self.fall[self.son.index(w1)])
        emax = max((earth,water))
        emin = min((earth,water))
        for i in gas:
            fire = datetime_int(2,self.maresia[i][1])
            if emin<=fire<=emax:
                tyr = self.pdel.Append((self.maresia[i][1], self.maresia[i][2], self.maresia[i][3], self.maresia[i][4]))
                if gas[i][1]: self.pdel.SetItemTextColour(tyr, '#ADADAD')
        gas.close()

    def gogogo(self, event):
        today1 = datetime_int(2, str(datetime.now().year) + '-' + good_show("o", str(datetime.now().month)) + '-' + good_show("o", str(datetime.now().day)))
        gas=shelve.open(current_dir + '\\saves\\deliverys.txt')
        self.maresia = {}
        for i in gas:
            key = gas[i][0]
            date1, time1 = i.split()
            air = shelve.open(current_dir + '\\saves\\' + date1 + '.txt')
            adr = s_acentos(str(air['sales'][key]['city']) + ' - ' + str(air['sales'][key]['adress']))
            rec = s_acentos(r_acentos(air['sales'][key]['receiver']))
            tempo = str(air['sales'][key]['hour'])
            date = str(air['sales'][key]['date'])
            if int(date_reverse(date.replace('/', '-')).replace('-', '')) < int(str(datetime.now().month) + good_show("o", str(datetime.now().day))):
                date = date + '/' + str(datetime.now().year+1)
            else:
                date = date + '/' + str(datetime.now().year)
            self.maresia[i] = [key, date, tempo, adr, rec]
            air.close()
        water = today1
        for i in gas:
            tempo= self.maresia[i][2]
            date = self.maresia[i][1]
            fire = datetime_int(2, date)
            if fire < today1:
                g = gas
                del g[i]
                gas = g
            elif fire > water:
                water = fire
        b = today1
        self.fall = []
        while b <= water:
            self.fall.append(datetime_int(3, b))
            b += 1
        self.fall.sort()
        self.gon = []
        self.son = []
        for i in self.fall:
            self.gon.append(i)
            nert = i[8:10] + '/' + i[5:7] + '/' + i[:4]
            self.son.append(nert)
        self.alpha = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 30), style=wx.CB_READONLY)
        self.alpha.Bind(wx.EVT_COMBOBOX, self.starter)
        self.alpha.SetValue(self.son[0])
        self.zetta = wx.ComboBox(self.final, -1, choices=self.son, size=(130, -1), pos=(5, 90), style=wx.CB_READONLY)
        self.zetta.Bind(wx.EVT_COMBOBOX, self.starter)
        self.zetta.SetValue(self.son[len(self.son)-1])
        gas.close()
        self.starter(event)

    def closer(self,event):
        self.Close()


class ask(wx.Dialog):
    def __init__(self, parent,frame_id, title, red, box):
        wx.Dialog.__init__(self, parent,frame_id, title, size = (400,180))
        self.red = red
        self.box = box
        self.SetBackgroundColour('#D6D6D6')
        if red==1:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar tudo?", pos = (50, 50))
        elif red==2:
            wx.StaticText(self, -1, u"Você tem certeza que deseja sair agora?", pos = (50, 50))
        elif red==3 and box==1:
            wx.StaticText(self, -1, u"Finalizar Venda?", pos = (50, 50))
        elif red==3 and box==2:
            wx.StaticText(self, -1, u"Finalizar registro de gasto?", pos = (50, 50))
        elif red==3 and box==5:
            wx.StaticText(self, -1, u"Finalizar registro de perda?", pos = (50, 50))
        elif red==3 and box==6:
            wx.StaticText(self, -1, u"Finalizar cadastro de cliente?", pos = (50, 50))
        elif red==3 and box==8:
            wx.StaticText(self, -1, u"Finalizar cadastro de produto?", pos = (50, 50))
        elif red==3 and box==11:
            wx.StaticText(self, -1, u"Finalizar registro de ganho?", pos = (50, 50))
        elif red==4 and box==3:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar esta venda?", pos=(50, 50))
        elif red==4 and box==3.5:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este gasto?", pos=(50, 50))
        elif red==4 and box==5:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este registro?", pos=(50, 50))
        elif red==4 and box==7:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este cliente?", pos=(50, 50))
        elif red==4 and box==9:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este produto?", pos=(50, 50))
        elif red==4 and box==11:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este ganho?", pos=(50, 50))
        elif red==4 and box==12:
            wx.StaticText(self, -1, u"Você tem certeza que deseja apagar este gasto?", pos=(50, 50))
        elif red==5 and box==4:
            wx.StaticText(self, -1, u"Você tem certeza que deseja restaurar esse registro?", pos=(50, 50))
        elif red==6 and box==6:
            wx.StaticText(self, -1, u"Você tem certeza que deseja desconectar essa venda?", pos=(50, 50))
        elif red==99:
            wx.StaticText(self, -1, u"Você tem certeza que deseja sair do programa?", pos=(50, 50))
        self.Centre()
        ok = wx.Button(self, -1, u"Sim", pos=(100, 100))
        ok.Bind(wx.EVT_BUTTON, self.cont)
        nok = wx.Button(self, -1, u"Não", pos=(200, 100))
        nok.Bind(wx.EVT_BUTTON, self.closer)
        self.ShowModal()

    def closer(self, event):
        self.Close()

    def cont(self, event):
        a = self.GetParent()
        self.Destroy()
        if self.red==1:
            a.clean()
        elif self.red==2:
            a.Close()
        elif self.red==3 and self.box==1:
            a.end_sell()
        elif self.red==3 and self.box==2:
            a.end()
        elif self.red==3 and self.box==5:
            a.end()
        elif self.red==3 and self.box==6:
            a.end()
        elif self.red==3 and self.box==8:
            a.end()
        elif self.red==3 and self.box==11:
            a.end()
        elif self.red==4 and self.box==3:
            a.remover(a.prods)
        elif self.red==4 and self.box==3.5:
            a.remover(a.expent)
        elif self.red==4 and self.box==4:
            a.remover(1)
        elif self.red==4 and self.box==5:
            a.remover(a.was)
        elif self.red==4 and self.box==7:
            a.del_entry(1)
        elif self.red==4 and self.box==9:
            a.del_entry(1)
        elif self.red==4 and self.box==11:
            a.remover(11)
        elif self.red==4 and self.box==12:
            a.remover(12)
        elif self.red==5 and self.box==4:
            a.remover(1)
        elif self.red==6 and self.box==6:
            a.unbinder()
        elif self.red==99:
            base_s.closer()


class confirmation(wx.Dialog):
    def __init__(self, parent,frame_id, title, blue):
        wx.Dialog.__init__(self, parent,frame_id, title, size=(400, 180))
        self.Centre()
        self.blue = blue
        if blue == 1:
            wx.StaticText(self, -1, u"Venda registrada com sucesso!\nRegistrar outra venda?", pos=(50, 50))
        elif blue == 2:
            wx.StaticText(self, -1, u"Gasto registrado com sucesso!\nRegistrar outro gasto?", pos=(50, 50))
        elif blue == 3:
            wx.StaticText(self, -1, u"Desperdício registrado com sucesso!\nRegistrar outro?", pos=(50, 50))
        elif blue == 4:
            wx.StaticText(self, -1, u"Cliente cadastrado com sucesso!\nCadatrar outro?", pos=(50, 50))
        elif blue == 5:
            wx.StaticText(self, -1, u"Produto cadastrado com sucesso!\nCadatrar outro?", pos=(50, 50))
        elif blue == 6:
            wx.StaticText(self, -1, u"Produtos registrados com sucesso!\nRegistrar outros?", pos=(50, 50))
        elif blue == 7:
            wx.StaticText(self, -1, u"Ganho registrado com sucesso!\nRegistrar outro?", pos=(50, 50))
        ok = wx.Button(self, -1, u"Sim", pos=(100, 100))
        ok.Bind(wx.EVT_BUTTON, self.closer)
        nok = wx.Button(self, -1, u"Não", pos=(200, 100))
        nok.Bind(wx.EVT_BUTTON, self.cont)
        self.SetBackgroundColour('#D6D6D6')
        a = parent
        if self.blue in [1, 2, 3] and type(a.GetParent()) is report:
            a.GetParent().run()
        elif self.blue == 4 and type(a.GetParent()) is clients:
            a.GetParent().power_on(1)
        elif self.blue in [5, 6] and type(a.GetParent()) is stock:
            a.GetParent().power_on(1)
        self.ShowModal()
        self.Destroy()

    def closer(self, event):
        self.Close()

    def cont(self, event):
        a = self.GetParent()
        a.Close()
        self.Close()


class warner(wx.Dialog):
    def __init__(self, parent,frame_id, title, red):
        wx.Dialog.__init__(self, parent,frame_id, title, size = (500,230))
        self.red = red
        self.SetBackgroundColour('#D6D6D6')
        if red[5] == 1:
            blur = u'Primeiro Aviso'
        elif red[5] == 2:
            blur = u'Segundo Aviso'
        elif red[5] == 3:
            blur = u'Aviso Final'
        tempo= str(datetime.now().hour) + ':' + str(datetime.now().minute)
        minor= datetime_int(1,red[0])-datetime_int(1,tempo)
        if minor>=0:
            y = u"%s! Falta menos de %s minutos para a entrega para o(a) Sr(a) %s\nem %s, a qual esta marcada para as %s." % (blur, str(min), red[2], red[1], red[0])
        else:
            y = u"%s! Passou-se %s minutos da hora da entrega para o(a) Sr(a) %s\nem %s, a qual estava marcada para as %s." % (blur, str(- min), red[2], red[1], red[0])
        wx.StaticText(self, -1, y, pos = (10, 50))
        self.Centre()
        ok = wx.Button(self, -1, u"Ver Mais", pos=(100, 150))
        ok.Bind(wx.EVT_BUTTON, self.more)
        nok = wx.Button(self, -1, u"OK", pos=(200, 150))
        nok.Bind(wx.EVT_BUTTON, self.closer)
        gray = wx.Button(self, -1, u"Entrega realizada", pos=(300, 150))
        gray.Bind(wx.EVT_BUTTON, self.ready)
        self.ShowModal()
        self.Destroy()

    def closer(self, event):
        self.Close()

    def more(self, event):
        earth = shelve.open(current_dir + '\\saves\\' + self.red[4] + '.txt')
        brown = earth['sales'][self.red[3]]['time']
        sell(self.GetParent(), mode=[(current_dir + "\\saves\\" + self.red[4] + '.txt'), self.red[3], brown], delmode=1)
        earth.close()

    def ready(self, event):
        buster = shelve.open(current_dir + '\\saves\\deliverys.txt')
        for i in buster:
            if buster[i][0]==self.red[3]:
                tempo= str(datetime.now().hour) + ':' + str(datetime.now().minute)
                buster[i] = [self.red[3], True, tempo]
        buster.close()
        self.Close()


class settings(wx.Frame):
    def __init__(self, parent,frame_id=-1, title=u'Configurações'):
        wx.Frame.__init__(self, parent,frame_id, title, size=(550,400), style=wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.Centre()
        self.SetBackgroundColour('#D6D6D6')
        self.SetIcon(general_icon)
        self.options = wx.Notebook(self, pos = (5,5), style=wx.LEFT)
        #--Geral
        #buscar atualizações
        general = wx.Panel(self.options)
        self.OnStart()
        self.update = wx.Panel(general, pos = (10,20), size = (515, 150), style = wx.SIMPLE_BORDER)
        wx.StaticText(self.update, -1, u'Atualizações', pos = (210,5))
        self.autoUpdate = wx.CheckBox(self.update, -1, u'Buscar atualizações automaticamente?', (10,50))
        self.autoUpdate.SetValue(self.prefAutoUpdate)
        #--Security
        #escolher quais lugares precisam de senha
        security = wx.Panel(self.options)
        self.password = wx.Panel(security, pos = (10,20), size = (515, 150), style = wx.SIMPLE_BORDER)
        wx.StaticText(self.password, -1, u'Alteração de senha', pos = (210,5))
        wx.StaticText(self.password, -1, u'Senha Atual:', pos = (100,25))
        wx.StaticText(self.password, -1, u'Nova Senha:', pos = (300,25))
        wx.StaticText(self.password, -1, u'Repita a nova senha:', pos = (300,80))
        self.oldPass = wx.TextCtrl(self.password, size = (150,30), pos = (100,45), style = wx.TE_PASSWORD)
        self.newPass1 = wx.TextCtrl(self.password, size = (150,30), pos = (300,45), style = wx.TE_PASSWORD)
        self.newPass2 = wx.TextCtrl(self.password, size = (150,30), pos = (300,100), style = wx.TE_PASSWORD)
        self.passChange = wx.Button(self.password, -1, u'Alterar Senha', pos = (100,90))
        self.passChangeText = wx.TextCtrl(self.password, -1,size = (150,25), pos = (100,125), style = wx.NO_BORDER|wx.TE_READONLY)
        self.passChangeText.SetBackgroundColour('#D6D6D6')
        self.passChange.Bind(wx.EVT_BUTTON, self.OnPassChange)
        #Custom
        #logo da empresa, backgrounds
        custom = wx.Panel(self.options)

        self.options.AddPage(general, u'Geral')
        self.options.AddPage(security, u'Segurança')
        self.options.AddPage(custom, u'Customizações')

        wx.EVT_PAINT(self.password, self.OnPaint)
        self.Show()

    def OnPaint(self, event):
        lok = wx.Bitmap(current_dir + '\\data\\pics\\Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self.password).DrawBitmap(lok, 0, 30)

    def OnStart(self):
        if not os.path.exists('preferences'):
            os.mkdir('preferences')
        generalFile = shelve.open(current_dir + '\\preferences\\general.txt')
        if 'Auto Update' not in generalFile:
            generalFile['Auto Update'] = True
        self.prefAutoUpdate = generalFile['Auto Update']
        generalFile.close()

    def OnPassChange(self, event):
        if self.newPass1x.GetValue()!=self.newPass2.GetValue():
            self.passChangeText.SetValue(u'As senhas são diferentes!')
            self.passChangeText.SetForegroundColour('red')
            return
        if password_check(self.oldPass.GetValue()):
            hex_pass = hashlib.sha256(self.newPass1.GetValue()).hexdigest()
            pickle.dump(hex_pass, open('preferences/accounts.p', 'wb'))
            self.passChangeText.SetValue(u'Senha alterada com sucesso!')
            self.passChangeText.SetForegroundColour('#009900')
            self.oldPass.Clear()
            self.newPass1.Clear()
            self.newPass2.Clear()
            return
        else:
            self.passChangeText.SetValue(u'Senha Incorreta!')
            self.passChangeText.SetForegroundColour('red')
            return


class pass_box(wx.Dialog):
    def __init__(self, parent,frame_id=-1, title=u'Acesso Restrito'):
        wx.Dialog.__init__(self, parent,frame_id, title, size=(400,180))
        self.parent = parent
        self.Centre()
        self.SetIcon(general_icon)
        wx.EVT_PAINT(self, self.OnPaint)
        wx.StaticText(self, -1, u'Digíte a senha:', pos = (100,25)).SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.password = wx.TextCtrl(self, -1, pos = (100,50), size = (250,30), style = wx.TE_PASSWORD)
        cancel = wx.Button(self, -1, u'Cancelar', pos = (120,90))
        contin = wx.Button(self, -1, u'Continuar', pos = (250,90))
        cancel.Bind(wx.EVT_BUTTON, self.exit)
        contin.Bind(wx.EVT_BUTTON, self.go_on)
        self.denied_message = wx.StaticText(self, -1, u'Acesso Negado!', pos = (170,130))
        self.denied_message.SetForegroundColour('red')
        self.denied_message.Hide()
        self.ShowModal()
        self.Destroy()

    def OnPaint(self, event):
        lok = wx.Bitmap(current_dir + '\\data\\pics\\Lock.png', wx.BITMAP_TYPE_PNG)
        wx.PaintDC(self).DrawBitmap(lok, 0, 30)

    def exit(self, event):
        self.Destroy()

    def go_on(self, event):
        key = self.password.GetValue()
        if password_check(key):
            self.parent.win11(True)
            self.Destroy()
        else:
            self.denied_message.Show()


def good_show(type, tex):
    if type=="hour":
        xet = float((tex).replace(":", "."))
        if len(tex)==2 or (xet<10 and xet*10==int(xet*10)):
            tex = "0" + tex + "0"
            return tex
        elif xet<10:
            tex = "0" + tex
            return tex
        elif xet*10 == int(xet*10):
            tex = tex + "0"
            return tex
        else:
            return tex
    elif type=="money":
        tex = str(tex)
        tex = tex.replace('.', ',')
        x = len(tex.split(',')[1])
        if x==1:
            tex = tex + "0"
        elif x>2:
            tex = tex[:-x+2]
        return tex
    elif type=="date":
        xet = float((tex).replace("/", "."))
        if len(tex)==2 or (xet<10 and xet*10==int(xet*10)):
            tex = "0" + tex + "0"
            return tex
        elif xet<10:
            tex = "0" + tex
            return tex
        elif xet*10 == int(xet*10):
            tex = tex + "0"
            return tex
        else:
            return tex
    elif type=="o":
        if len(tex)==1:
            tex = "0" + tex
            return tex
        elif len(tex)==0:
            tex = "00"
            return tex
        else:
            return tex


def datetime_int(type, value):
    if type==1:
        dex = int(value.replace(':','')[:4])
        agi = int(dex/100)
        return (agi*60 + dex%100)
    elif type==2:
        stats = value.replace('/','-').split('-')
        if len(stats[0])==4:
            agi = int(stats[0])
            dex = int(stats[1])
            vit = int(stats[2])
        else:
            agi = int(stats[2])
            dex = int(stats[1])
            vit = int(stats[0])
        atk = [0,31,59,90,120,151,181,212,243,273,304,334]
        if not agi%4:
            for r in range(2,12):
                atk[r]+=1
        return int((agi-1)*365.25 + atk[dex-1] + vit)
    elif type==3:
        value+=1
        agi = int(value//365.25 + 1)
        luk = int(value%365.25)
        atk = [0,31,59,90,120,151,181,212,243,273,304,334]
        matk = [31,28,31,30,31,30,31,31,30,31,30,31]
        if not agi%4:
            for r in range(2,12):
                atk[r]+=1
            matk[1]=29
        for i in range(12):
            if luk-atk[i]<=matk[i]:
                dex = i + 1
                vit = luk-atk[i]
                break
        return '%s-%s-%s' %(str(agi), good_show('o', str(dex)), good_show('o', str(vit)))


def date_reverse(text):
    text_ = text.replace('/','-').split('-')
    text_.reverse()
    return '-'.join(text_)


def week_end(month):
    ds = month.replace('/','-').split('-')
    if len(ds[1])==4:
        ds.reverse()
    ds[0] = int(ds[0])
    ds[1] = int(ds[1])
    saturdays = []
    matk = [31,28,31,30,31,30,31,31,30,31,30,31]
    if not ds[0]%4:
        matk[1]=29
    for i in range(matk[ds[1]-1]):
        if calendar.weekday(ds[0], ds[1], i+1)==5:
            saturdays.append(i+1)
    if matk[ds[1]-1] not in saturdays: saturdays.append(matk[ds[1]-1])
    return saturdays


def s_acentos(text):
    return normalize('NFKD', text.decode('utf-8')).encode('ASCII', 'ignore')


def r_acentos(text):
    return normalize('NFKD', text).encode('utf-8', 'ignore')


def resize_bitmap(pic, x, y):
    seal = wx.ImageFromBitmap(pic)
    seal = seal.Scale(x, y, wx.IMAGE_QUALITY_HIGH)
    return wx.BitmapFromImage(seal)


def check_money(event):
    num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    dex = [8, 127, 314, 316, 9]
    pro = event.GetKeyCode()
    box = event.GetEventObject()
    rhyme = box.GetValue().replace(",", ".").replace('R$ ', '')
    try:
        if pro == dex[2] or pro == dex[3] or pro == dex[4]:
            event.Skip()
        elif pro == dex[0] or pro == dex[1]:
            wer = (float(rhyme)*100 - ((float(rhyme)*100)%(10)))/1000
            box.SetValue('R$ ' + good_show("money", str(wer).replace(".", ",")))
        elif pro in num:
            if len(box.GetValue())==14:
                box.SetValue('R$ 0,00')
                return
            wes = float(rhyme)*10 + float(chr(pro))/100
            box.SetValue('R$ ' + good_show("money", str(wes).replace(".", ",")))
    except RuntimeError, e:
        box.SetValue("R$ 0,00")


def dmy(event):
    try:
        box = event.GetEventObject()
        value = event.GetKeyCode()
        num = [48,49,50,51,52,53,54,55,56,57,8,127,314,316,9]
        if value in num[:10]:
            text = box.GetValue()
            text2 = text.replace('/','').replace('_','')
            text2 = text2 + str(chr(value))
            while len(text2)<8:
                text2 = text2 + '_'
            text = text2[:2] + '/' + text2[2:4] + '/' + text2[4:8]
            box.SetValue(text)
        elif value in num[10:12]:
            text = box.GetValue()
            text2 = text.replace('/','').replace('_','')
            text2 = text2[:-1]
            while len(text2)<8:
                text2 = text2 + '_'
            text = text2[:2] + '/' + text2[2:4] + '/' + text2[4:]
            box.SetValue(text)
        elif value in num[12:]:
            event.Skip()
    except:
        event.GetEventObject().SetValue('__/__/____')


def telcode(event):
    box = event.GetEventObject()
    try:
        value = event.GetKeyCode()
        num = [48,49,50,51,52,53,54,55,56,57,8,127,314,316,9]
        if value in num[:10]:
            text = box.GetValue()
            text2 = text.replace('-','').replace('(','').replace(')','')
            text2 = text2 + str(chr(value))
            if len(text2)>11: text2 = text2[:11]
            text3 = text2
            if len(text2)>4: text3 = text2[:-4] + '-' + text2[-4:]
            if len(text2)>9: text3 = '(' + text3[:2] + ')' + text3[2:]
            box.SetValue(text3)
        elif value in num[10:12]:
            text = box.GetValue()
            text2 = text.replace('-','').replace('(','').replace(')','')
            text2 = text2[:-1]
            if len(text2)>11:
                text2 = text2[:11]
            text3 = text2
            if len(text2)>4: text3 = text2[:-4] + '-' + text2[-4:]
            if len(text2)>9: text3 = '(' + text3[:2] + ')' + text3[2:]
            box.SetValue(text3)
        elif value in num[12:]:
            event.Skip()
    except:
        box.SetValue('')


def cpfcode(event):
    box = event.GetEventObject()
    try:
        value = event.GetKeyCode()
        num = [48,49,50,51,52,53,54,55,56,57,8,127,314,316,9]
        if value in num[:10]:
            text = box.GetValue()
            text2 = text.replace('-','').replace('.','')
            text2 = text2 + str(chr(value))
            if len(text2)>11: text2 = text2[:11]
            text3 = text2
            if len(text2)>3: text3 = text2[:3] + '.' + text2[3:]
            if len(text2)>6: text3 = text3[:7] + '.' + text3[7:]
            if len(text2)>9: text3 = text3[:11] + '-' + text3[11:]
            box.SetValue(text3)
        elif value in num[10:12]:
            text = box.GetValue()
            text2 = text.replace('-','').replace('.','')
            text2 = text2[:-1]
            if len(text2)>11:
                text2 = text2[:11]
            text3 = text2
            if len(text2)>3: text3 = text2[:3] + '.' + text2[3:]
            if len(text2)>6: text3 = text3[:7] + '.' + text2[7:]
            if len(text2)>9: text3 = text3[:11] + '-' + text3[11:]
            box.SetValue(text3)
        elif value in num[12:]:
            event.Skip()
    except:
        box.SetValue('')


def no_char(event):
    pass


def password_check(password):
    if not os.path.exists(current_dir + '\\preferences\\accounts.p'):
        pickle.dump(masterPassword, open(current_dir + '\\preferences\\accounts.p', 'wb'))
        message_dialog = wx.MessageDialog(None, -1, u'O arquivo com a senha do programa foi apagado. Senha resetada para a padrão!', u'IMPORTANTE', style = wx.OK|wx.ICON_EXCLAMATION)
        message_dialog.ShowModal()
        message_dialog.Destroy()
    hex_pass = hashlib.sha256(password).hexdigest()
    adm = pickle.load(open(current_dir + '\\preferences\\accounts.p', 'rb'))
    if adm==hex_pass or hex_pass==masterPassword:
        return True
    else:
        return False

brstates = ['AL', 'AM', 'PI', 'SP', 'SC', 'RJ', 'DF',
            'GO', 'RS', 'MT', 'MS', 'MG', 'PR', 'PA',
            'RR', 'AP', 'PE', 'TO', 'RN', 'PB', 'CE',
            'MA', 'AC', 'SE', 'BA', 'RO', 'ES', '--']
brstates.sort()
week = [u'Segunda', u'Terça', u'Quarta', u'Quinta', u'Sexta', u'Sábado', u'Domingo']
masterPassword = '5600715f42bf51c40dc330d750cd996f58fead4ddea56466ce7498d17801b3a5'
current_dir = os.path.realpath(os.curdir)



prog = wx.App()
general_icon = wx.Icon(current_dir + "\\bronze.ico", wx.BITMAP_TYPE_ICO)
base_s = base()
prog.MainLoop()

'''
###TOP PRIORITY###
criar venda programada
na venda programada, se for entrega, já deixar a entrega programada
salvar para que =m será entregue como cliente também

Otimizar a função serch do clientes e do stocks (para de rodar o hd e armazenar em um outro vetor o que está sendo visto no search)


categoria no relatório de produtos
fechamento e resumo não conseguem comparar a forma de pagamento se escrito a mão
v2.0
fazer instalador
recuperação de backup,
salvar tudo  ou os backups no drop ou parecido
'''
