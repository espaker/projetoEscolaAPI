# -*- coding: utf-8 -*-

from configparser import ConfigParser


class Parser:

    def __init__(self, conf_file, encoding='utf-8'):
        self.config = ConfigParser()
        self.config.read(conf_file, encoding)

    def conf_get(self):
        return self.config