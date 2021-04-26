
#importe as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import sys

#funções a serem utilizadas
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder\n\n")
    signal = signalMeu()

    print("Gerando Tons base\n\n")

    frequencias = [[697, 770, 852, 941], [1209, 1336, 1477, 1633]] 
    frequenciasTecla = [[], []]
    tecla = str(input("Escolha uma tecla do teclado numérico [0 a 9 | * e # | A, B, C, D]: "))
    print("Aguardando usuário...\n\n")
    print(tecla)

    linha1 = ["1", "2", "3", "A"]
    linha2 = ["4", "5", "6", "B"]
    linha3 = ["7", "8", "9", "C"]
    linha4 = ["*", "0", "#", "D"]
    # Primeira linha
    if tecla in linha1:
        print("Entrou")
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

    print("Executando as senoides (emitindo o som)")
    print(f"Lista frequencias: {frequenciasTecla}")
    arrayFrequencia = np.arange(frequencias[0][0], frequenciasTecla[1][0], ((frequenciasTecla[1][0] - frequencias[0][0] )/44100))
    print(f"Array frequencias: {arrayFrequencia}")
    print(f"Array lenght: {len(arrayFrequencia)}")
    sd.play(arrayFrequencia, 44100)

    # print("Gerando Tom referente ao símbolo : {}".format(tecla))
    # sd.play(tone, fs)
    # # Exibe gráficos
    # plt.show()
    # # aguarda fim do audio
    # sd.wait()
    # plotFFT(self, signal, fs)
    
    #********************************************instruções*********************************************** 
    # seu objetivo aqui é gerar duas senoides. Cada uma com frequencia corresposndente à tecla pressionada
    # então inicialmente peça ao usuário para digitar uma tecla do teclado numérico DTMF
    
    # agora, voce tem que gerar duas senoides com as frequencias corresposndentes à tecla pressionada, segundo a tabela DTMF
    # se voce quiser, pode usar a funcao de construção de senoides existente na biblioteca de apoio cedida. Para isso, você terá que entender como ela funciona e o que são os argumentos.

    # essas senoides tem que ter taxa de amostragem de 44100 amostras por segundo, entao voce tera que gerar uma lista de tempo correspondente a isso e entao gerar as senoides
    # lembre-se que a senoide pode ser construída com A*sin(2*pi*f*t)
    # o tamanho da lista tempo estará associada à duração do som. A intensidade é controlada pela constante A (amplitude da senoide). Seja razoável.
    # some as senoides. A soma será o sinal a ser emitido.
    # utilize a funcao da biblioteca sounddevice para reproduzir o som. Entenda seus argumento.
    # grave o som com seu celular ou qualquer outro microfone. Cuidado, algumas placas de som não gravam sons gerados por elas mesmas. (Isso evita microfonia).
    
    # construa o gráfico do sinal emitido e o gráfico da transformada de Fourier. Cuidado. Como as frequencias sao relativamente altas, voce deve plotar apenas alguns pontos (alguns periodos) para conseguirmos ver o sinal
if __name__ == "__main__":
    main()
