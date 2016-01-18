#!/usr/bin/env python
# -*- coding: utf-8 -*-


import database


class SaleData:

    ID = -1

    products_IDs = None
    amounts = None

    sold = 0.0
    discount = 0.0
    value = 0.0

    payment = None

    client_name = None
    client_cpf = None

    delivery_ID = None

    record_time = None
    record_date = None

    def __init__(self):
        pass

    def database_insert(self):
        db = database.SalesDB(self.record_date)
        db.insert_sale(self)
        db.close()
