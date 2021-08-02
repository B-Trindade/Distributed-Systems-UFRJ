# Programacao com sockets em python: script ativo

import socket

HOST = ''
PORT = 8000

# Descritor socket
sckt = socket.socket() # default: socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincular endereco e porta
sckt.bind((HOST, PORT))

sckt.listen(1)

novoSckt, endereco = sckt.accept()
print('Conectado com: ' + str(endereco))

while True:
    msg = novoSckt.recv(1024)
    if not msg: break
    print('Mensagem recebida: ' + str(msg, encoding='utf-8'))
    novoSckt.send(msg)

novoSckt.close()

sckt.close()
