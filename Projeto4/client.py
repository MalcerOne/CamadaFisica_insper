#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################
__author__ = "Rafael Seicali Malcervelli"


#C:\Documentos Insper\4º_semestre\CamFis\projeto1\CamadaFisica_insper\Projeto1_2_3

from enlace import *
import time
import numpy as np
from pyfiglet import Figlet
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from utils import *
import keyboard
from identificators import id_client, id_server, id_arquivo

#Nome da porta serial a ser conectada
serialName = "COM5"          

#Setting de alguns valores padrões do header, payload e EOP
tam_head = 10 
tam_payload = 114 # Tamaho maximo
tam_eop = 4

#------------------------------------------------------------------
#Definição de algumas funções utilizadas no código
#------------------------------------------------------------------

def eop():
    return b'\xff' b'\xaa' b'\xff' b'\xaa'

def package(tam):
    qntd_pacotes_int = int(tam/tam_payload)
    resto = tam % tam_payload

    if resto == 0:
        return qntd_pacotes_int, tam_payload
    else:
        return qntd_pacotes_int+1, resto

def header(tipo, numero_pacotes, numero_pack_atual, tamanho_payload, idclient, idserver):
    """
    Legenda Header_ conforme a posição dos bytes:
    0 -> Tipo da mensagem {
        1 = handshake/ 
        2 = handshake_server/ 
        3 = mandar pacote/ 
        4 = confirmação do pacote pelo server/ 
        5 = time out/
        6 = erro}
    1 -> Id do sensor
    2 -> Id do server
    3 -> Número total de pacotes
    4 -> Número do pacote atual
    5 -> Se for handshake: Id do arquivo // Se for dados: Tamanho do payload
    6 -> Pacote solicitado para recomeço quando a erro no envio
    7 -> Último pacote recebido com sucesso
    8 -> 0 
    9 -> 0
    """

    zero = transform_byte(0)
    tip = transform_byte(tipo)
    npack_atual = transform_byte(numero_pack_atual)
    n_pacotes = transform_byte(numero_pacotes)
    t_pay = transform_byte(tamanho_payload)
    id_Server = transform_byte(idserver)
    id_Client = transform_byte(idclient)

    return tip + id_Client + id_Server + n_pacotes + npack_atual + t_pay + zero*4
    
def handshake(pacotes, idserver, idclient, idarquivo):
    zero = transform_byte(0)
    tip = transform_byte(1)
    numero_pacotes = transform_byte(pacotes)
    id_Server = transform_byte(idserver)
    id_Client = transform_byte(idclient)
    id_Arquivo = transform_byte(idarquivo)

    return tip + id_Client + id_Server + numero_pacotes + zero + id_Arquivo + zero*4

def check_for_error(eop, header):
    if len(eop) != tam_eop:
        print("Erro no tamanho do EOP...")
        return True
    elif len(header) != tam_head:
        print("Erro no tamanho do header...")
        return True
    else:
        return False
    
