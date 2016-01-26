#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import data_types
import core

# TODO não apagar permanentemente as entradas, apenas desabilitar para não gerar bugs


def copy2memory(db_path, table=None):

    # create a memory database
    new_db = sqlite3.connect(':memory:')

    old_db = sqlite3.connect(db_path)

    query = ''

    if table:
        for line in old_db.iterdump():
            if table in line:
                query = line
                break
    else:
        query = "".join(line for line in old_db.iterdump())

    if not query:
        raise sqlite3.OperationalError('Tabela inexistente')

    # Dump old database in the new one.
    new_db.executescript(query)

    old_db.close()

    return new_db


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
    data.imposto = database_list[4]

    return data


class InventoryDB:

    default_path = core.directory_paths['databases'] + 'inventory.db'

    def __init__(self, db_path=None, table=None):
        """
        Método construtor. Abre o Banco de Dados de produtos
        :type db_path: String
        """
        if not db_path:
            db_path = self.default_path
        self.db_path = db_path

        if db_path == ':memory:':
            self.db = copy2memory(self.default_path, table)
        else:
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
            CATEGORY TEXT NOT NULL UNIQUE, NCM CHAR(8), CFOP CHAR(4), IMPOSTO REAL)''')
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

        data.ID = self.cursor.lastrowid

    def edit_product(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :type data: data_types.ProductData
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.barcode, data.description, data.category_ID, data.price,
                 data.amount, data.supplier, data.obs, data.record_time, data.record_date, data.ID)

        # Prepara a linha de comando
        cmd = 'UPDATE INVENTORY SET BARCODE=?, DESCRIPTION=?, CATEGORY=?, PRICE=?, '
        cmd += 'AMOUNT=?, SUPPLIER=?, OBS=?, RECORD_TIME=?, RECORD_DATE=? WHERE ID=?'
        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_product(self, product_id):
        """
        Delete um produto do BD
        :type product_id: str
        :param product_id: id do produto a ser deletado
        """
        self.cursor.execute('DELETE FROM INVENTORY WHERE ID=?', (product_id, ))
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

    def inventory_search_barcode(self, barcode):
        """
        Busca o item com um codigo de barras especifico no BD
        :type barcode: str
        :param barcode: Codigo de barras do produto
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (barcode, ))
        return database2product(self.cursor.fetchone())

    def inventory_search_id(self, product_id):
        """
        Busca o item com um ID especifico no BD
        :type product_id: int
        :param product_id: ID do produto
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ID=?""", (product_id, ))
        return database2product(self.cursor.fetchone())

    def inventory_search_description(self, description):
        """
        Busca o item com um ID especifico no BD
        :type description: str
        :param description: Descrição do produto
        :return: Dados do produto encontrado
        :rtype: list[data_types.ProductData]
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        info = '%' + description + '%'
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE DESCRIPTION LIKE ? ORDER BY DESCRIPTION""", (info, ))

        products_list = list()

        for product in self.cursor.fetchall():
            products_list.append(database2product(product))

        return products_list

    def inventory_search(self, info):
        """
        Faz uma busca por um dado generico mno banco de dados.
        Dada uma String busca por correspondecia por descrições, ids, categoria, fornecedores e NCM
        :param info: String com o dado a ser buscado
        :type info: String
        :return: List com todos os produtos compativeis com a busca
        :rtype: list[data_types.ProductData]
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

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ? ORDER BY CATEGORY""", (info, ))
        category_list = list(set(category_list + self.cursor.fetchall()))

        # Caso a entrada seja numerica, busca pelo NCM
        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE NCM LIKE ? ORDER BY NCM""", (info, ))
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
        :rtype: list[data_types.ProductData]
        """
        self.cursor.execute("""SELECT * FROM INVENTORY ORDER BY DESCRIPTION""")

        temp = self.cursor.fetchall()

        products_list = list()

        for product in temp:
            products_list.append(database2product(product))

        return products_list

    def insert_category(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: Dados da nova categoria
        :type data: data_types.CategoryData
        """

        # TODO buscar o imposto

        _data = (data.category, data.ncm, data.cfop, data.imposto)

        self.cursor.execute('INSERT INTO CATEGORIES (CATEGORY, NCM, CFOP, IMPOSTO) VALUES (?,?,?,?)', _data)
        self.db.commit()

    def edit_category(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: Dados da nova categoria
        :type data: data_types.CategoryData
        """

        _data = (data.category, data.ncm, data.cfop, data.imposto, data.ID)

        self.cursor.execute('UPDATE CATEGORIES SET CATEGORY=?, NCM=?, CFOP=?, IMPOSTO=? WHERE ID=?', _data)
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
        :rtype: list[data_types.CategoryData]
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

        for category in filtered_list:
            categories_list.append(database2category(category))

        return categories_list

    def categories_search_id(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        :rtype: data_types.CategoryData
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
        :rtype: list[data_types.CategoryData]
        """
        self.cursor.execute("""SELECT * FROM CATEGORIES ORDER BY CATEGORY""")

        temp = self.cursor.fetchall()

        categories_list = list()

        for category in temp:
            categories_list.append(database2category(category))

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
        Cria todas as tabelas do Banco de Dados de Clientes> CLIENTS
        :return: None
        """
        self.cursor.execute('''CREATE TABLE CLIENTS(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            NAME TEXT NOT NULL, SEX CHAR(10) NOT NULL, BIRTH CHAR(10), EMAIL TEXT, TELEPHONE CHAR(11),
            CPF CHAR(11), CEP CHAR(8), STATE CHAR(2), CITY TEXT, DISTRICT TEXT, ADDRESS TEXT,
            OBS TEXT, LAST_SALE CHAR(10), RECORD_DATE CHAR(10) NOT NULL)''')

        self.db.commit()

    def insert_client(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Clientes
        :type data: data_types.ClientData
        :param data: dados do novo cliente a ser inserido
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.name, data.sex, data.birth, data.email, data.telephone, data.cpf,
                 data.cep, data.state, data.city, data.district, data.address, data.obs, data.record_date)

        cmd = 'INSERT INTO CLIENTS (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADDRESS, OBS, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def edit_client(self, data):
        """
        Edita uma entrada do Banco de Dados de Clientes
        :type data: data_types.ClientData
        :param data: dados do cliente a ser editado
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.name, data.sex, data.birth, data.email, data.telephone, data.cpf,
                 data.cep, data.state, data.city, data.district, data.address, data.obs, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADDRESS=?, OBS=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_client(self, product_id):
        """
        Deleta um cliente do BD
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

        clients_list = list()

        for client in filtered_list:
            clients_list.append(database2client(client))

        return clients_list

    def clients_search_cpf(self, cpf):
        """
        Faz uma busca por um cpf especifico no Banco de dados
        :param cpf: cpf do cliente a ser buscado
        :return: dados do cliente com o cpf especificado
        """
        self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=?""", (cpf, ))
        return database2client(self.cursor.fetchone())

    def clients_search_id(self, client_id):
        """
        Faz uma busca por um id especifico no Banco de dados
        :param client_id: id do cliente a ser buscado
        :return: dados do cliente com o id especificado
        """
        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ID=?""", (client_id, ))
        return database2client(self.cursor.fetchone())

    def clients_list(self):
        """
        Dados de todos os produtos cadastrados
        :rtype: list
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM CLIENTS ORDER BY NAME""")

        temp = self.cursor.fetchall()

        clients_list = list()

        for client in temp:
            clients_list.append(database2client(client))

        return clients_list


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
    data.client_cpf = database_list[9]
    data.record_time = database_list[10]
    data.record_date = database_list[11]
    data.active = database_list[12]

    return data


def database2expense(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto gasto
    :param database_list: lista obtidada do db contendo dados de um gasto
    :type database_list: tuple
    :return: Objeto gASTO
    :rtype: data_types.ExpenseData
    """
    data = data_types.ExpenseData()

    data.ID = database_list[0]
    data.description = database_list[1]
    data.value = database_list[2]
    data.record_time = database_list[3]
    data.record_date = database_list[4]
    data.active = database_list[5]

    return data


def database2waste(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto desperdicio
    :param database_list: lista obtidada do db contendo dados de um desperdicio
    :type database_list: tuple
    :return: Objeto Desperdicio
    :rtype: data_types.WasteData
    """
    data = data_types.WasteData()

    data.ID = database_list[0]
    data.product_ID = database_list[1]
    data.amount = database_list[2]
    data.record_time = database_list[3]
    data.record_date = database_list[4]
    data.active = database_list[5]

    return data


class TransactionsDB:

    def __init__(self, db_path=None):
        """
        Método construtor. Abre o Banco de Dados de clientes
        :type db_path: String
        """

        if not db_path:
            db_path = core.directory_paths['databases'] + 'transactions.db'
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
        Cria todas as tabelas do Banco de Dados de Transações> Vendas, Gastos
        :return: None
        :rtype: None
        """
        self.cursor.execute('''CREATE TABLE SALES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            PRODUCTS TEXT NOT NULL, AMOUNTS TEXT NOT NULL, PRICES TEXT NOT NULL, SOLD REAL,
            DISCOUNT REAL, TAXES REAL, VALUE REAL, PAYMENT TEXT, CLIENT_CPF CHAR(11),
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE EXPENSES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            DESCRIPTION TEXT NOT NULL, VALUE REAL, RECORD_TIME CHAR(8) NOT NULL,
            RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE WASTES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            PRODUCT_ID INTEGER NOT NULL, AMOUNT INTEGER,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.db.commit()

    def insert_sale(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Vendas
        :param data: dados da nova venda a ser cadastrada
        :type data: data_types.SaleData
        """

        # Transfere os dados recebidos para um tuple
        _data = (' '.join(data.products_IDs), ' '.join(data.amounts), ' '.join(data.prices), data.sold, data.discount,
                 data.taxes, data.value, data.payment, data.client_cpf, data.record_time, data.record_date,
                 1 if data.active else 0)

        cmd = 'INSERT INTO SALES (PRODUCTS, AMOUNTS, PRICES, SOLD, DISCOUNT, TAXES, VALUE, PAYMENT, '
        cmd += 'CLIENT_CPF, RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere a nova venda no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_expense(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Gastos
        :param data: dados do novo gasto a ser cadastrado
        :type data: data_types.ExpenseData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.description, data.value, data.record_time, data.record_date, 1 if data.active else 0)

        cmd = 'INSERT INTO EXPENSES (DESCRIPTION, VALUE, RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?)'

        # Insere o novo gasto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_waste(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Desperdicio
        :param data: dados do novo Desperdicio a ser cadastrado
        :type data: data_types.WasteData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.product_ID, data.amount, data.record_time, data.record_date, 1 if data.active else 0)

        cmd = 'INSERT INTO WASTES (PRODUCT_ID, AMOUNT, RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?)'

        # Insere o novo gasto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def edit_sale(self, data):
        """
        Edita uma entrada do Banco de Dados de Vendas
        :param data: dados da venda a ser editada
        :type data: data_types.SaleData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.products_IDs, data.amounts, data.prices, data.sold, data.discount, data.taxes,
                 data.value, data.payment, data.client_cpf, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE SALES SET PRODUCTS=?, AMOUNTS=?, PRICES=?, SOLD=?, DISCOUNT=?, TAXES=?, VALUE=?, PAYMENT=?, '
        cmd += 'CLIENT_CPF=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_expense(self, data):
        """
        Edita uma entrada do Banco de Dados de Gastos
        :param data: dados do gasto a ser editado
        :type data: data_types.ExpenseData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.description, data.value, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE EXPENSES SET DESCRIPTION=?, VALUE=? WHERE ID=?'

        # Edita o gasto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_waste(self, data):
        """
        Edita uma entrada do Banco de Dados de Desperdicio
        :param data: dados do desperdicio a ser editado
        :type data: data_types.WasteData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.product_ID, data.amount, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE WASTES SET PRODUCT_ID=?, AMOUNT=? WHERE ID=?'

        # Edita o desperdicio no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_sale(self, sale_id):
        """
        Delete uma venda do BD
        :param sale_id: id da venda a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM SALES WHERE ID=?', (sale_id, ))
        self.db.commit()

    def delete_expense(self, expense_id):
        """
        Delete um gasto do BD
        :param expense_id: id do gasto a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM EXPENSES WHERE ID=?', (expense_id, ))
        self.db.commit()

    def delete_waste(self, waste_id):
        """
        Delete um Desperdicio do BD
        :param waste_id: id do desperdicio a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM WASTES WHERE ID=?', (waste_id, ))
        self.db.commit()

    def sales_search_id(self, sale_id):
        """
        Encontra a venda com um determinado ID
        :param sale_id: id da venda a ser buscada
        :rtype: data_types.SaleData
        :return: uma venda do BD
        """
        self.cursor.execute("""SELECT * FROM SALES WHERE ID=?""", (sale_id, ))

        return database2sale(self.cursor.fetchone())

    def expenses_search_id(self, expense_id):
        """
        Encontra o Gasto com um determinado ID
        :param expense_id: id da venda a ser buscada
        :rtype: data_types.ExpenseData
        :return: um objeto gasto
        """
        self.cursor.execute("""SELECT * FROM EXPENSES WHERE ID=?""", (expense_id, ))

        return database2expense(self.cursor.fetchone())

    def wastes_search_id(self, waste_id):
        """
        Encontra o desperdicio com um determinado ID
        :param waste_id: id da venda a ser buscada
        :rtype: data_types.WasteData
        :return: um objeto gasto
        """
        self.cursor.execute("""SELECT * FROM WASTES WHERE ID=?""", (waste_id, ))

        return database2waste(self.cursor.fetchone())

    def daily_sales_list(self, date):
        """
        Dados de todas as vendas cadastrados em um determinado dia
        :param date: data a ser verificada
        :rtype: list[data_types.SaleData]
        :return: uma list com todas as vendas do BD na data
        """
        self.cursor.execute("""SELECT * FROM SALES WHERE RECORD_DATE=?""", (date, ))

        temp = self.cursor.fetchall()
        sales_list = list()

        for sale in temp:
            sales_list.append(database2sale(sale))

        return sales_list

    def daily_expenses_list(self, date):
        """
        Dados de todos os gastos cadastrados em um determinado dia
        :param date: data a ser verificada
        :rtype: list[data_types.ExpenseData]
        :return: uma list com todos os gastos do BD na data
        """
        self.cursor.execute("""SELECT * FROM EXPENSES WHERE RECORD_DATE=?""", (date, ))

        temp = self.cursor.fetchall()
        expenses_list = list()

        for expense in temp:
            expenses_list.append(database2expense(expense))

        return expenses_list

    def daily_wastes_list(self, date):
        """
        Dados de todos os desperdicios cadastrados em um determinado dia
        :param date: data a ser verificada
        :rtype: list[data_types.WasteData]
        :return: uma list com todos os desperdicios do BD na data
        """
        self.cursor.execute("""SELECT * FROM WASTES WHERE RECORD_DATE=?""", (date, ))

        temp = self.cursor.fetchall()
        wastes_list = list()

        for waste in temp:
            wastes_list.append(database2waste(waste))

        return wastes_list

    def monthly_sales_list(self, month):
        """
        Dados de todas as vendas cadastrados em um determinado mes
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.SaleData]
        :return: uma list com todas as vendas do BD no mes
        """

        month += '%'

        self.cursor.execute("""SELECT * FROM SALES WHERE RECORD_DATE LIKE ?""", (month, ))

        temp = self.cursor.fetchall()
        sales_list = list()

        for sale in temp:
            sales_list.append(database2sale(sale))

        return sales_list

    def monthly_expenses_list(self, month):
        """
        Dados de todos os gastos cadastrados em um determinado mes
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.ExpenseData]
        :return: uma list com todos os gastos do BD no mes
        """

        month += '%'

        self.cursor.execute("""SELECT * FROM EXPENSES WHERE RECORD_DATE LIKE ?""", (month, ))

        temp = self.cursor.fetchall()
        expenses_list = list()

        for expense in temp:
            expenses_list.append(database2expense(expense))

        return expenses_list

    def monthly_wastes_list(self, month):
        """
        Dados de todos os desperdicios cadastrados em um determinado mes
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.WasteData]
        :return: uma list com todos os desperdicios do BD no mes
        """

        month += '%'

        self.cursor.execute("""SELECT * FROM WASTES WHERE RECORD_DATE LIKE ?""", (month, ))

        temp = self.cursor.fetchall()
        wastes_list = list()

        for waste in temp:
            wastes_list.append(database2waste(waste))

        return wastes_list

    def list_record_dates(self):
        """
        Obtém uma lista com todas as datas com dados registrados
        :return: Lista com todos os dias com movimento registrado
        :rtype: list[str]
        """
        records = list()

        self.cursor.execute('SELECT RECORD_DATE FROM WASTES')
        records = list(set(records + self.cursor.fetchall()))

        self.cursor.execute('SELECT RECORD_DATE FROM SALES')
        records = list(set(records + self.cursor.fetchall()))

        self.cursor.execute('SELECT RECORD_DATE FROM EXPENSES')
        records = list(set(records + self.cursor.fetchall()))

        for i in range(len(records)):
            records[i] = records[i][0]

        records.sort(reverse=True)

        return records


def database2delivery(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto venda
    :param database_list: lista obtidada do db contendo dados de uma venda
    :type database_list: tuple
    :return: Objeto Venda
    :rtype: data_types.DeliveryData
    """
    data = data_types.DeliveryData()

    data.ID = database_list[0]
    data.sale_ID = database_list[1]

    data.client = database_list[2]
    data.receiver = database_list[3]

    data.state = database_list[4]
    data.city = database_list[5]
    data.address = database_list[6]

    data.telephone = database_list[7]

    data.date = database_list[8]
    data.hour = database_list[9]

    data.obs = database_list[10]

    return data


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
        Cria todas as tabelas do Banco de Dados de Entregas>
        :return: None
        """
        self.cursor.execute('''CREATE TABLE DELIVERIES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            SALE_ID INTEGER NOT NULL, CLIENT TEXT, RECEIVER TEXT, STATE CHAR(2), CITY TEXT, ADDRESS TEXT,
            TELEPHONE CHAR(11), DELIVERY_TIME CHAR(8) NOT NULL, DELIVERY_DATE CHAR(10) NOT NULL, OBS TEXT)''')

        self.db.commit()

    def insert_delivery(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Entregas
        :param data: dados da nova entrega a ser inserida
        :type data: data_types.DeliveryData
        :rtype: None
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.sale_ID, data.client, data.receiver, data.state, data.city, data.address, data.telephone,
                 data.date, data.hour, data.obs)

        cmd = 'INSERT INTO DELIVERIES (SALE_ID, CLIENT, RECEIVER, SATATE, CITY, ADDRESS, TELEPHONE'
        cmd += 'DELIVERY_DATE, DELIVERY_HOUR, OBS) VALUES (?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def edit_delivery(self, data):
        """
        Edita uma entrada do Banco de Dados de Entregas
        :param data: dados da entrega
        :type data: data_types.DeliveryData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.client, data.receiver, data.state, data.city, data.address, data.telephone,
                 data.date, data.hour, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE DELIVERIES SET CLIENT=?, RECEIVER=?, STATE=?, CITY=?, ADDRESS=?, TELEPHONE=?, '
        cmd += 'DELIVERY_DATE=?, DELIVERY_HOUR=?, OBS=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_delivery(self, delivery_id):
        """
        Delete uma entrega do BD
        :param delivery_id: id da entrega a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute("""DELETE FROM DELIVERIES WHERE ID=?""", (delivery_id, ))
        self.db.commit()

    def deliverys_list(self, start=None, end=None):
        """
        Dados de todas as entregas programadas no periodo especificado
        :param start: Data inicial
        :param end: Data final
        :type start: str
        :type end: str
        :rtype: list[data_types.DeliveryData]
        :return: uma list com todas as entregas do BD entre as datas especificadas
        """
        if start and end:
            self.cursor.execute("""SELECT * FROM DELIVERIES WHERE DELIVERY_DATE BETWEEN ? AND ?
                                ORDER BY DELIVERY_DATA""", (start, end))

        elif start and not end:
            self.cursor.execute("""SELECT * FROM DELIVERIES WHERE DELIVERY_DATE <= ?
                                ORDER BY DELIVERY_DATA""", (end, ))

        elif not start and end:
            self.cursor.execute("""SELECT * FROM DELIVERIES WHERE DELIVERY_DATE BETWEEN >=
                                ORDER BY DELIVERY_DATA""", (start, ))

        else:
            self.cursor.execute("""SELECT * FROM DELIVERIES ORDER BY DELIVERY_DATA""")

        deliveries_list = list()

        for delivery in self.cursor.fetchall():
            deliveries_list.append(database2client(delivery))

        return deliveries_list
