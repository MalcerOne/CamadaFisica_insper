__author__ = "Rafael Seicali Malcervelli"

from enlace import *
import time
import numpy as np
from pyfiglet import Figlet
from utils import *

imageW = "imgs/recebidaCopia.png"
serialName = "COM3"

tam_head = 10 
tam_payload = 128 # Tamaho maximo
tam_eop = 4

def main():
    try:
        f = Figlet(font='slant')
        print(f.renderText('Projeto 3 - server'))

        com2 = enlace(serialName)
        com2.enable()
        com2.fisica.flush()
        print("\n-------------------")
        print("Porta {0} conectada!".format(serialName))
        print("-------------------\n")
        print("Aguardando transmissão...")

        #Recebendo o head
        img_size_b, lenRx = com2.getData(4)
        img_size_int = int.from_bytes(img_size_b, byteorder="big")
        print("---------------------------")
        print("Tamanho da imagem: {0}".format(img_size_int))
        print("---------------------------")

        #Enviando a imagem
        rxServer, lenRxServer = com2.getData(img_size_int)
        size_server = lenRxServer.to_bytes(4, byteorder="big")
        com2.sendData(size_server)

        #Salvando a imagem
        imagem = open(imageW, "wb")
        imagem.write(rxServer)
        imagem.close()
        print("\n-------------------------")
        print("Comunicação com a porta {0} encerrada".format(serialName))
        print("-------------------------\n")
        com2.disable()

    except:
        print("ops! :-\\")

if __name__ == "__main__":
    main()