def main():
    try:
        f1 = Figlet(font='slant')
        print(f1.renderText('Projeto 4 - client'))
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        # Ativa comunicacao. Inicia os threads e a comunicação serial 
        com1.enable()
        print("\n-------------------")
        print("Porta {0} conectada!".format(serialName))
        print("-------------------\n")
        
        print("Escolha uma imagem: ")
        Tk().withdraw()
        imageR = askopenfilename(initialdir = os.getcwd() , filetypes=[("Image files", ".png .jpg .jpeg")])
        print("Imagem escolhida: {}".format(imageR))
        
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esta sempre irá armazenar os dados a serem enviados.
        txClient = open(imageR, 'rb').read()
        size_Txclient = len(txClient)
        print("\nTamanho do arquivo a ser enviado [bytes]: {}".format(size_Txclient))
        
        #Quebra do arquivo em pacotes
        pacotes, tam_pay_final = package(size_Txclient)
        print("\n\nNúmero de pacotes: {}".format(pacotes))
        print("Tamanho do payload final [bytes]: {}".format(tam_pay_final))

        end_of_package = eop()
        handshaked = False

        while not handshaked:
            handshake_client = handshake(pacotes)
            print("Enviando o handshake para iniciar a comunicação...")
            com1.sendData(handshake_client + end_of_package)
            #Checar o Header do Handshake
            check_server_up = com1.rx.getNData_handshake(tam_head)
            #Se o getNData_handshake retornar 'Cinco segundo se passaram', significa que não recebemos a confirmação do server em cinco segundos
            while check_server_up == "Cinco segundos se passaram":
                retry = input("Servidor inativo. Tentar novamente? [S/N]: ")
                if retry == "N" or retry == "n":
                    print("Encerrando a comunicação")
                    com1.disable()
                    exit()
                elif retry == "S" or retry == "s":
                    print("Ok, tentando novamente...")
                    handshake_client = handshake(pacotes)
                    com1.sendData(handshake_client + end_of_package)
                    check_server_up = com1.rx.getNData_handshake(tam_head)

            #Checar o Hedar e EOP do handshake
            check_eop = com1.rx.getNData(tam_eop)
            if check_for_error(check_eop, check_server_up):
                print("Erro no handshake entre client e server")
            else:
                #Checar se o código recebido pelo tipo de mensagem no header do handshake, é 2
                if transform_int(check_server_up[0:1]) == 2:
                    print("\n---------------------------")
                    print("Server up! Iniciando a transmissão...")
                    print("---------------------------\n")
                    handshaked = True

        #Preparação para o envio dos pacotes, após a confirmação do handshake
        allpackages_sent = False
        numero_pacote = 1
        last_pack = 0
        payload_index = 0
        head_Server = [0, 0, 0, 0, 0, 0, 0, 0]
        sem_erros = 0
        header_ = b''

        while not allpackages_sent:
            print("Enviando pacote número {0}".format(numero_pacote))
            
            if numero_pacote == pacotes:
                header_ = header(5, pacotes, numero_pacote, tam_pay_final)
                payload = txClient[payload_index:payload_index + tam_payload]
                com1.sendData(header_ + payload + eop())
                print("Último pacote enviado! Aguardando resposta do server...")

                head_Server = com1.rx.getNData(tam_head)
                payload_Server = com1.rx.getNData(0)
                eop_Server = com1.rx.getNData(tam_eop)

                if check_for_error(eop_Server, head_Server):
                    print("Debug: Head -> {0} // EOP -> {1}".format(head_Server, eop_Server))

                elif transform_int(head_Server[4:5]) == 1:
                    print("Dados enviados com sucesso! Todos os pacotes foram enviados!")
                    allpackages_sent = True

                elif transform_int(head_Server[4:5]) == 0:
                    #Se é igual a 0, significa que houve um erro
                    print("Erro no envio do pacote. Enviando mais uma vez")
                    pacote_novo_erro = transform_int(head_Server[5:6])
                    print("Número do pacote: {0}".format(pacote_novo_erro))
                    continue
            
            else:
                header_ = header(3, pacotes, numero_pacote, tam_payload)
                payload = txClient[payload_index:payload_index + tam_payload]
                com1.sendData(header_ + payload + eop())
                print("Pacote enviado! Aguardando resposta do server...")

                #Após a primeira iteração, o head_Server é identificado pelo getNData em sua variavel
                head_Server = com1.rx.getNData(tam_head)
                payload_Server = com1.rx.getNData(0)
                eop_Server = com1.rx.getNData(tam_eop)

                #Checa algum erro no tamanho do header e do eop da resposta do server
                if check_for_error(eop_Server, head_Server):
                    print("Debug: Head -> {0} // EOP -> {1}".format(head_Server, eop_Server))
                
                elif transform_int(head_Server[4:5]) == 1:
                    #Sem erros, pacote enviado
                    print("Resposta recebida, pacote enviado! Preparando para enviar o próximo...\n\n")
                    payload_index += tam_payload
                    numero_pacote += 1
                    continue

                #Checa se há algum erro com o envio do pacote
                elif transform_int(head_Server[4:5]) == 0:
                    #Se é igual a 0, significa que houve um erro
                    print("Erro no envio do pacote. Enviando mais uma vez")
                    pacote_novo_erro = transform_int(head_Server[5:6])
                    numero_pacote = pacote_novo_erro
                    print("Número do pacote: {0}".format(numero_pacote))

        print("\n---------------------------")
        print("Transferência realizada com sucesso!")
        print("---------------------------\n")
        # Encerra comunicação
        print("\n-------------------------")
        print("Comunicação com a porta {0} encerrada".format(serialName))
        print("-------------------------\n")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()