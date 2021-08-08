# Programacao com sockets em python: script ativo

import sys
import socket
import threading
import select as s

HOST = ''
PORT = 5000
ENCODING = 'utf-8'
EXIT_KEYWORD = '$exit'

connections = {}
entry_points = [sys.stdin]

def initServer():
    """
    Inicia o socket: internet IPv4 + TCP
    """
    # Default: socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt = socket.socket()  # Descritor socket

    sckt.bind((HOST, PORT))
    sckt.listen(5)

    # Medida preventiva contra falhas entre a chamada de s.select() e sckt.accept()
    sckt.setblocking(False)
    return sckt

def acceptConnection(sckt):
    """
    Aceita a conexao com o cliente
    """
    newSckt, address = sckt.accept()
    print(f'Conectado com: {str(address)}') # Log de conexao com endereco <address>

    return newSckt, address
        
def requestHandler(newSckt, address):
    
    # Recebe mensagem com o nome do arquivo a ser bucado,
    # caso nao receba, termina a conexao atual
    file_name = newSckt.recv(1024)

    if not file_name:
            print(f'{str(address)}> Encerrou a conexao')
            del connections[newSckt]
            entry_points.remove(newSckt)
            newSckt.close()
            return None

    file_name = str(file_name, encoding=ENCODING)
    print(f'{address}: solicitacao de busca no arquivo "{file_name}".') # Log

    data = get_file(file_name)
    if data is not None:
        # Envia feedback para cliente
        msg = 'Arquivo encontrado com sucesso!'
        print('Enviando mensgem de sucesso...') 
        newSckt.send(msg.encode(ENCODING))

        # Recebe a palavra de busca. Caso nao receba, termina
        search_query = newSckt.recv(1024)
        if not file_name:
            print(f'{str(address)}> Encerrou a conexao')
            del connections[newSckt]
            entry_points.remove(newSckt)
            newSckt.close()
            return None

        search_query = str(search_query, encoding=ENCODING)
        print(f'{address}: solicitacao de busca por "{search_query}" em {file_name}.') # Log

        # Envia mensagem de conclusao para o cliente
        word_count = data.count(search_query)
        response = f'O arquivo "{file_name}" possui um total de {word_count} instancias da palavra "{search_query}".'
        newSckt.send(response.encode(ENCODING))

        print(f'Busca bem sucedida. Resposta enviada para {address}.')
    else:
        # Falha ao buscar pelo arquivo
        err_msg = 'Falha: Arquivo nao encontrado.'
        print('Enviando mensagem de falha...')
        newSckt.send(err_msg.encode(ENCODING))
            
    
    pass

def internalCommandHandler(cmd: str, sckt):
    if cmd == EXIT_KEYWORD:
        if not connections:
            sckt.close()
            sys.exit()
        else:
            print('Ha conexoes pendentes.')
    pass

def get_file(file_name: str):
    """
    Recebe o filename e tenta abri-lo como read only
    """
    try:
        with open(file_name, 'r') as file:
            data = file.read()
            return data
    except:
        return None

def main():
    try:
        sckt = initServer()
        print('Pronto para receber conexoes...')
        print(f'Para encerrar o servico, digite "{EXIT_KEYWORD}".')
        entry_points.append(sckt)

        while True:
            r, w, x = s.select(entry_points, [], [])

            for ready in r:
                if ready == sckt:
                    # Aceita a conexao
                    client_sckt, client_addr = acceptConnection(sckt) 

                    # Adiciona a conexao a lista de conexoes e mapeia (key:conexao, val:endereco)
                    entry_points.insert(0, client_sckt)
                    connections[client_sckt] = client_addr
                elif ready == sys.stdin:
                    # Permite interacao com o servidor
                    cmd = input()
                    internalCommandHandler(cmd, sckt)
                else:
                    requestHandler(ready, connections.get(ready))

    except socket.error as e:
        print('Erro: %s' % e)
        sys.exit()
    finally:
        sckt.close()
    pass

main()
