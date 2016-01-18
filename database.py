#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import data_types
import core


def database2product(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto produto
    :param database_list: lista obtidada do db contendo dados de um produto
    :type database_list: tuple
    :return: Objeto Produto
    :rtype: data_types.ProductData
    """
    data = data_types.ProductData()

    data.ID = database_list[0]
    data.barcode = database_list[1]
    data.description = database_list[2]
    data.category_ID = database_list[3]
    data.price = database_list[4]
    data.amount = database_list[5]
    data.sold = database_list[6]
    data.supplier = database_list[7]
    data.obs = database_list[8]
    data.record_time = database_list[9]
    data.record_date = database_list[10]

    return data


def database2category(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto categoria
    :param database_list: lista obtidada do db contendo dados de uma categoria
    :type database_list: tuple
    :return: Objeto Categoria
    :rtype: data_types.CategoryData
    """
    data = data_types.CategoryData()

    data.ID = database_list[0]
    data.category = database_list[1]
    data.ncm = database_list[2]
    data.cfop = database_list[3]

    return data


class InventoryDB:

    def __init__(self, db_path=None):
        """
        Método construtor. Abre o Banco de Dados de produtos
        :type db_path: String
        """
        if not db_path:
            db_path = core.directory_paths['databases'] + 'inventory.db'
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        try:
            self.create_table()
        except sqlite3.OperationalError:
            pass

    def close(self):
        """
        Fecha o banco de dados
        :return:
        """
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self):
        """
        Cria todas as tabelas do Banco de Dados de Produtos> Produtos, Categorias
        :return: None
        """
        self.cursor.execute('''CREATE TABLE INVENTORY(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            BARCODE CHAR(32) UNIQUE, DESCRIPTION TEXT NOT NULL, CATEGORY INTEGER NOT NULL,
            PRICE REAL NOT NULL, AMOUNT INTEGER, SOLD INTEGER, SUPPLIER TEXT, OBS TEXT, RECORD_TIME CHAR(8) NOT NULL,
            RECORD_DATE CHAR(10) NOT NULL)''')

        self.cursor.execute('''CREATE TABLE CATEGORIES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            CATEGORY TEXT NOT NULL UNIQUE, NCM CHAR(8))''')
        self.db.commit()

    def insert_product(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :type data: data_types.ProductData
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados mandados para um tuple

        _data = (data.barcode, data.description, data.category_ID, data.price, data.amount,
                 data.sold, data.supplier, data.obs, data.record_time, data.record_date)

        cmd = 'INSERT INTO INVENTORY (BARCODE, DESCRIPTION, CATEGORY, PRICE, AMOUNT, SOLD, SUPPLIER, OBS, '
        cmd += 'RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?)'
        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_product(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :type data: data_types.ProductData
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.barcode, data.description, data.category_ID, data.price,
                 data.amount, data.supplier, data.obs, data.record_time, data.record_date)

        # Prepara a linha de comando
        cmd = 'UPDATE INVENTORY SET BARCODE=?, DESCRIPTION=?, CATEGORY=?, PRICE=?, '
        cmd += 'AMOUNT=?, SUPPLIER=?, OBS=?, RECORD_TIME=?, RECORD_DATE=? WHERE ID=?'
        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_product(self, data):
        """
        Delete um produto do BD
        :type data: data_types.ProductData
        :param data: id do produto a ser deletado
        """
        self.cursor.execute('DELETE FROM INVENTORY WHERE ID=?', (data.ID, ))
        self.db.commit()

    def update_product_amount(self, data):
        """
        Atualiza a quantidade de um produto em estoque
        :type data: data_types.ProductData
        :param data: dados do produto
        """
        self.cursor.execute('UPDATE INVENTORY SET AMOUNT = ? where ID=?', (data.amount, data.ID))
        self.db.commit()

    def update_product_stock(self, data):
        """
        Atualiza a quantidade de um produto em estoque
        :type data: data_types.ProductData
        :param data: dados do produto
        """
        self.cursor.execute('UPDATE INVENTORY SET AMOUNT=AMOUNT+? where ID=?', (data.amount, data.ID))
        self.db.commit()

    def barcode_search(self, data):
        """
        Busca o item com um codigo de barras especifico no BD
        :type data: data_types.ProductData
        :param data: dados do produto
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (data.barcode, ))
        return database2product(self.cursor.fetchone())

    def inventory_search_id(self, data):
        """
        Busca o item com um ID especifico no BD
        :type data: data_types.ProductData
        :param data: dados do produto
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ID=?""", (data.ID, ))
        return database2product(self.cursor.fetchone())

    def inventory_search(self, info):    # TODO Atualmente apenas busca por igualdade, melhorar a busca
        """
        Faz uma busca por um dado generico mno banco de dados.
        Dada uma String busca por correspondecia por descrições, ids, categoria, fornecedores e NCM
        :param info: String com o dado a ser buscado
        :type info: String
        :return: List com todos os produtos compativeis com a busca
        :rtype: list(data_types.ProductData)
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ID=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE CATEGORY=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        info = '%' + info + '%'
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE DESCRIPTION LIKE ? ORDER BY DESCRIPTION""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM INVENTORY WHERE SUPPLIER LIKE ? ORDER BY DESCRIPTION""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        # Busca a entrada na tabela de categorias, compara com o nome da categoria
        category_list = list()

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ? ORDER BY DESCRIPTION""", (info, ))
        category_list = list(set(category_list + self.cursor.fetchall()))

        # Caso a entrada seja numerica, busca pelo NCM
        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE NCM LIKE ? ORDER BY DESCRIPTION""", (info, ))
            category_list = list(set(category_list + self.cursor.fetchall()))

        # Seleciona todos os produtos da categoria compativel com a busca
        for category in category_list:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE CATEGORY=? ORDER BY DESCRIPTION""", (category[0], ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        products_list = list()

        for product in filtered_list:
            products_list.append(database2product(product))

        return products_list

    def product_list(self):
        """
        Dados de todos os produtos cadastrados
        :return: Dados do produto encontrado
        :rtype: list(data_types.ProductData)
        """
        self.cursor.execute("""SELECT * FROM INVENTORY ORDER BY DESCRIPTION""")

        temp = self.cursor.fetchall()

        products_list = list()

        for product in temp:
            products_list.append(database2product(product))

        return products_list

    def insert_category(self, category, ncm):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param category: String com o nome da nova categoria
        :param ncm: numero do NCM dos produtos da categoria
        """

        self.cursor.execute('INSERT INTO CATEGORIES (CATEGORY, NCM) VALUES (?, ?)', (category, ncm))
        self.db.commit()

    def edit_category(self, category_id, category, ncm):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param category_id: int id da categoria a ser editada
        :param category: String com o nome da nova categoria
        :param ncm: numero do NCM dos produtos da categoria
        """

        self.cursor.execute('UPDATE CATEGORIES SET CATEGORY=?, NCM=? WHERE ID=?', (category, ncm, category_id))
        self.db.commit()

    def delete_category(self, category_id):
        """
        Apaga uma categoria do BD
        :param category_id: id da categoria sendo apagada
        :return:
        """
        self.cursor.execute('DELETE FROM CATEGORIES WHERE ID=?', (category_id, ))
        self.db.commit()

    def categories_search(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ID=? ORDER BY CATEGORY""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            pass

        info = '%' + info + '%'

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE NCM LIKE ? ORDER BY CATEGORY""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ? ORDER BY CATEGORY""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        categories_list = list()

        for product in filtered_list:
            categories_list.append(database2product(product))

        return categories_list

    def categories_search_id(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        """
        # Lista para armazenar todos os produtos compativeis com a busca

        # converte para integer para buscar por IDs e codigo de barras
        int_info = int(info)

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ID=?""", (int_info, ))
        return database2category(self.cursor.fetchone())

    def category_id(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        """

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY=?""", (info, ))
        return database2category(self.cursor.fetchone())

    def categories_list(self):
        """
        Fornece todas as categorias presentes no BD
        :return: Uma lista com todos os elementos do BD
        """
        self.cursor.execute("""SELECT * FROM CATEGORIES ORDER BY CATEGORY""")

        temp = self.cursor.fetchall()

        categories_list = list()

        for product in temp:
            categories_list.append(database2product(product))

        return categories_list


def database2client(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto cliente
    :param database_list: lista obtidada do db contendo dados de um cliente
    :type database_list: tuple
    :return: Objeto Cliente
    :rtype: data_types.ClientData
    """
    data = data_types.ClientData()

    data.ID = database_list[0]
    data.name = database_list[1]
    data.sex = database_list[2]
    data.birth = database_list[3]
    data.email = database_list[4]
    data.telephone = database_list[5]
    data.cpf = database_list[6]
    data.cep = database_list[7]
    data.state = database_list[8]
    data.city = database_list[9]
    data.district = database_list[10]
    data.address = database_list[11]
    data.obs = database_list[12]
    data.last_sale = database_list[13]
    data.record_date = database_list[14]

    return data


