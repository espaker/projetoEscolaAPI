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

    def query_exec(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit
            return {"State": True, "Result": self.cursor.fetchall()}
        except Exception as e:
            self.conn.rollback
            return {"State": False, "Result": e}

    def db_close(self):
        self.conn.close()