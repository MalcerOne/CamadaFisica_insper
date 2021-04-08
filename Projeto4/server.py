__author__ = "Rafael Seicali Malcervelli"

from enlace import *
import time
import numpy as np
from pyfiglet import Figlet
from utils import *
from datetime import datetime

#Definindo o local para salvar a foto
imageW = "imgs/recebidaCopia.png"

#Nome da porta serial a ser conectada
serialName = "COM3"

#Setting de alguns valores padrões do header, payload e EOP
tam_head = 10 
tam_payload = 114 # Tamanho maximo
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

def header_erro(tipo, numero_pacotes, numero_pack_atual, tamanho_payload, idclient, idserver, pacoteErro):
    zero = transform_byte(0)
    tip = transform_byte(tipo)
    npack_atual = transform_byte(numero_pack_atual)
    n_pacotes = transform_byte(numero_pacotes)
    t_pay = transform_byte(tamanho_payload)
    pacoteErro = transform_byte(pacoteErro)
    id_Server = transform_byte(idserver)
    id_Client = transform_byte(idclient)

    return tip + id_Client + id_Server + n_pacotes + npack_atual + t_pay + pacoteErro + zero*3


def handshake_confirm():
    return transform_byte(2) + transform_byte(0)*9

def check_error(eop, header):
    if len(eop) != tam_eop:
        print("Erro no tamanho do EOP...")
        return True

    if len(header) != tam_head:
        print("Erro no tamanho do header...")
        return True

    else:
        return False

def main():
    try:
        f = Figlet(font='slant')
        print(f.renderText('Projeto 4 - server'))

        com2 = enlace(serialName)
        com2.enable()

        print("\n-------------------")
        print("Porta {0} conectada!".format(serialName))
        print("-------------------\n")
        print("Aguardando transmissão...")

        receive_all_data = b''
        ocioso = True
        
        #Aguardando mensagem - handshake
        while ocioso:
            header_handshake = com2.rx.getNData(tam_head)
            eophandshake = com2.rx.getNData(tam_eop)
          
            if transform_int(header_handshake[0:1]) == 1:
                if transform_int(header_handshake[2:3]) == id_server:
                    ocioso = False
                    time.sleep(1)
                    continue
                time.sleep(1)
                continue
            time.sleep(1)
        
        pacotes = transform_int(header_handshake[3:4])
        print("\nHandshake recebido!\nNúmero total de pacotes a serem recebidos: {0}\nEnviando resposta para o client...\n\n".format(pacotes))
        
        handshake_answer = handshake_confirm()
        end_of_package_handshake = eop()

        com2.sendData(handshake_answer + end_of_package_handshake)

        cont = 1
        condition1 = 0

        while cont <= pacotes:

            if cont == pacotes:
                if condition1 == 0:
                    time1_set = time.time()
                    timer2_set = time.time()
                elif condition1 == 1:
                    timer1_set = time.time()

                print("Aguardando último pacote, número: {0}...".format(cont))
  
                header_pacote_final = com2.rx.getNData(tam_head)
                payload_arquivo_final = com2.rx.getNData(transform_int(header_pacote_final[5:6]))
                eop_arquivo = com2.rx.getNData(tam_eop)

                pacoteAtual = transform_int(header_pacote_final[4:5])
                if transform_int(header_pacote_final[0:1]) == 3:

                    if transform_int(header_pacote_final[7:8]) == 1 and pacoteAtual == cont and len(payload_arquivo_final) == transform_int(header_pacote_final[5:6]):
                    
                        print("Último pacote recebido! Enviando confirmação e salvando os dados\n")
                        receive_all_data += payload_arquivo_final
                        payload_size = len(receive_all_data)
                        com2.sendData(header(4, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                        cont += 1
                        continue
                    print("Erro no número do pacote ou tamanho do payload. Solicitando reenvio.")
                    com2.sendData(header_erro(6, pacotes, cont, tam_payload, id_client, id_server, cont) + eop())
                    condition1 = 0
                    continue

                time.sleep(1) 

                if time.time() - timer2_set > 20:
                    ocioso = True
                    com2.sendData(header(5, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                    print("Erro de TimeOut!")
                    print("\n-------------------------")
                    print("Comunicação com a porta {0} encerrada".format(serialName))
                    print("-------------------------\n")
                    com2.disable()
                
                if time.time() - timer1_set > 2:
                    com2.sendData(header(4, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                    condition1 = 1
                
                    
            if condition1 == 0:
                timer1_set = time.time()
                timer2_set = time.time()

            elif condition1 == 1:
                timer1_set = time.time()
        
            print("Aguardando o pacote número: {0}...".format(cont))

            header_pacote = com2.rx.getNData(tam_head)
            payload_arquivo = com2.rx.getNData(tam_payload)
            eop_arquivo = com2.rx.getNData(tam_eop)
            pacoteAtual = transform_int(header_pacote[4:5])

            if transform_int(header_pacote[0:1]) == 3:
                if pacoteAtual == cont and len(payload_arquivo) == tam_payload:
                    receive_all_data += payload_arquivo
                    payload_size = len(receive_all_data)
                    print("Pacote número {0} recebido, enviando confirmação...\n\n".format(pacoteAtual))
                    com2.sendData(header(4, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                    cont += 1
                else:
                    print("Erro no número do pacote ou tamanho do payload. Solicitando reenvio.")
                    com2.sendData(header_erro(6, pacotes, cont, tam_payload, id_client, id_server, cont) + eop())
                    condition1 = 0
                    continue

            time.sleep(1) 

            if time.time() - timer2_set > 20:
                ocioso = True
                com2.sendData(header(5, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                print("Erro de TimeOut!")
                print("\n-------------------------")
                print("Comunicação com a porta {0} encerrada".format(serialName))
                print("-------------------------\n")
                com2.disable()
                exit()
            
            if time.time() - timer1_set > 2:
                condition1 = 1
                print("Enviando novamente..")
                com2.sendData(header(4, pacotes, pacoteAtual, tam_payload, id_client, id_server) + eop())
                

        print("\n---------------------------")
        print("Transmissão realizada com sucesso, salvando os dados no arquivo: {0}".format(imageW))
        print("---------------------------\n")        

        #Salvando a imagem
        imagem = open(imageW, "wb")
        imagem.write(receive_all_data)
        imagem.close()

        print("Dados salvos com sucesso.")
        print("\n-------------------------")
        print("Comunicação com a porta {0} encerrada".format(serialName))
        print("-------------------------\n")
        com2.disable()

    except Exception as e:
        print(e)
        print("ops! :-\\")
        com2.disable()

if __name__ == "__main__":
    main()