#!/usr/bin/env python
# -*- coding: utf-8 -*-


import database


class SaleData:

    ID = -1

    products_IDs = None
    amounts = None
    prices = None

    sold = 0.0
    discount = 0.0
    taxes = 0.0
    value = 0.0

    payment = None

    client_cpf = None

    record_time = None
    record_date = None

    def __init__(self):
        pass

    def database_insert(self):
        db = database.SalesDB(self.record_date)
        db.insert_sale(self)
        db.close()


class ProductData:

    ID = -1

    description = None
    barcode = None

    price = 0.0
    amount = -1
    sold = 0

    category_ID = -1
    supplier = None

    obs = None

    record_time = None
    record_date = None

    def __init__(self):
        pass


class CategoryData:

    ID = -1

    category = None

    ncm = None

    cfop = None

    imposto = 0.0

    def __init__(self):
        pass


class ClientData:

    ID = -1

    name = None
    sex = None
    birth = None
    cpf = None

    email = None
    telephone = None

    cep = None
    state = None
    city = None
    district = None
    address = None

    obs = None

    last_sale = None
    record_date = None

    def __init__(self):
        pass


class DeliveryData:
    ID = -1

    sale_ID = -1

    client = None

    receiver = None

    telephone = None

    state = None
    city = None
    district = None
    address = None

    date = None
    hour = None

    obs = None

    def __init__(self):
        pass
