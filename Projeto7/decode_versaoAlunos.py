
#Importe todas as bibliotecas
from suaBibSignal import *
import pickle    #alternativas  #from detect_peaks import *   #import pickle
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time
import sys
from pyfiglet import Figlet

#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    f1 = Figlet(font='slant')
    print(f1.renderText('Projeto 7 - receptor'))
    #*****************************instruções********************************
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida)   
    # algo como:
    print("\n[+]---Inicializando decoder\n\n")
    signal = signalMeu() 
       
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    sd.default.samplerate = 44100 #Hz, profundidade de 16 bits
    sd.default.channels = 1 # o numero de canais, tipicamente são 2. Placas com dois canais. Se ocorrer problemas pode tentar com 1. No caso de 2 canais, ao gravar um audio, terá duas listas
    duration =  2 # #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic
    
    #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes) durante a gracação. Para esse cálculo você deverá utilizar a taxa de amostragem e o tempo de gravação
    numAmostras = sd.default.samplerate * duration
    #faca um print na tela dizendo que a captacao comecará em n segundos. e entao 
    #use um time.sleep para a espera
    print("\n[+]---A captação do som começará em 5 segundos...")
    time.sleep(5)
   
    #Ao seguir, faca um print informando que a gravacao foi inicializada
    print("\n[+]---Gravação inicializada!")
    #para gravar, utilize
    audio = sd.rec(int(numAmostras), sd.default.samplerate, channels=1)
    sd.wait()
    print("\n[+]---FIM")

    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista, isso dependerá so seu sistema, drivers etc...
    #extraia a parte que interessa da gravação (as amostras) gravando em uma variável "dados". Isso porque a variável audio pode conter dois canais e outas informações). 
    dadoslista = []
    for amostras in audio:
        dadoslista.append(amostras[0])

    dadosArray = np.array(dadoslista)
    # # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    tempo = np.linspace(-1 ,1,1*44100*2)
    # # plot do gravico áudio gravado (dados) vs tempo! Não plote todos os pontos, pois verá apenas uma mancha (freq altas) . 
    plt.plot(tempo, dadosArray, "r-", label=f"Áudio captado")
    plt.grid(True)
    plt.title(f"Áudio gravado x Tempo")
    plt.xlabel("Tempo [s]")
    plt.ylabel("Amplitude do som")
    plt.xlim(0, 0.001)
    plt.ylim(-0.05, 0.05)
    plt.legend()
    plt.show()  
    # ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    # xf, yf = signal.calcFFT(y, fs)
    # plt.figure("F(y)")
    # plt.plot(xf,yf)
    # plt.grid()
    # plt.title('Fourier audio')
    
    # #agora, voce tem os picos da transformada, que te informam quais sao as frequencias mais presentes no sinal. Alguns dos picos devem ser correspondentes às frequencias do DTMF!
    # #Para descobrir a tecla pressionada, voce deve extrair os picos e compara-los à tabela DTMF
    # #Provavelmente, se tudo deu certo, 2 picos serao PRÓXIMOS aos valores da tabela. Os demais serão picos de ruídos.

    # # para extrair os picos, voce deve utilizar a funcao peakutils.indexes(,,)
    # # Essa funcao possui como argumentos dois parâmetros importantes: "thres" e "min_dist".
    # # "thres" determina a sensibilidade da funcao, ou seja, quao elevado tem que ser o valor do pico para de fato ser considerado um pico
    # #"min_dist" é relatico tolerancia. Ele determina quao próximos 2 picos identificados podem estar, ou seja, se a funcao indentificar um pico na posicao 200, por exemplo, só identificara outro a partir do 200+min_dis. Isso evita que varios picos sejam identificados em torno do 200, uma vez que todos sejam provavelmente resultado de pequenas variações de uma unica frequencia a ser identificada.   
    # # Comece com os valores:
    # index = peakutils.indexes(yf, thres=0.4, min_dist=50)
    # print("index de picos {}" .format(index)) #yf é o resultado da transformada de fourier

    # #printe os picos encontrados! 
    # # Aqui você deverá tomar o seguinte cuidado: A funcao  peakutils.indexes retorna as POSICOES dos picos. Não os valores das frequências onde ocorrem! Pense a respeito
    
    # #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    # #print o valor tecla!!!
    # #Se acertou, parabens! Voce construiu um sistema DTMF

    # #Você pode tentar também identificar a tecla de um telefone real! Basta gravar o som emitido pelo seu celular ao pressionar uma tecla. 

      
    # ## Exiba gráficos do fourier do som gravados 
    # plt.show()

if __name__ == "__main__":
    main()
