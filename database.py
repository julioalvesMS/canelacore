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
            BARCODE CHAR(32) NOT NULL UNIQUE, DESCRIPTION TEXT NOT NULL, CATEGORY INTEGER NOT NULL,
            PRICE REAL NOT NULL, AMOUNT INTEGER, SUPPLIER TEXT, OBS TEXT, RECORD_TIME CHAR(8) NOT NULL,
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
                 data['supplier'], data['obs'], data['time'], data['date'])
        cmd = 'INSERT INTO INVENTORY (BARCODE, DESCRIPTION, CATEGORY, PRICE, AMOUNT, SUPPLIER, OBS, '
        cmd += 'RECORD_TIME, RECORD_DATE) VALUES (?,?,?,?,?,?,?,?,?)'
        # Insere o novo produto no BD
        self.cursor.execute(cmd, _data)
        self.db.commit()

    def edit_product(self, data):
        """
        Edita uma entrada do Banco de Dados de Produtos
        :param data: dados do novo produto a ser inserida
        """

        # Transfere os dados do dict mandado para um tuple
        _data = (data['barcode'], data['description'], data['category'], data['price'], data['amount'],
                 data['supplier'], data['obs'], data['time'], data['date'])

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
        return self.cursor.fetchall()

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

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE BARCODE=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

            self.cursor.execute("""SELECT * FROM INVENTORY WHERE CATEGORY=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            int_info = -1

        self.cursor.execute("""SELECT * FROM INVENTORY WHERE DESCRIPTION=?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM INVENTORY WHERE SUPPLIER=?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        # Busca a entrada na tabela de categorias, compara com o nome da categoria
        category_list = list()

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY=?""", (info, ))
        category_list = list(set(category_list + self.cursor.fetchall()))

        # Caso a entrada seja numerica, busca pelo NCM
        if int_info != -1:
            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE NCM=?""", (info, ))
            category_list = list(set(category_list + self.cursor.fetchall()))

        # Seleciona todos os produtos da categoria compativel com a busca
        for category in category_list:
            print type(category)
            self.cursor.execute("""SELECT * FROM INVENTORY WHERE CATEGORY=?""", (category[0], ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        return filtered_list

    def product_list(self):
        """
        Dados de todos os produtos cadastrados
        :return: uma list com todos os produtos do BD
        """
        self.cursor.execute("""SELECT * FROM INVENTORY WHERE CATEGORY=?""")
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

            self.cursor.execute("""SELECT * FROM CATEGORIES WHERE ID=?""", (int_info, ))
            filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        except ValueError:
            # Caso não seja possivel converter para INTEGER pula as IDs e continua com as outras buscas
            pass

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE NCM=?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        self.cursor.execute("""SELECT * FROM CATEGORIES WHERE CATEGORY=?""", (info, ))
        filtered_list = list(set(filtered_list + self.cursor.fetchall()))

        return filtered_list

    def categories_list(self):
        """
        Fornece todas as categorias presentes no BD
        :return: Uma lista com todos os elementos do BD
        """
        self.cursor.execute("""SELECT * FROM CATEGORIES""")
        return self.cursor.fetchall()
