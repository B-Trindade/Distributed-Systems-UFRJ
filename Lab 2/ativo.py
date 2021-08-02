# Programacao com sockets em python: script ativo

import socket

HOST = 'localhost'
PORT = 8000

# Cria o objeto socket
try:
    sckt = socket.socket()
except socket.error as e:
    print('Erro durante criacao do socket %s' % e)
    raise SystemExit #sys.exit(1) mas sem o import

# Estabelece conexao entre sockets
try:
    sckt.connect((HOST, PORT))
except socket.gaierror as e:
    print('Falha durante tentativa de conectar com: %s' % e)
    raise SystemExit
except socket.error as e:
    print('Erro de conexao: %s' % e)
    raise SystemExit

print('Conectado com servidor de echo (%s) pela porta %s.' % (HOST,PORT))
print('Para encerrar a conexao digite \'exit\'.\n')

# bloco try-except para envio e recebimento da mensagem de echo
try:
    while True:
        msg = input('Insira sua mensagem: ')
        if msg == 'exit': 
            print('Encerrando conexao...')
            break
        sckt.send(msg.encode('utf-8'))

        echo = sckt.recv(1024)
        print('Echo> ' + str(echo, encoding='utf-8'))
        print()
except socket.error as e:
    print('Erro durante envio/recebimento de mensagem: %s' % e)
    raise SystemExit
finally:
    sckt.close()
