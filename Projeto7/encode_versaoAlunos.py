
#Importanto as bibliotecas necessárias
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import sys
from pyfiglet import Figlet

#Funções a serem utilizadas
def signal_handler(signal, frame):
        print('[!]---You pressed Ctrl+C!')
        sys.exit(0)

def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    f1 = Figlet(font='slant')
    print(f1.renderText('Projeto 7 - emissor'))
    print("\n[+]---Inicializando encoder\n\n")
    signal = signalMeu()

    print("[+]---Gerando Tons base\n\n")

    frequencias = [[697, 770, 852, 941], [1209, 1336, 1477, 1633]] 
    frequenciasTecla = [[], []]
    tecla = str(input("[?]---Escolha uma tecla do teclado numérico [0 a 9 | * e # | A, B, C, D]: "))
    print("[+]---Aguardando usuário...\n\n")
    print(f"[+]---Tecla escolhida: {tecla}")

    linha1 = ["1", "2", "3", "A"]
    linha2 = ["4", "5", "6", "B"]
    linha3 = ["7", "8", "9", "C"]
    linha4 = ["*", "0", "#", "D"]

    # Primeira linha
    if tecla in linha1:
        frequenciasTecla[0].append(frequencias[0][0])
        if tecla == "1":
            frequenciasTecla[1].append(frequencias[1][0])
        elif tecla == "2":
            frequenciasTecla[1].append(frequencias[1][1])
        elif tecla == "3":
            frequenciasTecla[1].append(frequencias[1][2])
        elif tecla == "A":
            frequenciasTecla[1].append(frequencias[1][3])

    # Segunda linha
    elif tecla in linha2:
        frequenciasTecla[0].append(frequencias[0][1])
        if tecla == "4":
            frequenciasTecla[1].append(frequencias[1][0])
        elif tecla == "5":
            frequenciasTecla[1].append(frequencias[1][1])
        elif tecla == "6":
            frequenciasTecla[1].append(frequencias[1][2])
        elif tecla == "B":
            frequenciasTecla[1].append(frequencias[1][3])

    # Terceira linha
    elif tecla in linha3:
        frequenciasTecla[0].append(frequencias[0][2])
        if tecla == "7":
            frequenciasTecla[1].append(frequencias[1][0])
        elif tecla == "8":
            frequenciasTecla[1].append(frequencias[1][1])
        elif tecla == "9":
            frequenciasTecla[1].append(frequencias[1][2])
        elif tecla == "C":
            frequenciasTecla[1].append(frequencias[1][3])

    # Quarta linha
    elif tecla in linha4:
        frequenciasTecla[0].append(frequencias[0][3])
        if tecla == "*":
            frequenciasTecla[1].append(frequencias[1][0])
        elif tecla == "0":
            frequenciasTecla[1].append(frequencias[1][1])
        elif tecla == "#":
            frequenciasTecla[1].append(frequencias[1][2])
        elif tecla == "D":
            frequenciasTecla[1].append(frequencias[1][3])

    print("[+]---Executando as senoides (emitindo o som)")
    fs = 44100
    tempo = np.linspace(-1, 1, 44100*1)
    sd.default.channels = 1

    #Primeira senoide
    x1, y1 = signal.generateSin(frequenciasTecla[0][0], 1, 1, fs)
    #Segunda senoide
    x2, y2 = signal.generateSin(frequenciasTecla[1][0], 1, 1, fs)

    #soma das senoides
    finalSin = y1 + y2
    print("[+]---Gerando Tom referente ao símbolo : {}".format(tecla))
    #Playing
    sd.play(finalSin, fs)

    # # Exibe gráficos
    plt.figure("Senoides")
    plt.plot(tempo, y1, "b-.", label=f"Frequência: {frequenciasTecla[0][0]} Hz", )
    plt.plot(tempo, y2, "r--", label=f"Frequência: {frequenciasTecla[1][0]} Hz")
    plt.plot(tempo, finalSin, "g-", label=f"Frequência Soma")
    plt.grid(True)
    plt.title(f"Senóides das frequências da tecla {tecla}")
    plt.xlabel("Tempo [s]")
    plt.ylabel("Amplitude do som")
    plt.xlim(0, 0.0135)
    plt.legend()
    plt.savefig("img/senoidesFrequencias.png", format="png")
    plt.show()

    # # aguarda fim do audio
    sd.wait()
if __name__ == "__main__":
    main()
