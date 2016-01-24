#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import calendar
import hashlib
import pickle
import platform
import shutil
from unicodedata import normalize

import wx
import wx.gizmos

__author__ = 'Julio'

"""
data conversion functions
"""


def good_show(types, tex):
    if types == "hour":
        xet = float(tex.replace(":", "."))
        if len(tex) == 2 or (xet < 10 and xet * 10 == int(xet * 10)):
            tex = "0" + tex + "0"
            return tex
        elif xet < 10:
            tex = "0" + tex
            return tex
        elif xet * 10 == int(xet * 10):
            tex += "0"
            return tex
        else:
            return tex
    elif types == "money":
        tex = str(tex)
        tex = tex.replace('.', ',')
        x = len(tex.split(',')[1])
        if x == 1:
            tex += "0"
        elif x > 2:
            tex = tex[:-x + 2]
        return tex
    elif types == "date":
        xet = float(tex.replace("/", "."))
        if len(tex) == 2 or (xet < 10 and xet * 10 == int(xet * 10)):
            tex = "0" + tex + "0"
            return tex
        elif xet < 10:
            tex = "0" + tex
            return tex
        elif xet * 10 == int(xet * 10):
            tex += "0"
            return tex
        else:
            return tex
    elif types == "o":
        if len(tex) == 1:
            tex = "0" + tex
            return tex
        elif len(tex) == 0:
            tex = "00"
            return tex
        else:
            return tex


def hour2int(value):
    """
    Gera um numero a partir de um horario
    :param value: string com um horario no formato hh:mm
    :return: int
    """
    time = int(value.replace(':', '')[:4])
    hours = int(time / 100)
    return hours * 60 + time % 100


def date2int(value):
    """
    Gera um numero a partir de uma data
    :param value: string com uma data no formato dd-mm-aaaa, aaaa-mm-dd, dd/mm/aaaa ou aaaa/mm/dd
    :return: int
    """
    stats = value.replace('/', '-').split('-')
    if len(stats[0]) == 4:
        year = int(stats[0])
        month = int(stats[1])
        day = int(stats[2])
    else:
        year = int(stats[2])
        month = int(stats[1])
        day = int(stats[0])
    days_until_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if not year % 4:
        for r in range(2, 12):
            days_until_month[r] += 1
    return int((year - 1) * 365.25 + days_until_month[month - 1] + day)


