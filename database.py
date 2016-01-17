#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import core


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
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['barcode'], data['description'], data['category'], data['price'], data['amount'],
                 0, data['supplier'], data['obs'], data['time'], data['date'])
        cmd = 'INSERT INTO INVENTORY (BARCODE, DESCRIPTION, CATEGORY, PRICE, AMOUNT, SOLD, SUPPLIER, OBS, '
        cmd += 'RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?)'
        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_product(self, product_id, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param product_id: id do produto a ser alterado
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['barcode'], data['description'], data['category'], data['price'], data['amount'],
                 data['supplier'], data['obs'], data['time'], data['date'], product_id)

        # Prepara a linha de comando
        cmd = 'UPDATE INVENTORY SET BARCODE=?, DESCRIPTION=?, CATEGORY=?, PRICE=?, '
        cmd += 'AMOUNT=?, SUPPLIER=?, OBS=?, RECORD_TIME=?, RECORD_DATE=? WHERE ID=?'
        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_product(self, product_id):
        """
        Delete um produto do BD
        :param product_id: id do produto a ser deletado
        :return:
        """
        self.cursor.execute('DELETE FROM INVENTORY WHERE ID=?', (product_id, ))
        self.db.commit()

    def update_product_amount(self, product_id, amount):
        """
        Atualiza a quantidade de um produto em estoque
        :param product_id: id do produto tendo o estoque atualizado
        :param amount: nova quantidade em estoque
        :return:
        """
        self.cursor.execute('UPDATE INVENTORY SET AMOUNT = ? where ID=?', (amount, product_id))
        self.db.commit()

    def update_product_stock(self, product_id, change):
        """
        Atualiza a quantidade de um produto em estoque
        :param product_id: id do produto tendo o estoque atualizado
        :param change: variação no estoque
        :return:
        """
        self.cursor.execute('UPDATE INVENTORY SET AMOUNT=AMOUNT+? where ID=?', (change, product_id))
        self.db.commit()

    def barcode_search(self, barcode):
        """
        Busca o item com um codigo de barras especifico no BD
        :param barcode: Codigo de barras sendo buscado
        :return:
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (barcode, ))
        return self.cursor.fetchone()

    def inventory_search_id(self, product_id):
        """
        Busca o item com um ID especifico no BD
        :param product_id: ID do produto sendo buscado sendo buscado
        :return:
        """

        # Faz o BD mostrar apenas o item com um codigo de barras especifico
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE ID=?""", (product_id, ))
        return self.cursor.fetchone()

    def inventory_search(self, info):    # TODO Atualmente apenas busca por igualdade, melhorar a busca
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

        return filtered_list

    def product_list(self):
        """
        Dados de todos os produtos cadastrados
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM INVENTORY ORDER BY DESCRIPTION""")
        return self.cursor.fetchall()

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

        return filtered_list

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
        return self.cursor.fetchone()

    def category_id(self, info):
        """
        Faz uma busca por um dado generico no banco de dados.
        Dada uma String busca por correspondecia por ids, categoria, e NCM
        :param info: String com o dado a ser buscado
        :return: List com todos as categorias compativeis com a busca
        """

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY=?""", (info, ))
        return self.cursor.fetchone()

    def categories_list(self):
        """
        Fornece todas as categorias presentes no BD
        :return: Uma lista com todos os elementos do BD
        """
        self.cursor.execute("""SELECT * FROM CATEGORIES ORDER BY CATEGORY""")
        return self.cursor.fetchall()


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
            CPF CHAR(11), CEP CHAR(8), STATE CHAR(2), CITY TEXT, DISTRICT TEXT, ADRESS TEXT,
            OBS TEXT, LAST_SALE CHAR(10), RECORD_DATE CHAR(10) NOT NULL)''')

        self.db.commit()

    def insert_client(self, data):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['adress'], data['obs'], data['date'])

        cmd = 'INSERT INTO CLIENTS (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADRESS, OBS, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'

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
                 data['state'], data['city'], data['district'], data['adress'], data['obs'], client_id)

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADRESS=?, OBS=? WHERE ID=?'

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

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ADRESS LIKE ? ORDER BY NAME""", (info, ))
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
            VALUE REAL, PAYMENTE TEXT, CLIENT INTEGER, TELEPHONE CHAR(11), CEP CHAR(8), STATE CHAR(2), CITY TEXT, DISTRICT TEXT, ADRESS TEXT,
            RECORD_TIME CHAR(8) NOT NULL, RECORD_DATE CHAR(10) NOT NULL)''', (day, ))

        self.db.commit()

    def insert_sale(self, data, ):
        """
        Insere uma nova entrada no Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['adress'], data['obs'], data['time'], data['date'])

        cmd = 'INSERT INTO INVENTORY (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADRESS, OBS, RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_sale(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['name'], data['sex'], data['birth'], data['email'], data['tel'], data['cpf'], data['cep'],
                 data['state'], data['city'], data['district'], data['adress'], data['obs'])

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADRESS=?, OBS=? WHERE ID=?'

        # Edita o produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def delete_sale(self, product_id):
        """
        Delete um produto do BD
        :param product_id: id do produto a ser deletado
        :return:
        """
        self.cursor.execute('DELETE FROM CLIENTS WHERE ID=?', (product_id, ))
        self.db.commit()

    def sales_search(self, info):    # TODO Atualmente apenas busca por igualdade, melhorar a busca
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

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ADRESS LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE OBS LIKE ?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        return filtered_list

    def daily_sales_list(self, day):
        """
        Dados de todas as vendas cadastrados em um determinado dia
        :param day: dia do mes a ser verificado
        :rtype: list
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM ?""", (day, ))
        return self.cursor.fetchall()


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
                 data['state'], data['city'], data['district'], data['adress'], data['obs'], data['time'], data['date'])

        cmd = 'INSERT INTO INVENTORY (NAME, SEX, BIRTH, EMAIL, TELEPHONE, CPF, CEP, STATE, CITY, '
        cmd += 'DISTRICT, ADRESS, OBS, RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

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
                 data['state'], data['city'], data['district'], data['adress'], data['obs'])

        # Prepara a linha de comando

        cmd = 'UPDATE CLIENTS SET NAME=?, SEX=?, BIRTH=?, EMAIL=?, TELEPHONE=?, CPF=?, CEP=?, STATE=?, CITY=?, '
        cmd += 'DISTRICT=?, ADRESS=?, OBS=? WHERE ID=?'

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

        self.cursor.execute("""SELECT * FROM CLIENTS WHERE ADRESS LIKE ?""", (info, ))
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