class ClientsDB:

    def __init__(self, db_path=None):
        """
        Método construtor. Abre o Banco de Dados de clientes
        :type db_path: String
        """
        if not db_path:
            db_path = core.directory_paths['databases'] + 'clients.db'
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        try:
            self.create_table()
        except sqlite3.OperationalError:
            pass

    def close(self):
        """
        Fecha o banco de dados
        :return:
        """
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self):
        """
        Cria todas as tabelas do Banco de Dados de Produtos> Produtos, Categorias
        :return: None
        """
        self.cursor.execute('''CREATE TABLE CLIENTS(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            NAME TEXT NOT NULL, SEX CHAR(10) NOT NULL, BIRTH CHAR(10), EMAIL TEXT, TELEPHONE CHAR(11),
            CPF CHAR(11), CEP CHAR(8), STATE CHAR(2), CITY TEXT, DISTRICT TEXT, ADDRESS TEXT,
            OBS TEXT, LAST_SALE CHAR(10), RECORD_DATE CHAR(10) NOT NULL)''')

        self.db.commit()

    def insert_client(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['address'], data['obs'], data['date'])

        cmd = 'INSERT INTO CLIENTS (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADDRESS, OBS, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_client(self, data, client_id):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        :param client_id: id do cliente a ser editado
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['address'], data['obs'], client_id)

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADDRESS=?, OBS=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_client(self, product_id):
        """
        Delete um produto do BD
        :param product_id: id do produto a ser deletado
        :return:
        """
        self.cursor.execute('DELETE FROM CLIENTS WHERE ID=?', (product_id, ))
        self.db.commit()

    def clients_search(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por descrições, ids, categoria, fornecedores e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos os produtos compativeis com a busca
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE ID=? ORDER BY NAME""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=? ORDER BY NAME""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        info = '%' + info + '%'

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE NAME LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE EMAIL LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE TELEPHONE LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CLIENTS WHERE CEP LIKE ? ORDER BY NAME""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE STATE LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE DISTRICT LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE CITY LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ADDRESS LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE OBS LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        return filtered_list

    def clients_search_cpf(self, cpf):
        """
        Faz uma busca por um cpf especifico no Banco de dados
        :param cpf: cpf do cliente a ser buscado
        :return: dados do cliente com o cpf especificado
        """
        self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=?""", (cpf, ))
        return self.cursor.fetchone()

    def clients_search_id(self, client_id):
        """
        Faz uma busca por um id especifico no Banco de dados
        :param client_id: id do cliente a ser buscado
        :return: dados do cliente com o id especificado
        """
        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ID=?""", (client_id, ))
        return self.cursor.fetchone()

    def clients_list(self):
        """
        Dados de todos os produtos cadastrados
        :rtype: list
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM CLIENTS ORDER BY NAME""")
        return self.cursor.fetchall()