def int2date(value):
    """
    Gera uma data a partir de um numero
    :param value: int com o numero de dias
    :return: string com a data no formato aaaa-mm-dd
    """
    value += 1
    year = int(value // 365.25 + 1)
    aux = int(value % 365.25)
    month = 0
    day = 0
    days_until_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    days_at_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # correcao para anos bissextos
    if not year % 4:
        for r in range(2, 12):
            days_until_month[r] += 1
        days_at_month[1] = 29

    # descobre o mes e dia
    for i in range(12):
        if aux - days_until_month[i] <= days_at_month[i]:
            month = i + 1
            day = aux - days_until_month[i]
            break
    return '%s-%s-%s' % (str(year), good_show('o', str(month)), good_show('o', str(day)))


def date_reverse(text):
    """
    troca uma data de aaaa-mm-dd para dd-mm-aaaa e vice versa
    :param text: string com uma data no formato aaaa-mm-dd ou dd-mm-aaaa
    :return: string com o formato invertido
    """
    text_ = text.replace('/', '-').split('-')
    text_.reverse()
    return '-'.join(text_)


def format_date_internal(date):
    date = date.replace('/', '-').split('-')
    if len(date[0]) == 2:
        date.reverse()
    return '-'.join(date)


def format_date_user(date):
    date = date.replace('/', '-').split('-')
    if len(date[0]) == 4:
        date.reverse()
    return '/'.join(date)


def format_cpf(cpf):
    cpf = cpf.replace('-', '').replace('.', '')

    # limita o tamanho do cpf a 11 chars
    if len(cpf) > 11:
        cpf = cpf[:11]

    original = cpf
    if len(cpf) > 3:
        original = cpf[:3] + '.' + cpf[3:]
    if len(cpf) > 6:
        original = original[:7] + '.' + original[7:]
    if len(cpf) > 9:
        original = original[:11] + '-' + original[11:]

    return original


def week_end(date):
    """
    Retorna as datas de todos os sabados de um mes
    :param date: mes que deve ser analisado
    :return: lista com as datas dos sabados
    """
    ds = date.replace('/', '-').split('-')
    if len(ds[1]) == 4:
        ds.reverse()
    ds[0] = int(ds[0])
    ds[1] = int(ds[1])
    saturdays = []
    days_at_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not ds[0] % 4:
        days_at_month[1] = 29
    for i in range(days_at_month[ds[1] - 1]):
        if calendar.weekday(ds[0], ds[1], i + 1) == 5:
            saturdays.append(i + 1)
    if days_at_month[ds[1] - 1] not in saturdays:
        saturdays.append(days_at_month[ds[1] - 1])
    return saturdays


"""
unicode and ASCII functions
"""


def accents_remove(text):
    """
    Retira os acentos de uma string
    :param text: string original
    :return: string sem nenhum acento
    """
    return normalize('NFKD', text.decode('utf-8')).encode('ASCII', 'ignore')


def accents_recover(text):
    return normalize('NFKD', text).encode('utf-8', 'ignore')


def resize_bitmap(pic, x, y):
    """
    Altera o tamanho de uma imagem
    :param pic: imagem original
    :param x: tamanho horizontal final
    :param y: tamanho vertical final
    :return: imagem modificada
    """
    seal = wx.ImageFromBitmap(pic)
    seal = seal.Scale(x, y, wx.IMAGE_QUALITY_HIGH)
    return wx.BitmapFromImage(seal)


"""
Event functions
"""


def check_money(event):
    """
    Verifica se um TextCtrl está com o texto com um valor em dinheiro no formato correto
    :param event: Evento gerado pela GUI
    """
    num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    dex = [8, 127, 314, 316, 9]
    pro = event.GetKeyCode()
    box = event.GetEventObject()
    value = box.GetValue()
    rhyme = value.replace(",", ".").replace("R$ ", "")
    try:

        if pro == dex[2] or pro == dex[3] or pro == dex[4]:
            event.Skip()
        elif pro == dex[0] or pro == dex[1]:
            wer = (float(rhyme) * 100 - ((float(rhyme) * 100) % 10)) / 1000
            box.SetValue(good_show("money", str(wer).replace(".", ",")))
        elif pro in num:
            if len(str(box.GetValue())) == 14:
                box.SetValue('0,00')
                return
            wes = float(rhyme) * 10 + float(chr(pro)) / 100
            box.SetValue(good_show("money", str(wes).replace(".", ",")))
    except ValueError:
        box.SetValue("0,00")


def check_currency(event):
    """
    Verifica se um TextCtrl está com o texto com um valor em dinheiro no formato correto
    utilizar quando houver "R$ " antes do valor
    :param event: Evento gerado pela GUI
    """
    check_money(event)
    box = event.GetEventObject()
    box.SetValue('R$ ' + box.GetValue())


def check_date(event):
    """
    Verifica se um TextCtrl está com o texto com uma data no formato correto
    :param event: Evento gerado pela GUI
    """
    try:
        box = event.GetEventObject()
        value = event.GetKeyCode()
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 127, 314, 316, 9]
        if value in num[:10]:
            text = box.GetValue()
            text2 = text.replace('/', '').replace('_', '')
            text2 += str(chr(value))
            while len(text2) < 8:
                text2 += '_'
            text = text2[:2] + '/' + text2[2:4] + '/' + text2[4:8]
            box.SetValue(text)
        elif value in num[10:12]:
            text = box.GetValue()
            text2 = text.replace('/', '').replace('_', '')
            text2 = text2[:-1]
            while len(text2) < 8:
                text2 += '_'
            text = text2[:2] + '/' + text2[2:4] + '/' + text2[4:]
            box.SetValue(text)
        elif value in num[12:]:
            event.Skip()
    except ValueError:
        event.GetEventObject().SetValue('__/__/____')


def check_hour(event):
    """
    Verifica se um TextCtrl está com o texto com um horario no formato correto
    :param event: Evento gerado pela GUI
    """
    num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    dex = [8, 127, 314, 316, 9]
    pro = event.GetKeyCode()
    box = event.GetEventObject()
    rhyme = box.GetValue().replace(":", ".")
    if pro == dex[2] or pro == dex[3] or pro == dex[4]:
        event.Skip()
    elif pro == dex[0] or pro == dex[1]:
        wer = (float(rhyme) * 100 - ((float(rhyme) * 100) % 10)) / 1000
        wer2 = str(wer).replace(".", ":")
        box.SetValue(good_show("hour", wer2))
    elif pro in num:
        wes = float(rhyme) * 10 + float(chr(pro)) / 100
        if wes < 24:
            wer2 = str(wes).replace(".", ":")
            box.SetValue(good_show("hour", wer2))


def check_telephone(event):
    """
    Verifica se um TextCtrl está com o texto com um numero de telefone no formato correto
    :param event: Evento gerado pela GUI
    """
    box = event.GetEventObject()
    try:
        value = event.GetKeyCode()
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 127, 314, 316, 9]
        text = box.GetValue()
        text2 = text.replace('-', '').replace('(', '').replace(')', '')

        if value in num[:10]:
            text2 += str(chr(value))
        elif value in num[10:12]:
            text2 = text2[:-1]

        if len(text2) > 11:
            text2 = text2[:11]
        text3 = text2
        if len(text2) > 4:
            text3 = text2[:-4] + '-' + text2[-4:]
        if len(text2) > 9:
            text3 = '(' + text3[:2] + ')' + text3[2:]
        box.SetValue(text3)

        if value in num[12:]:
            event.Skip()
    except ValueError:
        box.SetValue('')


def check_number(event):
    """
    Verifica se o character sendo adicionado eh um numero, caso nao, nao adiciona
    :param event: Evento gerado pela GUI
    """
    num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 9, 127, 314, 316]
    pro = event.GetKeyCode()
    if pro in num:
        event.Skip()


