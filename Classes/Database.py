# -*- coding: utf-8 -*-

import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:

    def __init__(self, database):
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()
        self.checkIfTablesExist()

    def query_exec(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit
            return {"State": True, "Result": self.cursor.fetchall()}
        except Exception as e:
            self.conn.rollback
            return {"State": False, "Result": e}

    def checkIfTablesExist(self):
        tables = self.query_exec("select name from sqlite_master where type = 'table';")
        createUsers = True

        for table in tables.get('Result'):
            if table.get('name') == 'users':
                createUsers = False

        if createUsers:
            self.query_exec("CREATE TABLE users "
                                "(Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "
                                "Name VARCHAR (255) DEFAULT NULL, "
                                "Type VARCHAR (32) DEFAULT NULL, "
                                "Phone VARCHAR (30) DEFAULT NULL, "
                                "Email VARCHAR (255) DEFAULT NULL, "
                                "user VARCHAR (100) DEFAULT NULL, "
                                "pass VARCHAR (100) DEFAULT NULL );")

            b = self.query_exec("INSERT INTO users (Id, Name, Type, user, pass) VALUES (1, 'Admin', 'admin', 'admin', 'admin');")
            print(b)


    def db_close(self):
        self.conn.close()

#a = Database('database.db')