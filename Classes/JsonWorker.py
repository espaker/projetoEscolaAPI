# -*- coding: utf-8 -*-

import json
import datetime
import decimal

from flask import request, Response


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super(self.__class__, self).default(obj)

class JsonFormater:

    def json_result(_code, _body):
        response = json.dumps(_body, cls=EnhancedJSONEncoder)
        callback = request.args.get('callback')
        if callback is not None:
            response = callback + "({})".format(response)

        return Response(response, mimetype='application/json'), _code