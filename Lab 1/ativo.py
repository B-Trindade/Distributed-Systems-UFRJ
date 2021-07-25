# Programacao com sockets em python: script ativo

import socket

HOST = 'localhost'
PORT = 8000

sckt = socket.socket()

sckt.connect((HOST, PORT))

sckt.send(b'Ola sou o lado ativo!')

msg = sckt.recv(1024)
print(str(msg, encoding='utf-8'))

sckt.close()
