#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################
__author__ = "Rafael Seicali Malcervelli"


#C:\Documentos Insper\4º_semestre\CamFis\projeto1\CamadaFisica_insper\Projeto4

from enlace import *
import time
import numpy as np
from pyfiglet import Figlet
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from utils import *
from datetime import datetime


#Nome da porta serial a ser conectada
serialName = "COM5"          

#Setting de alguns valores padrões do header, payload e EOP
tam_head = 10 
tam_payload = 114 # Tamaho maximo
tam_eop = 4

#Definição dos ids
id_client = 93
id_server = 22
id_arquivo = 55

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
    7 -> Último pacote recebido com sucesso {
        1 = Client avisa que é o ultimo -> Contém payload_final
        2 = Resposta do server recebendo o ultimo
    }
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

def header_lastpayload(tipo, numero_pacotes, numero_pack_atual, tamanho_payload_final, idclient, idserver, confirmacao):
    zero = transform_byte(0)
    tip = transform_byte(tipo)
    npack_atual = transform_byte(numero_pack_atual)
    n_pacotes = transform_byte(numero_pacotes)
    t_pay = transform_byte(tamanho_payload_final)
    id_Server = transform_byte(idserver)
    id_Client = transform_byte(idclient)
    confirmation = transform_byte(confirmacao)

    return tip + id_Client + id_Server + n_pacotes + npack_atual + t_pay + zero + confirmation + zero*2
    
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
        inicia = False

        while not inicia:
            handshake_client = handshake(pacotes, id_server, id_client, id_arquivo)
            print("Enviando o handshake para iniciar a comunicação...")
            com1.sendData(handshake_client + end_of_package)
            
            #Checar o Header do Handshake
            check_server_up = com1.rx.getNData_handshake(tam_head)
            #Se o getNData_handshake retornar 'Cinco segundo se passaram', significa que não recebemos a confirmação do server em cinco segundos
            while check_server_up == "Cinco segundos se passaram":
                retry = input("Servidor inativo. Tentar novamente? [S/N]: ")
                if retry == "N" or retry == "n":
                    print("Encerrando a comunicação")
                    header_ = header(5, pacotes, 1, tam_payload, id_client, id_server)
                    com1.sendData(header_ + eop())
                    com1.disable()
                    exit()
                elif retry == "S" or retry == "s":
                    print("Ok, tentando novamente...")
                    handshake_client = handshake(pacotes, id_server, id_client, id_arquivo)
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
                    inicia = True

        #Preparação para o envio dos pacotes, após a confirmação do handshake
        cont = 1
        payload_index = 0
        head_Server = [0, 0, 0, 0, 0, 0, 0, 0]
        header_ = b''
        timer12_check = 1
        count = 1
        a = 0

        while cont <= pacotes:
            
            if cont == pacotes and count == 1:
                timer12_check = 4
                print("Enviando último pacote!")

                header_ = header_lastpayload(3, pacotes, cont, tam_pay_final, id_client, id_server, 1)
                payload = txClient[payload_index:payload_index + tam_pay_final]
                com1.sendData(header_ + payload + eop())
                print("Pacote {0} enviado! Aguardando resposta do server...".format(cont))

                timer1_set = time.time()
                timer2_set = time.time()

            if timer12_check == 1:
                print("Enviando pacote número {0}".format(cont))
                header_ = header(3, pacotes, cont, tam_payload, id_client, id_server)
                payload = txClient[payload_index:payload_index + tam_payload]
                com1.sendData(header_ + payload + eop())
                print("Pacote {0} enviado! Aguardando resposta do server...".format(cont))

                timer1_set = time.time()
                timer2_set = time.time()

            elif timer12_check == 3:
                payload_index = 0
                print("\n-------------------------")
                print("Erro na ordem do arquivo ou tamanho do payload. Enviando novamente...")
                print("-------------------------\n")
                header_ = header(3, pacotes, cont, tam_payload, id_client, id_server)
                payload = txClient[payload_index:payload_index + tam_payload]
                com1.sendData(header_ + payload + eop())                

                print("Pacote {0} enviado! Aguardando resposta do server...".format(cont))
                

                timer1_set = time.time()
                timer2_set = time.time()

            head_Server = com1.rx.getNData(tam_head)
            payload_Server = com1.rx.getNData(0)
            eop_Server = com1.rx.getNData(tam_eop) 
            
            if transform_int(head_Server[0:1]) == 4:
                print("Resposta recebida! Aguarde, preparando para enviar próximo pacote...")
                cont += 1
                timer12_check = 1
                payload_index += tam_payload
                continue
            
            if time.time() - timer1_set > 5:
                if timer12_check == 4:
                    print("Passaram 5 segundos, enviando novamente..")
                    header_ = header_lastpayload(7, pacotes, cont, tam_pay_final, id_client, id_server, 1)
                    payload = txClient[payload_index:payload_index + tam_payload]
                    com1.sendData(header_ + payload + eop())

                    print("Pacote {0} enviado! Aguardando resposta do server...".format(cont))
                    timer1_set = time.time()
                else:
                    timer12_check = 2
                    print("Passaram 5 segundos, enviando novamente..")
                    header_ = header(3, pacotes, cont, tam_payload, id_client, id_server)
                    payload = txClient[payload_index:payload_index + tam_payload]
                    com1.sendData(header_ + payload + eop())
                    print("Pacote {0} enviado! Aguardando resposta do server...".format(cont))
                    timer1_set = time.time()
            
            #TimeOut
            if time.time() - timer2_set > 20:
                header_ = header(5, pacotes, cont, tam_payload, id_client, id_server)
                payload = txClient[payload_index:payload_index + tam_payload]
                com1.sendData(header_ + payload + eop())
                print("Erro de TimeOut!")
                print("\n-------------------------")
                print("Comunicação com a porta {0} encerrada".format(serialName))
                print("-------------------------\n")
                com1.disable()
                exit()
            
            #Pacote errado ou tamanho do payload
            if transform_int(head_Server[0:1]) == 6:
                timer12_check = 3
                cont = transform_int(head_Server[6:7])
                continue
            
            count = 2

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