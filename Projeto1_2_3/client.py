#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################
__author__ = "Rafael Seicali Malcervelli"

from enlace import *
import time
import numpy as np
from pyfiglet import Figlet
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
from utils import *

serialName = "COM5"          

tam_head = 10 
tam_payload = 128 # Tamaho maximo
tam_eop = 4

def eop():
    return transform_byte(0) * tam_eop

def package(tam):
    qntd_pacotes_int = int(tam/tam_payload)
    resto = tam % tam_payload

    if resto == 0:
        return qntd_pacotes_int, tam_payload
    else:
        return qntd_pacotes_int+1, resto

def header(tipo, numero_pacotes, numero_pack_atual, tamanho_payload):
    """
    Legenda Header conforme a posição dos bytes:
    0 -> Tipo da mensagem (1 = handshake / 2 = handshake_server / 3 = mandar pacote / 4 = confirmação do pacote pelo server / 5 = encerrar)
    1 -> Número total de pacotes
    2 -> Número do pacote atual
    3 -> Tamanho Payload
    4 -> Checagem de erros, 0 para erro, 1 para confirmação
    5 -> Número do pacote do erro, 0 para sem erros
    6 -> 0
    7 -> 0
    8 -> 0 
    9 -> 0
    """

    zero = transform_byte(0)
    tip = transform_byte(tipo)
    npack_atual = transform_byte(numero_pack_atual)
    n_pacotes = transform_byte(numero_pacotes)
    t_pay = transform_byte(tamanho_payload)

    return tip + n_pacotes + npack_atual + t_pay + zero*6
    
def handshake(pacotes):
    zero = transform_byte(0)
    tip = transform_byte(1)
    numero_pacotes = transform_byte(pacotes)
    return tip + numero_pacotes + zero*8

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
        print(f1.renderText('Projeto 3 - client'))
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
        pacotes, pay = package(size_Txclient)
        print("/n Número de pacotes: {}".format(pacotes))
        print("Tamanho do payload final: {}".format(pay))

        end_of_package = eop()
        print("\n---------------------------")
        print("Enviando handshake para o server")
        print("---------------------------\n")

        #Send data to server
        com1.sendData(txClient)
        print("---------------------------")
        print("Enviando {0} para o server".format(imageR))
        print("---------------------------")

        rxClient, lenRxClient = com1.getData(4)
        size_server = int.from_bytes(rxClient, byteorder='big')
        print("Tamanho da imagem: {0}".format(size_server))

        if size_client == size_server:
            t_end = time.time()
            print("\n---------------------------")
            print("Transferência realizada com sucesso!")
            print("---------------------------\n")
            #print("Tempo gasto pelo client [s]: {0:.2f}".format(t_end-t_start))
            #print("Taxa de transmissão [bytes/s]: {0:.2f}".format(size_server/(t_end-t_start)))
            print("---------------------------\n")
            # Encerra comunicação
            print("\n-------------------------")
            print("Comunicação com a porta {0} encerrada".format(serialName))
            print("-------------------------\n")
            com1.disable()
        else:
            print("Ops, ocorreu um erro na transferência!")   
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
