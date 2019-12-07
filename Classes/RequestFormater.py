# -*- coding: utf-8 -*-

import logging

from flask import request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            record.method = request.method
            record.url = request.url
            record.remote_addr = request.remote_addr
        except RuntimeError:
            record.method = '-'
            record.url = '-'
            record.remote_addr = '-'
        return super().format(record)