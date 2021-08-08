# Programacao com sockets em python: script ativo

import sys
import socket
import threading
import select as s

HOST = ''
PORT = 5000
ENCODING = 'utf-8'

# Lista de comandos
EXIT_KEYWORD = '$exit'
LIST_THREADS = { '$list threads', '$lt' }
LIST_CLIENTS = { '$list clients', '$lc'}
HELP = '$help'

# Entradas para esculta do select
entry_points = [sys.stdin]
# Mapa de conexoes com o servidor
connections = {}
# Lock para acessar o dicionario de conexoes
lock = threading.Lock()

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
    
    while True:
        # Recebe mensagem com o nome do arquivo a ser bucado,
        # caso nao receba, termina a conexao atual
        file_name = newSckt.recv(1024)

        if not file_name:
                file_unavailable(newSckt, address) # Lida com o encerramento da conexao
                return None

        file_name = str(file_name, encoding=ENCODING)
        print(f'{address}: solicitacao de busca no arquivo "{file_name}".') # Log

        data = get_file(file_name)  # Busca pelo arquivo solicitado
        if data is not None:
            # Envia feedback para cliente
            msg = 'Arquivo encontrado com sucesso!'
            print('Enviando mensgem de sucesso...') 
            newSckt.send(msg.encode(ENCODING))

            # Recebe a palavra de busca. Caso nao receba, termina
            search_query = newSckt.recv(1024)
            if not file_name:
                file_unavailable(newSckt, address) # Lida com o encerramento da conexao
                return None

            search_query = str(search_query, encoding=ENCODING)
            print(f'{address}: solicitacao de busca por "{search_query}" em {file_name}.') # Log

            # Envia mensagem de conclusao para o cliente
            word_count = data.count(search_query)   # Realiza operacao de contagem no arquivo
            response = f'O arquivo "{file_name}" possui um total de {word_count} instancias da palavra "{search_query}".'
            newSckt.send(response.encode(ENCODING))

            print(f'Busca bem sucedida. Resposta enviada para {address}.') # Log
        else:
            # Falha ao buscar pelo arquivo
            err_msg = 'Falha: Arquivo nao encontrado.'
            newSckt.send(err_msg.encode(ENCODING))
            print(f'Arquivo nao encontrado. Mensagem de falha enviada para {address}.') # Log
    
    pass

def internalCommandHandler(cmd: str, sckt, clients: list):
    if cmd == EXIT_KEYWORD:
        for c in clients:
            c.join()
        sckt.close()
        sys.exit()
    elif cmd in LIST_THREADS:
        print('\nLista de threads ativas:')
        for thread in threading.enumerate():
            print(f' - {thread}')
        print()
    elif cmd in LIST_CLIENTS:
        if connections:
            print('\nLista de clientes ativos:')
            for k,v in connections.items():
                print(f' - {v}')
        else:
            print('\n Nao ha conexoes ativas no momento.')
        print()
    elif cmd == HELP:
        print('Lista de comandos:\n')
        print(f'"{EXIT_KEYWORD}"\t > Bloqueia novos pedidos de conexao e encerra o servidor quando nao houver cliente.')
        for item in LIST_CLIENTS:
            print(f'"{item}"\t > Exibe a lista de enderecos de clientes conectados.')
        for item in LIST_THREADS:
            print(f'"{item}"\t > Exibe a lista de threads ativas.')
        print(f'"{HELP}"\t > Exibe lista de comandos para entrada padrao do servidor.\n')


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

def file_unavailable(newSckt, address):
    """
    Modularizacao do codigo que lida com encerramento da conexao
    """
    print(f'{str(address)}> Encerrou a conexao')

    # Protecao contra eventuais alteracoes na estrutura por outras threads
    lock.acquire()
    del connections[newSckt]
    lock.release()

    # Encerra a conexao
    newSckt.close()
    pass

def main():
    try:
        sckt = initServer()
        print('Pronto para receber conexoes...')
        print(f'Para encerrar o servico, digite "{EXIT_KEYWORD}".')
        entry_points.append(sckt)

        # Lista de threads ativas
        client_threads = [] 

        while True:
            r, w, x = s.select(entry_points, [], [])

            for ready in r:
                if ready == sckt:
                    # Aceita a conexao
                    client_sckt, client_addr = acceptConnection(sckt) 

                    # Cria a nova thread que ira lidar com a conexao
                    client = threading.Thread(target=requestHandler, args=(client_sckt, client_addr))
                    client.start()
        
                    # Adiciona a nova thread na lista de threads ativas
                    client_threads.append(client)

                    # Protecao contra alteracoes problematicas por multithreading 
                    lock.acquire()
                    connections[client_sckt] = client_addr  # Adiciona a conexao nova ao mapa de conexoes
                    lock.release()
                elif ready == sys.stdin:
                    # Permite interacao com o servidor
                    cmd = input()
                    internalCommandHandler(cmd, sckt, client_threads)

    except socket.error as e:
        print('Erro: %s' % e)
        sys.exit()
    finally:
        sckt.close()
    pass

main()
