#!/usr/bin/env python
# -*- coding: utf-8 -*-


from escpos.serial import SerialSettings
from escpos.impl.epson import TMT20
from satextrato import ExtratoCFeVenda, ExtratoCFeCancelamento


# Imprime um cupom de venda na impressora não fiscal
def imprimir_cupom_venda():
    # mini-impressora Epson TM-T20 conectada à porta serial COM1
    conn = SerialSettings.as_from('COM1:9600,8,1,N').get_connection()
    impressora = TMT20(conn)
    impressora.init()

    # abre o arquivo do CF-e e emite o extrato
    with open(r'C:\CFe545090.xml', 'r') as fp:
        extrato = ExtratoCFeVenda(fp, impressora)
        extrato.imprimir()


# Imprime um cupom de cancelamento na impressora não fiscal
def imprimir_cupom_cancelamento():
    # mini-impressora Epson TM-T20 conectada à porta serial COM1
    conn = SerialSettings.as_from('COM1:9600,8,1,N').get_connection()
    impressora = TMT20(conn)
    impressora.init()

    with open('CFe_1.xml', 'r') as fvenda, open('CFeCanc_1.xml', 'r') as fcanc:
        extrato = ExtratoCFeCancelamento(fvenda, fcanc, impressora)
        extrato.imprimir()