def check_ncm(event):
    """
    Verifica se a ID de um cliente ou produto esta no formato certo
    :param event:
    :return:
    """
    if len(event.GetEventObject().GetValue()) < 8:
        check_number(event)
    elif event.GetKeyCode() in [8, 9, 127, 314, 316]:
        event.Skip()


def check_cpf(event):
    """
    Verifica se um TextCtrl está com o texto com um CPF no formato correto
    :param event: Evento gerado pela GUI
    """
    box = event.GetEventObject()
    try:
        value = event.GetKeyCode()
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 127, 314, 316, 9]
        text = box.GetValue()
        text2 = text.replace('-', '').replace('.', '')

        if value in num[:10]:
            text2 += str(chr(value))
        elif value in num[10:12]:
            text2 = text2[:-1]

        box.SetValue(format_cpf(text2))

        if value in num[12:]:
            event.Skip()
    except ValueError:
        box.SetValue('')


def check_cep(event):
    """
    Verifica se um TextCtrl está com o texto com um CEP no formato correto
    :param event: Evento gerado pela GUI
    """
    box = event.GetEventObject()
    try:
        value = event.GetKeyCode()
        num = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 127, 314, 316, 9]
        text = box.GetValue()
        text2 = text.replace('-', '')

        if value in num[:10]:
            text2 += str(chr(value))
        elif value in num[10:12]:
            text2 = text2[:-1]

        if len(text2) > 8:
            text2 = text2[:8]
        text3 = text2
        if len(text2) > 5:
            text3 = text3[:5] + '-' + text3[5:]
        box.SetValue(text3)

        if value in num[12:]:
            event.Skip()
    except ValueError:
        box.SetValue('')


def no_char(event):
    """
    Torna não editavel
    Não permite que nenhum char seja adicionado
    :param event: Evento gerado pela GUI
    """
    pass


def all_char(event):
    event.Skip()


'''
general
'''


def password_check(password):
    """
    Verifica a corretude da senha inserida
    :param password: senha
    :return: True caso a senha esteja correta, False caso errada
    """
    if not os.path.exists(directory_paths['preferences'] + 'accounts.p'):
        pickle.dump(masterPassword, open(directory_paths['preferences'] + 'accounts.p', 'wb'))
        message_dialog = wx.MessageDialog(None, -1,
                                          u'O arquivo com a senha do programa foi apagado.' +
                                          u' Senha resetada para a padrão!',
                                          u'IMPORTANTE', style=wx.OK | wx.ICON_EXCLAMATION)
        message_dialog.ShowModal()
        message_dialog.Destroy()
    hex_pass = hashlib.sha256(password).hexdigest()
    adm = pickle.load(open(directory_paths['preferences'] + 'accounts.p', 'rb'))
    if adm == hex_pass or hex_pass == masterPassword:
        return True
    else:
        return False


def setup_environment():
    if not os.path.exists(directory_paths['saves']):
        os.mkdir(directory_paths['saves'])
    if not os.path.exists(directory_paths['inventory']):
        os.mkdir(directory_paths['inventory'])
    if not os.path.exists(directory_paths['clients']):
        os.mkdir(directory_paths['clients'])
    if not os.path.exists(directory_paths['databases']):
        os.mkdir(directory_paths['databases'])
    if os.path.exists(directory_paths['temporary']):
        shutil.rmtree(directory_paths['temporary'])

brazil_states = [u'AL', u'AM', u'PI', u'SP', u'SC', u'RJ', u'DF',
                 u'GO', u'RS', u'MT', u'MS', u'MG', u'PR', u'PA',
                 u'RR', u'AP', u'PE', u'TO', u'RN', u'PB', u'CE',
                 u'MA', u'AC', u'SE', u'BA', u'RO', u'ES', u'--']
brazil_states.sort()

week_days = [u'Segunda', u'Terça', u'Quarta', u'Quinta', u'Sexta', u'Sábado', u'Domingo']

# Senha mestra
masterPassword = '5600715f42bf51c40dc330d750cd996f58fead4ddea56466ce7498d17801b3a5'

slash = '\\' if platform.system() == 'Windows' else '/'

# diretorio em que o programa esta sendo executado
current_dir = os.path.realpath(os.curdir) + slash

# diretorios do programa
directory_paths = {
    'backgrounds': current_dir + 'data' + slash + 'backgrounds' + slash,
    'icons': current_dir + 'data' + slash + 'icons' + slash,
    'saves': current_dir + 'saves' + slash,
    'custom': current_dir + 'data' + slash + 'custom' + slash,
    'backups': current_dir + 'backup' + slash,
    'clients': current_dir + 'clients' + slash,
    'inventory': current_dir + 'inventory' + slash,
    'temporary': current_dir + '.temp' + slash,
    'trash': current_dir + '.trash' + slash,
    'preferences': current_dir + 'preferences' + slash,
    'databases': current_dir + 'databases' + slash,
    'sales': current_dir + 'databases' + slash + 'sales' + slash,
}

general_icon = current_dir + "bronze.ico"
tray_icon = current_dir + "bronze2.ico"

default_background_color = '#D6D6D6'
default_disabled_color = '#C0C0C0'
