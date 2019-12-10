# -*- coding: utf-8 -*-

import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:

    def __init__(self, database):
        self.conn = sqlite3.connect(database, check_same_thread=False, isolation_level=None)
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
        createNotes = True
        createGuardians = True
        createStudents = True
        createClasses = True
        createGuardianRelation = True
        createClassRelation = True

        for table in tables.get('Result'):
            if table.get('name') == 'users':
                createUsers = False
            if table.get('name') == 'notes':
                createNotes = False
            if table.get('name') == 'guardians':
                createGuardians = False
            if table.get('name') == 'students':
                createStudents = False
            if table.get('name') == 'classes':
                createClasses = False
            if table.get('name') == 'guardianRelation':
                createGuardianRelation = False
            if table.get('name') == 'classRelation':
                createClassRelation = False

        if createUsers:
            self.query_exec("CREATE TABLE users "
                                "(Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "
                                "Name VARCHAR (255) DEFAULT NULL, "
                                "Type VARCHAR (32) DEFAULT NULL, "
                                "Phone VARCHAR (30) DEFAULT NULL, "
                                "Email VARCHAR (255) DEFAULT NULL, "
                                "user VARCHAR (100) DEFAULT NULL, "
                                "pass VARCHAR (100) DEFAULT NULL );")

            self.query_exec("INSERT INTO users "
                            "(Id, Name, Type, user, pass) "
                            "VALUES "
                            "(1, 'Admin', 'admin', 'admin', '21232f297a57a5a743894a0e4a801fc3');")

        if createNotes:
            self.query_exec("CREATE TABLE notes "
                            "( Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "
                            "Name VARCHAR (64) NOT NULL, "
                            "description VARCHAR , "
                            "createdAt DATETIME NOT NULL);")

        if createGuardians:
            self.query_exec("CREATE TABLE guardians "
                            "( Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                            "name VARCHAR (255) NOT NULL, "
                            "phone VARCHAR (32) NOT NULL, "
                            "email VARCHAR (255));")

        if createStudents:
            self.query_exec("CREATE TABLE students "
                            "( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
                            "name VARCHAR (255) NOT NULL );")

        if createClasses:
            self.query_exec("CREATE TABLE classes "
                            "( Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "
                            "name VARCHAR (255) NOT NULL );")

        if createGuardianRelation:
            self.query_exec("CREATE TABLE guardianRelation "
                            "( GuardianId INTEGER NOT NULL REFERENCES guardians (Id), "
                            "Relation VARCHAR (32), "
                            "StudentId INTEGER REFERENCES students (id) NOT NULL ); ")

        if createClassRelation:
            self.query_exec("CREATE TABLE classRelation "
                            "( ClassId INTEGER REFERENCES classes (Id) NOT NULL, "
                            "StudentId INTEGER NOT NULL REFERENCES students (id) );")

    def db_close(self):
        self.conn.close()
