# -*- coding: utf-8 -*-

import os
import sys
import logging
import signal
import requests

from flask import Flask, request
from flask_cors import CORS
from logging.handlers import RotatingFileHandler
from cheroot.wsgi import Server as WSGIServer
from cheroot.ssl.builtin import BuiltinSSLAdapter

from Classes.Utils import Utils
from Classes.Parser import Parser
from Classes.RequestFormater import RequestFormatter
from Classes.Cache_control import CacheControl
from Classes.JsonWorker import JsonFormater
from Classes.Database import Database
from  Classes.SMS import SMS

app_version = '1.0.1'

execute = None
token = None
server = None
database = None
sms = None

cache_control = CacheControl()
json_result = JsonFormater.json_result

app = Flask(__name__)
CORS(app)


def getClasses():
    global database
    retunedJson = []
    for cls in database.query_exec('SELECT * FROM classes;').get('Result'):
        retunedJson.append({"id": cls.get('Id'), "name": cls.get('name'), "students": getStudents(cls.get('Id'))})
    return retunedJson


def getStudents(classId):
    global database
    students = []
    for student in database.query_exec('SELECT s.id, s.name FROM students s inner join classRelation cr on s.id = cr.StudentId WHERE cr.ClassId = {}'.format(classId)).get('Result'):
        students.append({"id": student.get("id"), "name": student.get("name"), "parents": getParents(student.get("id"))})
    return students


def getParents(studentId):
    global database
    parents = []
    for parent in database.query_exec('SELECT g.id, g.name, g.phone FROM guardians g inner join guardianRelation gr on g.Id = gr.UserId WHERE gr.StudentId = {}'.format(studentId)).get('Result'):
        parents.append({"user_id": parent.get("Id"), "name": parent.get("name"), "phone": parent.get("phone")})
    return parents


@app.route('/api/v1/testeEnvioSMS', methods=['POST'])
def testeEnvioSMS():
    global database
    log_main.info('--> /api/v1/testeEnvioSMS [POST]')
    try:
        tkn = request.headers['token_auth']
        if token == tkn:
            try:
                if request.json.get('token_totalVoice', '') == '' or request.json.get('phone', '') == '' or request.json.get('message', '') == '':
                    return json_result(400, {'state': 'error', 'message': 'Parametros invalidos'})
                url = 'https://api.totalvoice.com.br/sms'
                headers = {'content-type': 'application/json', 'Accept': 'application/json', 'Access-Token': request.json.get('token_totalVoice')}
                data = {"numero_destino": request.json.get('phone'), "mensagem": request.json.get('message')}
                r = requests.post(url, headers=headers, json=data, timeout=60)
                if r.status_code in [200, 201, 202]:
                    rjson = r.json()
                    return json_result(201, {'state': 'Sucess', 'message': rjson})
                else:
                    log_main.exception('--> /api/v1/testeEnvioSMS [POST]: [{}]'.format(r))
                    return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
            except Exception as e:
                log_main.exception('--> /api/v1/testeEnvioSMS [POST]: [{}]'.format(e))
                return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Invalido'})
    except:
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Não Informado'})

app.route('/api/v1/sendSMS', methods=['POST'])
def sendSMS():
    global sms
    log_main.info('--> /api/v1/sendSMS [POST]')
    try:
        tkn = request.headers['token_auth']
        if token == tkn:
            try:
                if request.json.get('token_totalVoice', '') == '' or request.json.get('phone', '') == '' or request.json.get('message', '') == '':
                    return json_result(400, {'state': 'error', 'message': 'Parametros invalidos'})
                url = 'https://api.totalvoice.com.br/sms'
                headers = {'content-type': 'application/json', 'Accept': 'application/json', 'Access-Token': request.json.get('token_totalVoice')}
                data = {"numero_destino": request.json.get('phone'), "mensagem": request.json.get('message')}
                r = requests.post(url, headers=headers, json=data, timeout=60)
                if r.status_code in [200, 201, 202]:
                    rjson = r.json()
                    return json_result(200, {'state': 'Sucess', 'message': rjson})
                else:
                    log_main.exception('--> /api/v1/sendSMS [POST]: [{}]'.format(r))
                    return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
                return json_result(200, {'state': 'Sucess', 'message': request.json})
            except Exception as e:
                log_main.exception('--> /api/v1/testeEnvioSMS [POST]: [{}]'.format(e))
                return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Invalido'})
    except:
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Não Informado'})

