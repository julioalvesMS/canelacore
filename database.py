#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import data_types
import core


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

    if not database_list:
        return None

    data = data_types.ProductData()

    data.ID = database_list[0]
    data.barcode = database_list[1] if database_list[1] else ''
    data.description = database_list[2]
    data.category_ID = database_list[3]
    data.price = database_list[4]
    data.amount = database_list[5]
    data.sold = database_list[6]
    data.supplier = database_list[7]
    data.obs = database_list[8]
    data.record_time = database_list[9]
    data.record_date = database_list[10]
    data.active = True if database_list[11] else False

    return data


def database2productcategory(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto categoria
    :param database_list: lista obtidada do db contendo dados de uma categoria
    :type database_list: tuple
    :return: Objeto Categoria
    :rtype: data_types.ProductCategoryData
    """
    if not database_list:
        return None

    data = data_types.ProductCategoryData()

    data.ID = database_list[0]
    data.category = database_list[1]
    data.ncm = database_list[2]
    data.cfop = database_list[3]
    data.imposto = database_list[4]
    data.unit = database_list[5]
    data.active = True if database_list[6] else False

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
            PRICE REAL NOT NULL, AMOUNT REAL, SOLD REAL, SUPPLIER TEXT, OBS TEXT, RECORD_TIME CHAR(8) NOT NULL,
            RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE CATEGORIES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            CATEGORY TEXT NOT NULL UNIQUE, NCM CHAR(8), CFOP INTEGER, IMPOSTO REAL,
            UNIT CHAR(6) NOT NULL, ACTIVE INTEGER)''')
        self.db.commit()

    def insert_product(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :type data: data_types.ProductData
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados mandados para um tuple

        _data = (data.barcode, data.description, data.category_ID, data.price, data.amount,
                 data.sold, data.supplier, data.obs, data.record_time, data.record_date, 1)

        cmd = 'INSERT INTO INVENTORY (BARCODE, DESCRIPTION, CATEGORY, PRICE, AMOUNT, SOLD, SUPPLIER, OBS, '
        cmd += 'RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
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
                 data.amount, data.supplier, data.obs, data.record_time, data.record_date, 1, data.ID)

        # Prepara a linha de comando
        cmd = 'UPDATE INVENTORY SET BARCODE=?, DESCRIPTION=?, CATEGORY=?, PRICE=?, '
        cmd += 'AMOUNT=?, SUPPLIER=?, OBS=?, RECORD_TIME=?, RECORD_DATE=?, ACTIVE=? WHERE ID=?'
        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def delete_product(self, product_id, undo=False):
        """
        Deleta permanentemente um produto do BD
        :type undo: bool
        :param undo: Caso True recupera um registro apagado
        :type product_id: int
        :param product_id: id do produto a ser deletado
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE INVENTORY SET ACTIVE=? WHERE ID=?', (active, product_id))
        self.db.commit()

    def delete_product_permanently(self, product_id):
        """
        Deleta permanentemente um produto do BD
        :type product_id: int
        :param product_id: id do produto a ser deletado
        """
        self.cursor.execute('DELETE FROM INVENTORY WHERE ID=?', (product_id, ))
        self.db.commit()

    def update_product_amount(self, product_id, amount):
        """
        Atualiza a quantidade de um produto em estoque
        :type product_id: int
        :type amount: float
        :param product_id: ID do produto
        :param amount: variacao no estoque
        """
        self.cursor.execute('UPDATE INVENTORY SET AMOUNT=? WHERE ID=?', (amount, product_id))
        self.db.commit()

    def update_product_stock(self, product_id, change, sold=True):
        """
        Altera o estoque de um produto em: change unidades
        :type product_id: int
        :type change: float
        :type sold: bool
        :param product_id: ID do produto
        :param change: variacao no estoque
        :param sold: True caso o estoque esteja sendo alterado devido a uma venda
        """
        if sold:
            self.cursor.execute('UPDATE INVENTORY SET AMOUNT=AMOUNT+?, SOLD=SOLD+? where ID=?',
                                (change, -change, product_id))
        else:
            self.cursor.execute('UPDATE INVENTORY SET AMOUNT=AMOUNT+? where ID=?',
                                (change, product_id))
        self.db.commit()

    def inventory_search_barcode(self, barcode, show_all=False):
        """
        Busca o item com um codigo de barras especifico no BD
        :type barcode: str
        :type show_all: bool
        :param barcode: Codigo de barras do produto
        :param show_all: Mostrar as entradas apagas também
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        if show_all:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (barcode, ))
        else:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND BARCODE=?""", (barcode, ))

        return database2product(self.cursor.fetchone())

    def inventory_search_id(self, product_id):
        """
        Busca o item com um ID especifico no BD
        :param product_id: ID do produto
        :type product_id: int
        :return: Dados do produto encontrado
        :rtype: data_types.ProductData
        """

        # Faz o BD mostrar apenas o item com um ID
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
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND
                            DESCRIPTION LIKE ? ORDER BY DESCRIPTION""", (info, ))

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

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND ID=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND BARCODE=?""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND CATEGORY=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        info = '%' + info + '%'
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND
                            DESCRIPTION LIKE ? ORDER BY DESCRIPTION""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND
                            SUPPLIER LIKE ? ORDER BY DESCRIPTION""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        # Busca a entrada na tabela de categorias, compara com o nome da categoria
        category_list = list()

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 AND
                            CATEGORY LIKE ? ORDER BY CATEGORY""", (info, ))
        category_list = list(set(category_list + self.cursor.fetchall()))

        # Caso a entrada seja numerica, busca pelo NCM
        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 AND
                                NCM LIKE ? ORDER BY NCM""", (info, ))
            category_list = list(set(category_list + self.cursor.fetchall()))

        # Seleciona todos os produtos da categoria compativel com a busca
        for category in category_list:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND
                                CATEGORY=? ORDER BY DESCRIPTION""", (category[0], ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        products_list = list()

        for product in filtered_list:
            products_list.append(database2product(product))

        return products_list

    def product_list(self, deleted=False):
        """
        Dados de todos os produtos cadastrados
        :type deleted: bool
        :param deleted: Caso True mostra apenas os produtos apagados, else apenas os ativos
        :return: Dados do produto encontrado
        :rtype: list[data_types.ProductData]
        """
        if deleted:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=0 ORDER BY DESCRIPTION""")
        else:
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 ORDER BY DESCRIPTION""")

        temp = self.cursor.fetchall()

        products_list = list()

        for product in temp:
            products_list.append(database2product(product))

        return products_list

    def insert_category(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: Dados da nova categoria
        :type data: data_types.ProductCategoryData
        """

        # TODO buscar o imposto

        _data = (data.category, data.ncm, data.cfop, data.imposto, data.unit, 1)

        self.cursor.execute("""INSERT INTO CATEGORIES (CATEGORY, NCM, CFOP,
                            IMPOSTO, UNIT, ACTIVE) VALUES (?,?,?,?,?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def edit_category(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: Dados da nova categoria
        :type data: data_types.ProductCategoryData
        """

        _data = (data.category, data.ncm, data.cfop, data.imposto, data.unit, 1, data.ID)

        self.cursor.execute("""UPDATE CATEGORIES SET CATEGORY=?, NCM=?, CFOP=?,
                            IMPOSTO=?, UNIT=?, ACTIVE=? WHERE ID=?""", _data)
        self.db.commit()

        data.active = True

    def delete_category(self, category_id, undo=False):
        """
        Deleta permanentemente uma categoria do BD
        :type undo: bool
        :param undo: Caso True recupera um registro apagado
        :type category_id: int
        :param category_id: id da categoria a ser deletada
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE CATEGORIES SET ACTIVE=? WHERE ID=?', (active, category_id))
        self.db.commit()

    def delete_category_permanently(self, category_id):
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
        :rtype: list[data_types.ProductCategoryData]
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 AND ID=? ORDER BY CATEGORY""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            pass

        info = '%' + info + '%'

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 AND NCM LIKE ? ORDER BY CATEGORY""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 AND CATEGORY LIKE ? ORDER BY CATEGORY""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        categories_list = list()

        for category in filtered_list:
            categories_list.append(database2productcategory(category))

        return categories_list

    def categories_search_id(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        :rtype: data_types.ProductCategoryData
        """
        # Lista para armazenar todos os produtos compativeis com a busca

        # converte para integer para buscar por IDs e codigo de barras
        int_info = int(info)

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ID=?""", (int_info, ))
        return database2productcategory(self.cursor.fetchone())

    def category_search_name(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        """

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY=?""", (info, ))
        return database2productcategory(self.cursor.fetchone())

    def categories_list(self, deleted=False):
        """
        Fornece todas as categorias presentes no BD
        :type deleted: bool
        :param deleted: mostrar apenas as apagas ou apenas as ativas
        :return: Uma lista com todos os elementos do BD
        :rtype: list[data_types.ProductCategoryData]
        """
        if deleted:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=0 ORDER BY CATEGORY""")
        else:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=1 ORDER BY CATEGORY""")

        temp = self.cursor.fetchall()

        categories_list = list()

        for category in temp:
            categories_list.append(database2productcategory(category))

        return categories_list


def database2client(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto cliente
    :param database_list: lista obtidada do db contendo dados de um cliente
    :type database_list: tuple
    :return: Objeto Cliente
    :rtype: data_types.ClientData
    """
    if not database_list:
        return None

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
    data.active = True if database_list[15] else False

    return data


def database2clientsale(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto cliente venda
    :param database_list: lista obtidada do db contendo dados de um cliente venda
    :type database_list: tuple
    :return: Objeto Cliente Venda
    :rtype: data_types.ClientSaleData
    """
    if not database_list:
        return None

    data = data_types.ClientSaleData()

    data.ID = database_list[0]
    data.client = database_list[1]
    data.sale = database_list[2]
    data.active = True if database_list[3] else False

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
            OBS TEXT, LAST_SALE CHAR(10), RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE SALES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            CLIENT INTEGER NOT NULL, SALE INTEGER NOT NULL UNIQUE, ACTIVE INTEGER NOT NULL)''')

        self.db.commit()

    def insert_client(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Clientes
        :type data: data_types.ClientData
        :param data: dados do novo cliente a ser inserido
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.name, data.sex, data.birth, data.email, data.telephone, data.cpf,
                 data.cep, data.state, data.city, data.district, data.address, data.obs, data.record_date, 1)

        cmd = 'INSERT INTO CLIENTS (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADDRESS, OBS, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_sale(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Clientes Vendas
        :type data: data_types.ClientSaleData
        :param data: dados da nova entrada a ser inserido
        """

        self.cursor.execute("""SELECT ID FROM SALES WHERE SALE=?""", (data.sale, ))

        temp = self.cursor.fetchone()
        if temp:
            data.ID = temp[0]

            return self.edit_sale(data)

        # Transfere os dados do dict mandado para um tuple
        _data = (data.client, data.sale, 1)

        # Insere o novo produto no BD
        self.cursor.execute("""INSERT INTO SALES (CLIENT, SALE, ACTIVE) VALUES (?,?,?)""", _data)
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
                 data.cep, data.state, data.city, data.district, data.address, data.obs, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADDRESS=?, OBS=?, ACTIVE=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def edit_sale(self, data):
        """
        Edita uma entrada do Banco de Dados de Clientes-Vendas
        :type data: data_types.ClientSaleData
        :param data: dados da entrada a ser editada
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.client, data.sale, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE SALES SET CLIENT=?, SALE=?, ACTIVE=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def edit_client_last_sale(self, client_id, last_sale):
        """
        Permite alterar a data da ultima venda de um cliente
        :param client_id: id do cliente
        :param last_sale: data da ultima venda a ser registrada
        :type client_id: int
        :type last_sale: str
        """

        self.cursor.execute('UPDATE CLIENTS SET LAST_SALE=? WHERE ID=?', (last_sale, client_id))
        self.db.commit()

    def delete_client(self, client_id, undo=False):
        """
        Deleta um cliente do BD
        :type undo: bool
        :param undo: Recuperar uma entrada apagada
        :param client_id: id do cliente a ser deletado
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE CLIENTS SET ACTIVE=? WHERE ID=?', (active, client_id))
        self.db.commit()

    def delete_sale(self, client_sale_id, undo=False):
        """
        Deleta permanentemente um cliente do BD
        :type undo: bool
        :param undo: Recuperar uma entrada apagada
        :param client_sale_id: id do cliente a ser deletado
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE SALES SET ACTIVE=? WHERE ID=?', (active, client_sale_id))
        self.db.commit()

    def delete_client_permanently(self, client_id):
        """
        Deleta permanentemente um cliente do BD
        :param client_id: id do cliente a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM CLIENTS WHERE ID=?', (client_id, ))
        self.db.commit()

    def delete_sale_permanently(self, client_sale_id):
        """
        Deleta permanentemente uma entrada do BD
        :param client_sale_id: id da entrada a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM SALES WHERE ID=?', (client_sale_id, ))
        self.db.commit()

    def clients_search(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por descrições, ids, categoria, fornecedores e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos os produtos compativeis com a busca
        :rtype: list[data_types.ClientData]
        """
        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND ID=? ORDER BY NAME""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND CPF=? ORDER BY NAME""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        info = '%' + info + '%'

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND NAME LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND EMAIL LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND TELEPHONE LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CLIENTS ACTIVE=1 AND WHERE CEP LIKE ? ORDER BY NAME""", (info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND STATE LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND DISTRICT LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND CITY LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND ADDRESS LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND OBS LIKE ? ORDER BY NAME""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        clients_list = list()

        for client in filtered_list:
            clients_list.append(database2client(client))

        return clients_list

    def clients_search_cpf(self, cpf, show_all=False):
        """
        Faz uma busca por um cpf especifico no Banco de dados
        :type show_all: bool
        :param show_all: Procurar entre todas as entradas, inclusive as apagadas
        :param cpf: cpf do cliente a ser buscado
        :return: dados do cliente com o cpf especificado
        :rtype: data_types.ClientData
        """
        if show_all:
            self.cursor.execute("""SELECT * FROM CLIENTS WHERE CPF=?""", (cpf, ))
        else:
            self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=1 AND CPF=?""", (cpf, ))
        return database2client(self.cursor.fetchone())

    def sales_search_client(self, client_id, show_all=False):
        """
        Faz uma busca por um cliente especifico no Banco de dados
        :type client_id: int
        :type show_all: bool
        :param show_all: Mostrar também as entradas apgadas
        :param client_id: id do cliente a ser buscado
        :return: dados da entrada com o id especificado
        :rtype: list[data_types.ClientSaleData]
        """
        if show_all:
            self.cursor.execute("""SELECT * FROM SALES WHERE CLIENT=?""", (client_id, ))
        else:
            self.cursor.execute("""SELECT * FROM SALES WHERE ACTIVE=1 AND CLIENT=?""", (client_id, ))

        temp = self.cursor.fetchall()

        client_sale_list = list()

        for client_sale in temp:
            client_sale_list.append(database2clientsale(client_sale))

        return client_sale_list

    def sales_search_sale(self, sale_id, show_all=False):
        """
        Faz uma busca por uma venda especifica no Banco de dados
        :type sale_id: int
        :type show_all: bool
        :param show_all: Mostrar também as entradas apgadas
        :param sale_id: id da venda a ser buscada
        :return: dados da entrada com o id especificado
        :rtype: data_types.ClientSaleData
        """
        if show_all:
            self.cursor.execute("""SELECT * FROM SALES WHERE SALE=?""", (sale_id, ))
        else:
            self.cursor.execute("""SELECT * FROM SALES WHERE ACTIVE=1 AND SALE=?""", (sale_id, ))

        temp = self.cursor.fetchall()

        client_sale_list = list()

        for client_sale in temp:
            client_sale_list.append(database2clientsale(client_sale))

        return client_sale_list

    def clients_search_id(self, client_id):
        """
        Faz uma busca por um id especifico no Banco de dados
        :type client_id: int
        :param client_id: id do cliente a ser buscado
        :return: dados do cliente com o id especificado
        :rtype: data_types.ClientData
        """
        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ID=?""", (client_id, ))
        return database2client(self.cursor.fetchone())

    def sales_search_id(self, client_sale_id):
        """
        Faz uma busca por um id especifico no Banco de dados
        :param client_sale_id: id da entrada a ser buscada
        :return: dados da entrada com o id especificado
        :rtype: data_types.ClientSaleData
        """
        self.cursor.execute("""SELECT * FROM SALES WHERE ID=?""", (client_sale_id, ))
        return database2clientsale(self.cursor.fetchone())

    def clients_list(self, deleted=False):
        """
        Dados de todos os produtos cadastrados
        :type deleted: bool
        :param deleted: Mostrar apenas as entradas apagadas
        :rtype: list[data_types.ClientData]
        :return: uma list com todos os produtos do BD
        """
        active = 0 if deleted else 1

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ACTIVE=? ORDER BY NAME""", (active, ))

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
    if not database_list:
        return None

    data = data_types.SaleData()

    data.ID = database_list[0]
    data.products_IDs = core.convert_list(database_list[1].split(), int)
    data.amounts = core.convert_list(database_list[2].split(), float)
    data.prices = core.convert_list(database_list[3].split(), float)
    data.sold = database_list[4]
    data.discount = database_list[5]
    data.taxes = database_list[6]
    data.value = database_list[7]
    data.payment = database_list[8]
    data.client_cpf = database_list[9]
    data.client_id = database_list[10]
    data.delivery = True if database_list[11] else False
    data.record_time = database_list[12]
    data.record_date = database_list[13]
    data.payment_pendant = True if database_list[14] else False
    data.active = True if database_list[15] else False

    return data


def database2expense(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto gasto
    :param database_list: lista obtidada do db contendo dados de um gasto
    :type database_list: tuple
    :return: Objeto Gasto
    :rtype: data_types.ExpenseData
    """
    if not database_list:
        return None

    data = data_types.ExpenseData()

    data.ID = database_list[0]
    data.description = database_list[1]
    data.value = database_list[2]
    data.category = database_list[3]
    data.record_time = database_list[4]
    data.record_date = database_list[5]
    data.active = True if database_list[6] else False

    return data


def database2waste(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto desperdicio
    :param database_list: lista obtidada do db contendo dados de um desperdicio
    :type database_list: tuple
    :return: Objeto Desperdicio
    :rtype: data_types.WasteData
    """
    if not database_list:
        return None

    data = data_types.WasteData()

    data.ID = database_list[0]
    data.product_ID = database_list[1]
    data.amount = database_list[2]
    data.record_time = database_list[3]
    data.record_date = database_list[4]
    data.active = True if database_list[5] else False

    return data


def database2transaction(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto transação
    :param database_list: lista obtidada do db contendo dados de uma transação
    :type database_list: tuple
    :return: Objeto Transação
    :rtype: data_types.TransactionData
    """
    if not database_list:
        return None

    data = data_types.TransactionData()

    data.ID = database_list[0]
    data.description = database_list[1]
    data.value = database_list[2]
    data.transaction_date = database_list[3]
    data.category = database_list[4]
    data.record_time = database_list[5]
    data.record_date = database_list[6]
    data.payment_pendant = True if database_list[7] else False
    data.active = True if database_list[8] else False

    return data


def database2transactioncategory(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto categoria de transação
    :param database_list: lista obtidada do db contendo dados de uma categoria de transação
    :type database_list: tuple
    :return: Objeto Transação
    :rtype: data_types.TransactionCategoryData
    """
    if not database_list:
        return None

    data = data_types.TransactionCategoryData()

    data.ID = database_list[0]
    data.category = database_list[1]
    data.active = True if database_list[2] else False

    return data


def database2cashregister(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto transação
    :param database_list: lista obtidada do db contendo dados de uma transação
    :type database_list: tuple
    :return: Objeto Transação
    :rtype: data_types.CashRegisterData
    """
    if not database_list:
        return None

    data = data_types.CashRegisterData()

    data.ID = database_list[0]
    data.fund = database_list[1]
    data.cash = database_list[2]
    data.withdrawal = database_list[3]
    data.record_date = database_list[4]
    data.active = True if database_list[5] else False

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
            PRODUCTS TEXT NOT NULL, AMOUNTS TEXT NOT NULL, PRICES TEXT NOT NULL, SOLD REAL, DISCOUNT REAL,
            TAXES REAL, VALUE REAL, PAYMENT TEXT, CLIENT_CPF CHAR(11), CLIENT_ID INTEGER, DELIVERY INTEGER,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, PAYMENT_PENDANT INTEGER, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE EXPENSES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            DESCRIPTION TEXT NOT NULL, VALUE REAL, CATEGORY INTEGER,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE WASTES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            PRODUCT_ID INTEGER NOT NULL, AMOUNT INTEGER,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE TRANSACTIONS(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            DESCRIPTION TEXT NOT NULL, VALUE REAL, TRANSACTION_DATE CHAR(10) NOT NULL, CATEGORY INTEGER, TYPE INTEGER,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL, PAYMENT_PENDANT INTEGER, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE CATEGORIES(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            CATEGORY TEXT NOT NULL UNIQUE, ACTIVE INTEGER)''')

        self.cursor.execute('''CREATE TABLE CASH_REGISTER(ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            FUND REAL, CASH REAL, WITHDRAWAL REAL, RECORD_DATE CHAR(10) NOT NULL, ACTIVE INTEGER)''')

        self.db.commit()

    def insert_sale(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Vendas
        :param data: dados da nova venda a ser cadastrada
        :type data: data_types.SaleData
        """

        products_ids = ' '.join(core.convert_list(data.products_IDs, str))
        amounts = ' '.join(core.convert_list(data.amounts, str))
        prices = ' '.join(core.convert_list(data.prices, str))

        # Transfere os dados recebidos para um tuple
        _data = (products_ids, amounts, prices, data.sold, data.discount,
                 data.taxes, data.value, data.payment, data.client_cpf, data.client_id, 1 if data.delivery else 0,
                 data.record_time, data.record_date, 1 if data.payment_pendant else 0, 1)

        # Insere a nova venda no BD
        self.cursor.execute("""INSERT INTO SALES (PRODUCTS, AMOUNTS, PRICES, SOLD, DISCOUNT, TAXES, VALUE, PAYMENT,
                            CLIENT_CPF, CLIENT_ID, DELIVERY, RECORD_TIME, RECORD_DATE, PAYMENT_PENDANT, ACTIVE) VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_expense(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Gastos
        :param data: dados do novo gasto a ser cadastrado
        :type data: data_types.ExpenseData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.description, data.value, data.category, data.record_time, data.record_date, 1)

        # Insere o novo gasto no BD
        self.cursor.execute("""INSERT INTO EXPENSES (DESCRIPTION, VALUE, CATEGORY,
                            RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_waste(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Desperdicio
        :param data: dados do novo Desperdicio a ser cadastrado
        :type data: data_types.WasteData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.product_ID, data.amount, data.record_time, data.record_date, 1)

        cmd = 'INSERT INTO WASTES (PRODUCT_ID, AMOUNT, RECORD_TIME, RECORD_DATE, ACTIVE) VALUES (?,?,?,?,?)'

        # Insere o novo gasto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_transaction(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Transações
        :param data: dados da nova Transações a ser cadastrada
        :type data: data_types.TransactionData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.description, data.value, data.transaction_date, data.category, data.type, data.record_time,
                 data.record_date, 1 if data.payment_pendant else 0, 1)

        # Insere o novo gasto no BD
        self.cursor.execute("""INSERT INTO TRANSACTIONS (DESCRIPTION, VALUE, TRANSACTION_DATE, CATEGORY, TYPE,
                            RECORD_TIME, RECORD_DATE, PAYMENT_PENDANT, ACTIVE) VALUES (?,?,?,?,?,?,?,?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_category(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Categorias
        :param data: dados da nova Categoria a ser cadastrada
        :type data: data_types.TransactionCategoryData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.category, 1)

        # Insere o novo gasto no BD
        self.cursor.execute("""INSERT INTO CATEGORIES (CATEGORY, ACTIVE) VALUES (?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def insert_cash(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Caixa
        :param data: dados do novo registro de caixa a ser cadastrado
        :type data: data_types.CashRegisterData
        """

        # Transfere os dados recebidos para um tuple
        _data = (data.fund, data.cash, data.withdrawal, data.record_date, 1)

        # Insere o novo gasto no BD
        self.cursor.execute("""INSERT INTO CASH_REGISTER (FUND, CASH, WITHDRAWAL, RECORD_DATE, ACTIVE)
                            VALUES (?,?,?,?,?)""", _data)
        self.db.commit()

        data.ID = self.cursor.lastrowid

    def edit_sale(self, data):
        """
        Edita uma entrada do Banco de Dados de Vendas
        :param data: dados da venda a ser editada
        :type data: data_types.SaleData
        """

        products_ids = ' '.join(core.convert_list(data.products_IDs, str))
        amounts = ' '.join(core.convert_list(data.amounts, str))
        prices = ' '.join(core.convert_list(data.prices, str))

        # Transfere os dados do dict mandado para um tuple
        _data = (products_ids, amounts, prices, data.sold, data.discount, data.taxes,
                 data.value, data.payment, data.client_cpf, data.client_id, 1 if data.payment_pendant else 0, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE SALES SET PRODUCTS=?, AMOUNTS=?, PRICES=?, SOLD=?, DISCOUNT=?, TAXES=?, VALUE=?, PAYMENT=?, '
        cmd += 'CLIENT_CPF=?, CLIENT_ID=?, PAYMENT_PENDANT=?, ACTIVE=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def edit_expense(self, data):
        """
        Edita uma entrada do Banco de Dados de Gastos
        :param data: dados do gasto a ser editado
        :type data: data_types.ExpenseData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.description, data.category, data.value, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE EXPENSES SET DESCRIPTION=?, VALUE=?, CATEGORY=?, ACTIVE=? WHERE ID=?'

        # Edita o gasto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def edit_waste(self, data):
        """
        Edita uma entrada do Banco de Dados de Desperdicio
        :param data: dados do desperdicio a ser editado
        :type data: data_types.WasteData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.product_ID, data.amount, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE WASTES SET PRODUCT_ID=?, AMOUNT=?, ACTIVE=? WHERE ID=?'

        # Edita o desperdicio no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def edit_transaction(self, data):
        """
        Edita uma entrada do Banco de Dados de Transaçoes
        :param data: dados do gasto a ser editado
        :type data: data_types.TransactionData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.description, data.value, data.transaction_date,
                 data.category, data.type, data.payment_pendant, 1, data.ID)

        # Edita a transação no BD
        self.cursor.execute("""UPDATE TRANSACTIONS SET DESCRIPTION=?, VALUE=?, TRANSACTION_DATE=?, CATEGORY=?,
                            TYPE=?, PAYMENT_PENDANT=?, ACTIVE=? WHERE ID=?""", _data)
        self.db.commit()

        data.active = True

    def edit_category(self, data):
        """
        Edita uma entrada do Banco de Dados de Categorias
        :param data: dados da categoria a ser editado
        :type data: data_types.TransactionCategoryData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.category, 1, data.ID)

        # Edita a transação no BD
        self.cursor.execute("""UPDATE CATEGORIES SET CATEGORY=?, ACTIVE=? WHERE ID=?""", _data)
        self.db.commit()

        data.active = True

    def edit_cash(self, data):
        """
        Edita uma entrada do Banco de Dados de Caixa
        :param data: dados do registro de caixa a ser editado
        :type data: data_types.CashRegisterData
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data.fund, data.cash, data.withdrawal, 1, data.ID)

        # Edita a transação no BD
        self.cursor.execute("""UPDATE CASH_REGISTER SET FUND=?, CASH=?, WITHDRAWAL=?, ACTIVE=? WHERE ID=?""", _data)
        self.db.commit()

        data.active = True

    def delete_sale(self, sale_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param sale_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE SALES SET ACTIVE=? WHERE ID=?', (active, sale_id))
        self.db.commit()

    def delete_expense(self, expense_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param expense_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE EXPENSES SET ACTIVE=? WHERE ID=?', (active, expense_id))
        self.db.commit()

    def delete_waste(self, waste_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param waste_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE WASTES SET ACTIVE=? WHERE ID=?', (active, waste_id))
        self.db.commit()

    def delete_transaction(self, transaction_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param transaction_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE TRANSACTIONS SET ACTIVE=? WHERE ID=?', (active, transaction_id))
        self.db.commit()

    def delete_category(self, category_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param category_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE CATEGORIES SET ACTIVE=? WHERE ID=?', (active, category_id))
        self.db.commit()

    def delete_cash(self, cash_id, undo=False):
        """
        Deleta uma entrada do BD
        :type undo: bool
        :param undo: Recuperar entrada apagada
        :param cash_id: id da entrada a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute('UPDATE CASH_REGISTER SET ACTIVE=? WHERE ID=?', (active, cash_id))
        self.db.commit()

    def delete_sale_permanently(self, sale_id):
        """
        Delete uma venda do BD
        :param sale_id: id da venda a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM SALES WHERE ID=?', (sale_id, ))
        self.db.commit()

    def delete_expense_permanently(self, expense_id):
        """
        Delete um gasto do BD
        :param expense_id: id do gasto a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM EXPENSES WHERE ID=?', (expense_id, ))
        self.db.commit()

    def delete_waste_permanently(self, waste_id):
        """
        Delete um Desperdicio do BD
        :param waste_id: id do desperdicio a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM WASTES WHERE ID=?', (waste_id, ))
        self.db.commit()

    def delete_transaction_permanently(self, transaction_id):
        """
        Delete uma transação do BD
        :param transaction_id: id da transação a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM TRANSACTIONS WHERE ID=?', (transaction_id, ))
        self.db.commit()

    def delete_category_permanently(self, category_id):
        """
        Delete uma categoria do BD
        :param category_id: id da categoria a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM CATEGORIES WHERE ID=?', (category_id, ))
        self.db.commit()

    def delete_cash_permanently(self, cash_id):
        """
        Delete um registro do BD
        :param cash_id: id do registro a ser deletado
        :return: None
        :rtype: None
        """
        self.cursor.execute('DELETE FROM CASH_REGISTER WHERE ID=?', (cash_id, ))
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

    def transactions_search_id(self, transactions_id):
        """
        Encontra a transação com um determinado ID
        :param transactions_id: id da transação a ser buscada
        :rtype: data_types.TransactionData
        :return: uma transação do BD
        """
        self.cursor.execute("""SELECT * FROM TRANSACTIONS WHERE ID=?""", (transactions_id, ))

        return database2transaction(self.cursor.fetchone())

    def categories_search_id(self, category_id):
        """
        Encontra a categoria com um determinado ID
        :param category_id: id da categoria a ser buscada
        :rtype: data_types.TransactionCategoryData
        :return: uma Categoria do BD
        """
        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ID=?""", (category_id, ))

        return database2transactioncategory(self.cursor.fetchone())

    def cash_search_id(self, cash_id):
        """
        Encontra o registro com um determinado ID
        :param cash_id: id do registro a ser buscado
        :rtype: data_types.CashRegisterData
        :return: um registro do BD
        """
        self.cursor.execute("""SELECT * FROM CASH_REGISTER WHERE ID=?""", (cash_id, ))

        return database2cashregister(self.cursor.fetchone())

    def categories_search_category(self, info, show_all=False):
        """
        Encontra o registro compativel com a info
        :param info: texto a ser buscado
        :type show_all: bool
        :param show_all: Considerar também as entradas apagadas
        :rtype: list[data_types.TransactionCategoryData]
        :return: um registro do BD
        """

        info = u'%' + info + u'%'
        if show_all:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ?""", (info, ))
        else:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ? AND ACTIVE=1""", (info, ))

        temp = self.cursor.fetchall()
        categories_list = list()

        for category in temp:
            categories_list.append(database2transactioncategory(category))

        return categories_list

    def categories_search(self, info):
        """
        Encontra o registro compativel com a info
        :param info: texto a ser buscado
        :rtype: list[data_types.TransactionCategoryData]
        :return: um registro do BD
        """

        # Lista para armazenar todos os produtos compativeis com a busca
        filtered_list = []
        try:
            # converte para integer para buscar por IDs e codigo de barras
            int_info = int(info)

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE ACTIVE=1 AND ID=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))
        except ValueError:
            pass

        info = u'%' + info + u'%'
        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY LIKE ? AND ACTIVE=1""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        categories_list = list()

        for category in filtered_list:
            categories_list.append(database2transactioncategory(category))

        return categories_list

    def cash_search_date(self, date):
        """
        Encontra o registro de uma determinada data
        :param date: data do registro a ser buscado
        :rtype: data_types.CashRegisterData
        :return: um registro do BD
        """
        self.cursor.execute("""SELECT * FROM CASH_REGISTER WHERE RECORD_DATE=?""", (date, ))

        return database2cashregister(self.cursor.fetchone())

    def daily_sales_list(self, date, deleted=False):
        """
        Dados de todos os cadastros em uma data no BD
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param date: data a ser verificada
        :rtype: list[data_types.SaleData]
        :return: uma list com todas as entradas do BD na data
        """
        active = 0 if deleted else 1
        self.cursor.execute("""SELECT * FROM SALES WHERE ACTIVE=? AND RECORD_DATE=?""", (active, date))

        temp = self.cursor.fetchall()
        sales_list = list()

        for sale in temp:
            sales_list.append(database2sale(sale))

        return sales_list

    def daily_expenses_list(self, date, deleted=False):
        """
        Dados de todos os cadastros em uma data no BD
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param date: data a ser verificada
        :rtype: list[data_types.ExpenseData]
        :return: uma list com todas as entradas do BD na data
        """
        active = 0 if deleted else 1
        self.cursor.execute("""SELECT * FROM EXPENSES WHERE ACTIVE=? AND RECORD_DATE=?""", (active, date))

        temp = self.cursor.fetchall()
        expenses_list = list()

        for expense in temp:
            expenses_list.append(database2expense(expense))

        return expenses_list

    def daily_wastes_list(self, date, deleted=False):
        """
        Dados de todos os cadastros em uma data no BD
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param date: data a ser verificada
        :rtype: list[data_types.WasteData]
        :return: uma list com todas as entradas do BD na data
        """
        active = 0 if deleted else 1
        self.cursor.execute("""SELECT * FROM WASTES WHERE ACTIVE=? AND RECORD_DATE=?""", (active, date))

        temp = self.cursor.fetchall()
        wastes_list = list()

        for waste in temp:
            wastes_list.append(database2waste(waste))

        return wastes_list

    def daily_transactions_list(self, date, deleted=False):
        """
        Dados de todos os cadastros em uma data no BD
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param date: data a ser verificada
        :rtype: list[data_types.TransactionData]
        :return: uma list com todas as entradas do BD na data
        """
        active = 0 if deleted else 1
        self.cursor.execute("""SELECT * FROM TRANSACTIONS WHERE ACTIVE=? AND TRANSACTION_DATE=?""", (active, date))

        temp = self.cursor.fetchall()
        transactions_list = list()

        for transaction in temp:
            transactions_list.append(database2transaction(transaction))

        return transactions_list

    def monthly_sales_list(self, month, deleted=False):
        """
        Dados de todas as entradas cadastrados em um determinado mes
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.SaleData]
        :return: uma list com todas as entradas do BD no mes
        """
        active = 0 if deleted else 1

        month += '%'

        self.cursor.execute("""SELECT * FROM SALES WHERE ACTIVE=? AND RECORD_DATE LIKE ? ORDER BY RECORD_DATE""",
                            (active, month))

        temp = self.cursor.fetchall()
        sales_list = list()

        for sale in temp:
            sales_list.append(database2sale(sale))

        return sales_list

    def monthly_expenses_list(self, month, deleted=False):
        """
        Dados de todas as entradas cadastrados em um determinado mes
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.ExpenseData]
        :return: uma list com todas as entradas do BD no mes
        """
        active = 0 if deleted else 1

        month += '%'

        self.cursor.execute("""SELECT * FROM EXPENSES WHERE ACTIVE=? AND RECORD_DATE LIKE ? ORDER BY RECORD_DATE""",
                            (active, month))

        temp = self.cursor.fetchall()
        expenses_list = list()

        for expense in temp:
            expenses_list.append(database2expense(expense))

        return expenses_list

    def monthly_wastes_list(self, month, deleted=False):
        """
        Dados de todas as entradas cadastrados em um determinado mes
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.WasteData]
        :return: uma list com todas as entradas do BD no mes
        """
        active = 0 if deleted else 1

        month += '%'

        self.cursor.execute("""SELECT * FROM WASTES WHERE ACTIVE=? AND RECORD_DATE LIKE ? ORDER BY RECORD_DATE""", (active, month))

        temp = self.cursor.fetchall()
        wastes_list = list()

        for waste in temp:
            wastes_list.append(database2waste(waste))

        return wastes_list

    def monthly_transactions_list(self, month, transaction_type=-1, deleted=False):
        """
        Dados de todas as entradas cadastrados em um determinado mes
        :type transaction_type: int
        :param transaction_type: Tipo de entrada a ser listada
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :param month: mes no formato yyyy-mm a ser verificado
        :type month: str
        :rtype: list[data_types.TransactionData]
        :return: uma list com todas as entradas do BD no mes
        """
        active = 0 if deleted else 1

        month += '%'

        if transaction_type == -1:
            self.cursor.execute("""SELECT * FROM TRANSACTIONS WHERE ACTIVE=? AND TRANSACTION_DATE LIKE ?
                                ORDER BY TRANSACTION_DATE""", (active, month))
        else:
            self.cursor.execute("""SELECT * FROM TRANSACTIONS WHERE ACTIVE=? AND TYPE=? AND TRANSACTION_DATE LIKE ?
                                ORDER BY TRANSACTION_DATE""", (active, transaction_type, month))

        temp = self.cursor.fetchall()
        transactions_list = list()

        for transaction in temp:
            transactions_list.append(database2transaction(transaction))

        return transactions_list

    def list_record_dates(self, transactions=False, deleted=False):
        """
        Obtém uma lista com todas as datas com dados registrados
        :type transactions: bool
        :param transactions: Mostrar também as datas das entradas de transações
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :return: Lista com todos os dias com movimento registrado
        :rtype: list[str]
        """

        active = 0 if deleted else 1

        records = list()

        self.cursor.execute('SELECT RECORD_DATE FROM WASTES WHERE ACTIVE=?', (active, ))
        records = list(set(records + self.cursor.fetchall()))

        self.cursor.execute('SELECT RECORD_DATE FROM SALES WHERE ACTIVE=?', (active, ))
        records = list(set(records + self.cursor.fetchall()))

        self.cursor.execute('SELECT RECORD_DATE FROM EXPENSES WHERE ACTIVE=?', (active, ))
        records = list(set(records + self.cursor.fetchall()))

        if transactions:
            self.cursor.execute('SELECT RECORD_DATE FROM TRANSACTIONS WHERE ACTIVE=?', (active, ))
            records = list(set(records + self.cursor.fetchall()))

        for i in range(len(records)):
            records[i] = records[i][0]

        records.sort(reverse=True)

        return records

    def list_transactions_dates(self, deleted=False):
        """
        Obtém uma lista com todas as datas com transações registradas
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :return: Lista com todos os dias com movimento registrado
        :rtype: list[str]
        """

        active = 0 if deleted else 1

        self.cursor.execute('SELECT RECORD_DATE FROM TRANSACTIONS WHERE ACTIVE=? GROUP BY RECORD_DATE', (active, ))
        records = self.cursor.fetchall()

        for i in range(len(records)):
            records[i] = records[i][0]

        records.sort(reverse=True)

        return records

    def categories_list(self, deleted=False):
        """
        Encontra o registro compativel com a info
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :rtype: list[data_types.TransactionCategoryData]
        :return: um registro do BD
        """

        active = 0 if deleted else 1

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ACTIVE=?""", (active, ))

        temp = self.cursor.fetchall()
        categories_list = list()

        for category in temp:
            categories_list.append(database2transactioncategory(category))

        return categories_list

    def sales_list_pendant(self, deleted=False):
        """
        Dados de todas as entradas cadastrados que estão com pagamento pendente
        :type deleted: bool
        :param deleted: Mostrar entradas apagadas apenas
        :rtype: list[data_types.SaleData]
        :return: uma list com todas as entradas do BD no mes
        """
        active = 0 if deleted else 1

        self.cursor.execute("""SELECT * FROM SALES WHERE ACTIVE=? AND PAYMENT_PENDANT=1 ORDER BY RECORD_DATE""",
                            (active, ))

        temp = self.cursor.fetchall()
        sales_list = list()

        for sale in temp:
            sales_list.append(database2sale(sale))

        return sales_list


def database2delivery(database_list):
    """
    Converte uma lista obtidada do banco de dados em um objeto venda
    :param database_list: lista obtidada do db contendo dados de uma venda
    :type database_list: tuple
    :return: Objeto Venda
    :rtype: data_types.DeliveryData
    """
    if not database_list:
        return None

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
    data.active = True if database_list[11] else False

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
            TELEPHONE CHAR(11), DELIVERY_DATE CHAR(10) NOT NULL, DELIVERY_TIME CHAR(8) NOT NULL,
            OBS TEXT, ACTIVE INT(1) NOT NULL)''')

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
                 data.date, data.hour, data.obs, 1)

        cmd = 'INSERT INTO DELIVERIES (SALE_ID, CLIENT, RECEIVER, STATE, CITY, ADDRESS, TELEPHONE, '
        cmd += 'DELIVERY_DATE, DELIVERY_TIME, OBS, ACTIVE) VALUES (?,?,?,?,?,?,?,?,?,?,?)'

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
                 data.date, data.hour, 1, data.ID)

        # Prepara a linha de comando

        cmd = 'UPDATE DELIVERIES SET CLIENT=?, RECEIVER=?, STATE=?, CITY=?, ADDRESS=?, TELEPHONE=?, '
        cmd += 'DELIVERY_DATE=?, DELIVERY_HOUR=?, OBS=?, ACTIVE=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

        data.active = True

    def delete_delivery(self, delivery_id, undo=False):
        """
        Delete uma entrega do BD
        :type undo: bool
        :param undo: Recuperar apagado
        :param delivery_id: id da entrega a ser deletada
        :return: None
        :rtype: None
        """
        active = 1 if undo else 0

        self.cursor.execute("""UPDATE DELIVERIES SET ACTIVE=? WHERE ID=?""", (active, delivery_id))
        self.db.commit()

    def delete_delivery_permanently(self, delivery_id):
        """
        Delete uma entrega do BD
        :param delivery_id: id da entrega a ser deletada
        :return: None
        :rtype: None
        """
        self.cursor.execute("""DELETE FROM DELIVERIES WHERE ID=?""", (delivery_id, ))
        self.db.commit()

    def deliveries_search_sale(self, sale_id):
        """
        Encontra a entrega de uma determinada venda
        :param sale_id: id da venda a ser buscada
        :rtype: data_types.DeliveryData
        :return: uma entrega do BD
        """
        self.cursor.execute("""SELECT * FROM DELIVERIES WHERE SALE_ID=?""", (sale_id, ))

        return database2delivery(self.cursor.fetchone())

    def deliveries_search_id(self, delivery_id):
        """
        Encontra a entrega com um determinado ID
        :param delivery_id: id da entrega a ser buscada
        :rtype: data_types.DeliveryData
        :return: uma entrega do BD
        """
        self.cursor.execute("""SELECT * FROM DELIVERIES WHERE ID=?""", (delivery_id, ))

        return database2delivery(self.cursor.fetchone())

    def deliveries_list(self, show_all=False):
        """
        Dados de todas as entregas programadas
        :param show_all: Mostrar todas as entregas registradas ou só as ativas
        :type show_all: bool
        :rtype: list[data_types.DeliveryData]
        :return: uma list com todas as entregas do BD
        """

        if not show_all:
            self.cursor.execute("""SELECT * FROM DELIVERIES WHERE ACTIVE=1 ORDER BY DELIVERY_DATE""")

        else:
            self.cursor.execute("""SELECT * FROM DELIVERIES ORDER BY DELIVERY_DATE""")

        deliveries_list = list()

        for delivery in self.cursor.fetchall():
            deliveries_list.append(database2delivery(delivery))

        return deliveries_list
