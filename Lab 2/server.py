# Programacao com sockets em python: script ativo

import socket

HOST = ''
PORT = 5000
ENCODING = 'utf-8'

#Recebe o filename e tenta abri-lo como read only
def get_file(file_name: str):
    try:
        with open(file_name, 'r') as file:
            data = file.read()
            return data
    except:
        return None

# Descritor socket
sckt = socket.socket() # default: socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincular endereco e porta
sckt.bind((HOST, PORT))

# Escuta apenas um client por vez
sckt.listen(1)


while True:
    novoSckt, endereco = sckt.accept()
    print('Conectado com: ' + str(endereco))

    while True:
        file_name = novoSckt.recv(1024)
        if not file_name: break
        file_name = str(file_name, encoding=ENCODING)

        data = get_file(file_name)
        if data is not None:
            msg = 'Arquivo encontrado com sucesso!'
            print('Enviando mensgem de sucesso...')
            novoSckt.send(msg.encode(ENCODING))

            search_query = novoSckt.recv(1024)
            if not file_name: break
            search_query = str(search_query, encoding=ENCODING)

            word_count = data.count(search_query)
            response = f'O arquivo "{file_name}" possui um total de {word_count} instancias da palavra "{search_query}".'
            novoSckt.send(response.encode(ENCODING))

            print('Resposta para client enviada.')
        else:
            err_msg = 'Falha: Arquivo nao encontrado.'
            print('Enviando mensagem de falha...')
            novoSckt.send(err_msg.encode(ENCODING))
            
    novoSckt.close()
sckt.close()
