# Api Gestao Escolar Tech

####Install:
    Installing python modules:
    # python3 -m pip install flask flask_cors requests cheroot flask_apidoc
    
    Configure your totalvoice token
    # echo <TOKEN> > token 
    
    Creating linux service:
    # cd <API Dir>
    Open "ApiGestaoEscolar.service" and configure <API Dir>
    # cp ApiGestaoEscolar.service /etc/systemd/system/
    # systemctl start ApiGestaoEscolar.service
    # systemctl enable ApiGestaoEscolar.service
    # systemctl status ApiGestaoEscolar.service
    
    Then status must been return "active (running)"
    
    
###Routes:
    [POST] <IP>:8866/api/v1/testeEnvioSMS
    [GET] <IP>:8866/api/v1/getDataBaseJson
    [POST] <IP>:8866/api/v1/sendNote
    
####Team

- Ricardo Alves
- Leonardo
- Eduardo Quintino
- Espaker
- Felipe

####Another project links
- https://github.com/ricardotecnicob/gestaoescolartech_documentacao
- https://github.com/ricardotecnicob/gestaoescolartech_frontend	
- https://github.com/ricardotecnicob/gestaoescolartech_mobile