def database2sale(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto venda
    :param database_list: lista obtidada do db contendo dados de uma venda
    :type database_list: tuple
    :return: Objeto Venda
    :rtype: data_types.SaleData
    """
    data = data_types.SaleData()

    data.ID = database_list[0]
    data.products_IDs = database_list[1].split()
    data.amounts = database_list[2].split()
    data.prices = database_list[3].split()
    data.sold = database_list[4]
    data.discount = database_list[5]
    data.taxes = database_list[6]
    data.value = database_list[7]
    data.payment = database_list[8]
    data.client_name = database_list[9]
    data.client_cpf = database_list[10]
    data.delivery_ID = database_list[11]
    data.record_time = database_list[12]
    data.record_date = database_list[13]

    return data


class SalesDB:

    def __init__(self, date, db_path=None):
        """
        Método construtor. Abre o Banco de Dados de clientes
        :type date: String
        :type db_path: String
        """

        date = core.format_date_internal(date)

        self.date = date
        if not db_path:
            db_path = core.directory_paths['sales'] + date[:8] + '.db'
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        if len(date) == 10:
            day = date[8:]
            try:
                self.create_table(day)
            except sqlite3.OperationalError:
                pass

    def close(self):
        """
        Fecha o banco de dados
        :return:
        """
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self, day):
        """
        Cria todas as tabelas do Banco de Dados de Produtos> Produtos, Categorias
        :param day: dia do mes
        :return: None
        """
        self.cursor.execute('''CREATE TABLE ?(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            PRODUCTS TEXT NOT NULL, AMOUNTS TEXT NOT NULL, PRICES TEXT NOT NULL, SOLD REAL, DISCOUNT REAL, TAXES REAL,
            VALUE REAL, PAYMENTE TEXT, CLIENT_NAME TEXT, CLIENT_CPF CHAR(11), DELIVERY_ID CHAR(8),
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL)''', (day, ))

        self.db.commit()

    def insert_sale(self, data, day=-1):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: dados da nova venda a ser cadastrada
        :param day: dia da venda sendo cadastrada
        """

        if day == -1:
            day = data.record_date[8:]

        try:
            self.create_table(day)
        except sqlite3.OperationalError:
            pass

        # Transfere os dados do dict mandado para um tuple
        _data = (day, data.products_IDs, data.amounts, data.prices, data.sold, data.discount, data.taxes,
                 data.value, data.payment, data.client_name, data.client_cpf, data.delivery_ID, data.record_time,
                 data.record_date)

        cmd = 'INSERT INTO ? (PRODUCTS, AMOUNTS, PRICES, SOLD, DISCOUNT, TAXES, VALUE, PAYMENT, CLIENT_NAME, '
        cmd += 'CLIENT_CPF, DELIVERY_ID, RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_sale(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        day = data.record_date[8:]

        # Transfere os dados do dict mandado para um tuple
        _data = (day, data.products_IDs, data.amounts, data.prices, data.sold, data.discount, data.taxes,
                 data.value, data.payment, data.client_name, data.client_cpf, data.delivery_ID, data.record_time,
                 data.record_date, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE ? SET PRODUCTS=?, AMOUNTS=?, PRICES=?, SOLD=?, DISCOUNT=?, TAXES=?, VALUE=?, PAYMENT=?, '
        cmd += 'CLIENT_NAME=?, CLIENT_CPF=?, DELIVERY_ID=?, RECORD_TIME=?, RECORD_DATE=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_sale(self, ID, day):
        """
        Delete um produto do BD
        :param ID: id do produto a ser deletado
        :param day: dia em que está registrada a venda
        :return:
        """
        self.cursor.execute('DELETE FROM ? WHERE ID=?', (day, ID))
        self.db.commit()

    def daily_sales_list(self, day):
        """
        Dados de todas as vendas cadastrados em um determinado dia
        :param day: dia do mes a ser verificado
        :rtype: list
        :return: uma list com todos os produtos do BD
        """
        try:
            self.cursor.execute("""SELECT * FROM ?""", (day, ))
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            return []

    def monthly_sales_list(self):
        """
        Dados de todas as vendas cadastrados em um mes
        :rtype: dict
        :return: uma list com todos os produtos do BD
        """
        total = dict()
        for day in range(1, 32):
            try:
                self.cursor.execute("""SELECT * FROM ?""", (day, ))
            except sqlite3.OperationalError:
                continue
            total[day] = self.cursor.fetchall()
        return total


class DeliveriesDB:

    def __init__(self, db_path=None):
        """
        Método construtor. Abre o Banco de Dados de clientes
        :type db_path: String
        """
        if not db_path:
            db_path = core.directory_paths['databases'] + 'deliveries.db'
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        try:
            self.create_table()
        except sqlite3.OperationalError:
            pass

    def close(self):
        """
        Fecha o banco de dados
        :return:
        """
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self):
        """
        Cria todas as tabelas do Banco de Dados de Produtos> Produtos, Categorias
        :return: None
        """
        self.cursor.execute('''CREATE TABLE DELIVERIES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            SALE_ID INTEGER NOT NULL, DELIVERY_TIME CHAR(8) NOT NULL, DELIVERY_DATE CHAR(10) NOT NULL)''')

        self.db.commit()

    def insert_client(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['address'], data['obs'], data['time'], data['date'])

        cmd = 'INSERT INTO INVENTORY (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADDRESS, OBS, RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_client(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['address'], data['obs'])

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADDRESS=?, OBS=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_client(self, product_id):
        """
        Delete um produto do BD
        :param product_id: id do produto a ser deletado
        :return:
        """
        self.cursor.execute('DELETE FROM CLIENTS WHERE ID=?', (product_id, ))
        self.db.commit()

    def clients_search(self, info):    # TODO Atualmente apenas busca por igualdade, melhorar a busca
        """
        Faz uma busca por um dado generico mno banco de dados.
        Dada uma String busca por correspondecia por descrições, ids, categoria, fornecedores e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos os produtos compativeis com a busca
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE ID=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=?""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        info = '%' + info + '%'

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE NAME LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE EMAIL LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE TELEPHONE LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CLIENTS WHERE CEP LIKE ?""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ADDRESS LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE OBS LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        return filtered_list

    def clients_search_cpf(self, cpf):

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=?""", (cpf, ))
        return self.cursor.fetchall()

    def clients_list(self):
        """
        Dados de todos os produtos cadastrados
        :rtype: list
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM CLIENTS""")
        return self.cursor.fetchall()
