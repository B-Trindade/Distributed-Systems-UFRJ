# Programacao com sockets em python: script ativo

import socket

HOST = 'localhost'
PORT = 5000         # porta em que o server estara escutando
ENCODING = 'utf-8'  # constante de encode das mensagens

# Cria o objeto socket
try:
    sckt = socket.socket()
except socket.error as e:
    print('Erro durante criacao do socket %s' % e)  # Lanca erro em caso de falha durante a criacao do socket
    raise SystemExit #sys.exit(1) mas sem o import

# Estabelece conexao entre sockets
try:
    sckt.connect((HOST, PORT))
except socket.gaierror as e:
    print('Falha durante tentativa de conectar com: %s' % e)
    raise SystemExit    # Termina a execucao em caso de falha
except socket.error as e:
    print('Erro de conexao: %s' % e)
    raise SystemExit    # Termina a execucao em caso de falha

# Instrucoes para o usuario e indicacao de que procedimentos iniciais correram sem problemas
print('Conectado com o servidor (%s) pela porta %s.' % (HOST,PORT))

# bloco try-except para request/response
try:
    while True:
        print('Nova busca!')
        print('Para encerrar a conexao digite \'$exit\'.\n')

        # Recebe o nome do arquivo ou o codigo para encerrar a conexao com o server
        file_name = input('Insira o nome do arquivo para ser lido: ')
        if file_name == '$exit': 
            print('Encerrando conexao...')
            break
        
        # Recebe a palavra que sera buscada no arquivo file_name
        search_query = input('Insira a palavra de busca: ')
        if search_query == '$exit': 
            print('Encerrando conexao...')
            break

        sckt.send(file_name.encode(ENCODING))   # request pela disponibilidade do arquivo
        file_available = sckt.recv(1024)        # response do server sinalizando se o arquivo esta disponivel
        file_available = str(file_available, encoding=ENCODING) # converte para string, tornando a resposta interpretavel

        # Se o arquivo estiver disponivel envia a palavra a ser buscada
        if file_available == 'Arquivo encontrado com sucesso!': # Mensagem de sucesso esperada para prosseguir
            print('Server> ' + file_available )                 # Imprime a resposta do server

            print('Buscando por "' + search_query + '"...')           # Comunica ao usuario que a busca sera feita a seguir
            sckt.send(search_query.encode(ENCODING))            # Envia o novo request para o server informando a palavra a ser buscada

            word_count = sckt.recv(1024)                        # Recebe a resposta do server contendo a mensagem com o numero de vezes que a palavra foi contada
            word_count = str(word_count, encoding=ENCODING)     # Traduz a mensagem codificada

            print('Server> ' + word_count + '\n')                   # Exibe a resposta do servidor com a mensagem e a contagem
        elif file_available == 'Falha: Arquivo nao encontrado.':
            print('Server> ' + file_available + '\n')   # Exibe mensagem de erro esperado
        else:
            print('Erro nao esperado.')             # Informa que erro nao esperado ocorreu, prepara para uma nova busca
except socket.error as e:
    print('Erro durante request/receive com server: %s' % e)
    raise SystemExit
finally:
    sckt.close()
