
#Importe todas as bibliotecas
from suaBibSignal import signalMeu
import peakutils    #alternativas  #from detect_peaks import *   #import pickle
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

def getFrequencies(frequencia):
    frequencias = [[697, 770, 852, 941], [1209, 1336, 1477, 1633]]
    peakFreqC = 0
    peakFreqL = 0
    #linha
    for linha in frequencias[0]:
        if int(frequencia) in range(linha - 40, linha + 40):
            peakFreqL = linha
            return peakFreqL
    
    for coluna in frequencias[1]:
        if int(frequencia) in range(linha - 40, linha + 40):
            peakFreqC = coluna
            return peakFreqC

    
def main():
    f1 = Figlet(font='slant')
    print(f1.renderText('Projeto 7 - receptor'))
  
    print("\n[+]---Inicializando decoder\n\n")
    signal = signalMeu() 

    duration =  1 #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic
    sd.default.channels = 1
    sd.default.samplerate = 44100
    numAmostras = 44100 * duration
    
    print("\n[+]---A captação do som começará em 5 segundos...")
    time.sleep(5)
   

    print("\n[+]---Gravação inicializada!")

    audio = sd.rec(int(numAmostras))
    sd.wait()
    print("\n[+]---Fim da gravação.")

    tempo = np.linspace(0,2,44100)

    # # plot do gravico áudio gravado (dados) vs tempo!  
    print("\n[+]---Plotando gráfico do áudio gravado.")
    plt.figure("Senoide")
    plt.plot(tempo[:400], audio[:400], "r-", label=f"Áudio captado")
    plt.grid(True)
    plt.title(f"Áudio gravado x Tempo")
    plt.autoscale(enable=True, axis="both", tight=True)
    plt.show()
    

    # ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    print("\n[+]---Realizando a transformada de Fourier.")
    xf, yf = signal.calcFFT(audio, 44100)
    print("\n[+]---Plotando gráfico da transformada de Fourier.")
    plt.figure("Fourier")
    plt.plot(xf,yf)
    plt.grid(True)
    plt.title('Transformada de Fourier - Áudio gravado')
    plt.autoscale(enable=True, axis="both", tight=True)
    plt.show()
    
    ## Adquirindo a tecla a partir do som obtido e da transformada de fourier
    print("\n[+]---Identificando picos.")
    index = peakutils.indexes(yf, thres=0.2, min_dist=10)
    frqObtidaLista = [[], []]
    for frequencia in xf[index]:
        #Linha
        if int(frequencia) in range(640, 990):
            frqObtidaLista[0].append(getFrequencies(frequencia))
        #Coluna
        elif int(frequencia) in range(1160, 1680):
            frqObtidaLista[1].append(getFrequencies(frequencia))

    tabelaDTMF = {"1":[697, 1209], "2":[697, 1336], "3":[697, 1477], "A":[697, 1633], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "B":[770, 1633], "7":[852, 1209], "8":[852, 1336], "9":[852, 1477], "C":[852, 1633], "X":[941, 1209], "0":[941, 1336], "#":[941, 1477], "D":[941, 1633]}

    character = "None"
    for tecla, frequencias in tabelaDTMF.items():
        if frqObtidaLista[0] == frequencias[0] and frqObtidaLista[1] == frequencias[1]:
            character = tecla
    
    print(f"\n[+]---Tecla referente ao som gravado: {character}")

if __name__ == "__main__":
    main()