@app.route('/api/v1/sendNote', methods=['POST'])
def sendNote():
    global database, sms
    log_main.info('--> /api/v1/sendNote [POST]')
    try:
        tkn = request.headers['token_auth']
        if token == tkn:
            try:
                if request.json.get('note', '') == '' or request.json.get('students', '') == '':
                    return json_result(400, {'state': 'error', 'message': 'Parametros invalidos'})
                note = database.query_exec('SELECT description FROM notes WHERE Id = {}'.format(request.json.get('note'))).get('Result')[0]['description']
                students = ','.join(map(str, request.json.get('students')))
                query = 'SELECT g.phone FROM guardians g inner join guardianRelation gr on g.Id = gr.UserId WHERE gr.StudentId in ({})'.format(students)
                for phone in database.query_exec(query).get('Result'):
                    message = sms.sendSMS(phone, note, multiSMS=True)
                    if not message.get('State'):
                        log_main.exception('--> /api/v1/sendNote [POST]: [{}]'.format(message.get('Message')))
                        return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
                return json_result(200, {'state': 'Sucess', 'message': message.get('Message')})
            except Exception as e:
                log_main.exception('--> /api/v1/sendNote [POST]: [{}]'.format(e))
                return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Invalido'})
    except:
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Não Informado'})

@app.route('/api/v1/getDataBaseJson', methods=['GET'])
def getDataBaseJson():
    global database
    log_main.info('--> /api/v1/getDataBaseJson [GET]')
    try:
        tkn = request.headers['token_auth']
        if token == tkn:
            try:
                returnData = {"users": database.query_exec('select * from users').get('Result'),
                              "notes": database.query_exec('select * from notes').get('Result'),
                              "classes": getClasses()
                              }

                return json_result(200, {'state': 'Sucess', 'message': returnData})
            except Exception as e:
                log_main.exception('--> /api/v1/getDataBaseJson [get]: [{}]'.format(e))
                return json_result(500, {'state': 'error', 'message': 'Erro Desconhecido'})
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Invalido'})
    except:
        return json_result(401, {'state': 'unauthorized', 'message': 'Token Não Informado'})


def initiate():
    log_main.info('Iniciando a API versão: {}'.format(app_version))

    signal.signal(signal.SIGTERM, finalize)
    signal.signal(signal.SIGINT, finalize)

    global token, database, sms

    token = conf.get('Auth', 'Token', fallback='14acd1c3b2f50c1e7354668f7d0b4057')

    ttvToken = open(os.path.join(workdir, conf.get('Auth', 'TokenTTV', fallback=False)), 'r')
    sms = SMS(ttvToken.readline())
    ttvToken.close()

    log_main.warning('Iniciando conexão com banco de dados ...')
    try:
        db = os.path.join(workdir, conf.get('Database', 'Database', fallback='data.db'))
        database = Database(db)
    except Exception as e:
        log_main.exception('Erro ao iniciar a conexão com o banco de dados: [{}]'.format(e))

    _port = conf.getint('Flask', 'Port', fallback=8860)
    _host = conf.get('Flask', 'Host', fallback='0.0.0.0')
    _threads = conf.getint('Flask', 'Threads', fallback=100)
    _ssl_cert = os.path.join(workdir, 'SSL', conf.get('Flask', 'SSL_Cert', fallback=''))
    _ssl_key = os.path.join(workdir, 'SSL', conf.get('Flask', 'SSL_Key', fallback=''))
    try:
        _ssl_enabled = os.path.isfile(_ssl_cert) and os.path.isfile(_ssl_key)
    except Exception:
        _ssl_enabled = False

    if len(sys.argv) > 1:
        if sys.argv[1] in ('-v', '--version'):
            print('API')
            print('Versão: {}'.format(app_version))
            sys.exit(0)
        elif sys.argv[1] in ('-d', '--debug'):
            app.run(host=_host, port=_port, threaded=True, debug=True)
        else:
            print('ERRO | Parâmetro desconhecido: {}'.format(sys.argv))
            sys.exit(2)
    else:
        global server
        server = WSGIServer(bind_addr=(_host, _port), wsgi_app=app, numthreads=_threads)
        if _ssl_enabled:
            server.ssl_adapter = BuiltinSSLAdapter(_ssl_cert, _ssl_key)
        log_main.warning('Iniciando flask ...')
        server.start()


def finalize(signum, desc):
    global execute, server, database
    log_main.info('Recebi o sinal [{}] Desc [{}], finalizando...'.format(signum, desc))

    log_main.warning('Limpando Cache Control ...')
    cache_control.clear()

    log_main.warning('Encerrando conexão com banco de dados ...')
    database.db_close()

    if server is not None:
        log_main.warning('Parando Serviço ...')
        server.stop()
    if execute:
        execute = False
    else:
        sys.exit(2)


if __name__ == '__main__':
    execute = True
    workdir = Utils.get_workdir()
    conf = Parser(os.path.join(workdir, 'config.ini')).conf_get()
    _level = conf.getint('Debug', 'Level', fallback=3)
    debug_dir = os.path.join(workdir, 'debug')
    log_file_path = os.path.join(debug_dir, 'API.log')
    if not os.path.exists(debug_dir):
        os.mkdir(debug_dir, 0o775)
    log_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 10, backupCount=10)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(RequestFormatter(
        '[%(asctime)s] | %(levelname)s | %(name)s | %(remote_addr)s | %(method)s | %(url)s | %(message)s'))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    log_main = logging.getLogger('API:' + str(os.getpid()))
    app.logger.addHandler(log_handler)
    app.debug = True

    initiate()
