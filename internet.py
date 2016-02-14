#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webbrowser
import exception
import settings

NEW_TAB = 2     # open in a new tab, if possible

GOOGLE_MAPS_SEARCH = "https://www.google.com.br/maps?q="


def search_in_maps(address):
    """
    Busca um endereço no google maps
    :param address: Endereço a ser buscado
    :type address: str
    :rtype: None
    """
    url = GOOGLE_MAPS_SEARCH + address.replace(' ', '+')
    webbrowser.open(url, new=NEW_TAB)


def imposto_122741(category_id=None, data=None, origin=None):
    """
    coleta os dados de imposto de um determinado produto
    :param category_id: id do produto
    :param data: Produto a ter o imposto coletado
    :param origin: Frame de origem
    :type category_id: int
    :type data: data_types.ProductCategoryData
    :type origin: wx.Window
    :return: produto
    :rtype: data_types.ProductData
    """
    import ibptws.provisoes
    import ibptws.excecoes
    import database
    from ibptws import conf

    import requests

    conf.token = '797XZCfo2HY0TtThIPLPiMds9JzUrCDvUVhiPaJ_Jq7OFawH1OdSq3kJkOSsxPpI'
    conf.cnpj = '16678899000136'
    conf.estado = 'SP'

    if not data and not category_id:
        return False

    db = database.InventoryDB()

    if not data:
        data = db.categories_search_id(category_id)

    calc = ibptws.provisoes.SemProvisao()
    try:
        p = calc.get_produto(data.ncm, 0)
        data.imposto_federal = float(p.aliquota_nacional + p.aliquota_importado)
        data.imposto_estadual = float(p.aliquota_estadual)

        data.imposto_total = data.imposto_federal + data.imposto_estadual

    except ibptws.excecoes.ErroProdutoNaoEncontrado:
        import dialogs
        import categories
        dialogs.launch_error(origin, u'O NCM da categoria "%s" é inválido!' % data.category)
        if not isinstance(origin, categories.ProductCategoryData):
            categories.ProductCategoryData(origin, title=data.category, category_id=category_id, data=data)
        raise exception.ExceptionNCM

    except requests.ConnectionError:
        db.insert_category_fila(data.ID)
        raise exception.ExceptionInternet

    return data


def atualizar_imposto_122741():
    import threading
    import core

    last_update = settings.CONFIG.get(settings.CONFIG_SECTION_SAT, settings.CONFIG_FIELD_LAST_UPDATE_IMPOSTO)
    interval = int(settings.CONFIG.get(settings.CONFIG_SECTION_SAT, settings.CONFIG_FIELD_UPDATE_IMPOSTO_INTERVAL))

    now_date = core.date2int(core.datetime_today()[0])
    last_date = core.date2int(last_update)

    if now_date >= last_date + interval:
        thread = threading.Thread(target=__atualiza_imposto_122741)
    else:
        thread = threading.Thread(target=__fila_imposto_122741)

    thread.setDaemon(True)
    thread.start()


def __atualiza_imposto_122741():
    import database
    import core
    db = database.InventoryDB()
    line = db.categories_list()
    for data in line:
        try:
            imposto_122741(data=data)
            db.edit_category_impostos(data)
        except exception.ExceptionNCM:
            continue
        except exception.ExceptionInternet:
            continue
    settings.CONFIG.set(settings.CONFIG_SECTION_SAT, settings.CONFIG_FIELD_LAST_UPDATE_IMPOSTO,
                        core.datetime_today()[0])

    settings.save_config()


def __fila_imposto_122741():
    import database
    db = database.InventoryDB()
    line = db.fila_list()
    for category_id in line:
        try:
            data = db.categories_search_id(category_id)
            imposto_122741(data=data)
            db.edit_category_impostos(data)
        except exception.ExceptionNCM:
            continue
        except exception.ExceptionInternet:
            continue

    db.close()
