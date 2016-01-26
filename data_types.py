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

    active = True

    def __init__(self):
        pass

    def database_insert(self):
        db = database.TransactionsDB(self.record_date)
        db.insert_sale(self)
        db.close()


class ExpenseData:

    ID = -1

    description = None

    value = 0.0

    record_time = None
    record_date = None

    active = True

    def __init__(self):
        pass

    def database_insert(self):
        db = database.TransactionsDB(self.record_date)
        db.insert_expense(self)
        db.close()


class WasteData:

    ID = -1

    product_ID = None

    amount = 0.0

    record_time = None
    record_date = None

    active = True

    def __init__(self):
        pass

    def database_insert(self):
        db = database.TransactionsDB(self.record_date)
        db.insert_waste(self)
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

    active = True

    def __init__(self):
        pass


class CategoryData:

    ID = -1

    category = None

    ncm = None

    cfop = None

    imposto = 0.0

    active = True

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

    active = True

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

    active = True

    def __init__(self):
        pass
