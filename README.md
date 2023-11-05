# Xarxes i Serveis: Practica 2
Practica 2 Protocol TFTP

## Executar
### Setup
Importar dependencies 
```
pip3 install -r requirements.txt
```


Executar servidor (en el directori del projecte) 
```
ptftpd -D -p 6969 -r lo ./
```

### Script
Llegir arxiu
```
python3 tftp_client.py r <filename> <port opcional (def: 6969)>
```


Escriure arxiu
```
python3 tftp_client.py w <filename> <port opcional (def: 6969)>
```
