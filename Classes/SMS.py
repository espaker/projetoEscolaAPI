import requests

class SMS:

    def __init__(self, ttvToken):
        self.url = 'https://api.totalvoice.com.br/sms'
        self.headers = {'content-type': 'application/json', 'Accept': 'application/json',
                   'Access-Token': ttvToken}

    def sendSMS(self, phone, message, waitAnswer=False, tags=False, multiSMS=False, schedule=False):
        if not multiSMS and len(message) > 100:
            return {'State': False, 'Message': 'Para enviar SMS com mais de 100 caracteres e necessario o parametro "multiSMS"'}
        data = {"numero_destino": phone, "mensagem": message}
        if waitAnswer:
            data['resposta_usuario'] = waitAnswer
        if tags:
            data['tags'] = tags
        if multiSMS:
            data['multi_sms'] = multiSMS
        if schedule:
            data['data_criacao'] = schedule
        r = requests.post(self.url, headers=self.headers, json=data, timeout=60)
        if r.status_code in [200, 201, 202]:
            return {'State': True, 'Message': r.json()}
        return {'State': False, 'Message': r.json()}
