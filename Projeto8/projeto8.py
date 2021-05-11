#!/usr/bin/env python
# coding: utf-8

## Importando bibliotecas
from funcoes_LPF import *
from tkinter.filedialog import askopenfilename
import time, os
from scipy.io import wavfile
from pyfiglet import Figlet
import scipy.signal as sps
import sounddevice as sd
import matplotlib.pyplot as plt

def main():
    f1 = Figlet(font='slant')
    print(f1.renderText('Projeto 8 - Modulo AM'))
    print("\n[+]---Selecione um arquivo de áudio\n")

    ## Leitura do arquivo
    file = askopenfilename(initialdir=os.getcwd(), title='Selecione o arquivo .wav', filetypes=[('Sound Files', '.wav')])
    
    print(f"\n[+]---Arquivo '{os.path.basename(file)}' selecionado\n")
    samplerate, audio = wavfile.read(file)

    # Se o samplerate do audio não for 44100, cria um novo samplerate adequando o audio para tal.
    if samplerate != 44100:
        # https://stackoverflow.com/questions/30619740/downsampling-wav-audio-file
        number_of_samples = round(len(audio) * float(44100) / samplerate)
        audio = sps.resample(audio, number_of_samples)
        duration = number_of_samples/44100
        samplerate = int(number_of_samples/duration)
    else:
        duration = len(audio)/samplerate
        number_of_samples = samplerate*duration
    sd.default.channels = 1
    yAudio = audio[:,1]

    ## Normalizar o sinal
    audioNormalizado = normalizeAudio(yAudio)
    print(f"\n[+]---Faixa do áudio normalizado: '[{audioNormalizado.min(), audioNormalizado.max()}]'\n")

    ## Reproduzir o sinal normalizado
    print(f"\n[+]---Tocando o audio normalizado\n")
    sd.play(audioNormalizado, samplerate)
    sd.wait()
    
    ## Filtrar as altas frequências
    print(f"\n[+]---Filtrando altas frequências do audio\n")
    audioFiltered = low_pass_filter(samplerate, 4000, audioNormalizado)

    ## Reproduzir o sinal (opaco)
    print(f"\n[+]---Tocando o audio com altas frequências filtradas\n")
    sd.play(audioFiltered)
    sd.wait()

    ## Modular o sinal em AM com Carrier de 20 MHz
    print(f"\n[+]---Modulando o sinal por AM de 20 MHz\n")
    t = np.linspace(0, duration, number_of_samples)
    carrier = 1*np.cos(2*np.pi*20000*t)
    audioModAM = 1*carrier*audioFiltered

    ## Reproduzir o sinal (não é perfeitamente audível)
    print(f"\n[+]---Tocando o audio modulado (não é audível)\n")
    sd.play(audioModAM)
    sd.wait()

    wavfile.write("rafaModularizado.wav", 44100, audioModAM)


    #=============================GRÁFICOS=================================

    ## Gráfico Fourier x Tempo do áudio original
    plt.plot(t, yAudio, label="Áudio Original")
    plt.title("Áudio original x Tempo")
    plt.savefig("AudioOriginalxTempo.jpg")
    plt.show()

    xf1, yf1 = calcFFT(yAudio, 44100)
    plt.plot(xf1, np.abs(yf1), label="Áudio Original", color="blue")
    plt.title("Fourier do áudio original")
    plt.savefig("FourierAudioOriginal.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio normalizado
    plt.plot(t, audioNormalizado, label="Áudio Normalizado")
    plt.title("Áudio normalizado x Tempo")
    plt.savefig("AudioNormalizadoxTempo.jpg")
    plt.show()

    xf2, yf2 = calcFFT(audioNormalizado, 44100)
    plt.plot(xf2, np.abs(yf2), label="Áudio Normalizado", color="green")
    plt.title("Fourier do áudio normalizado")
    plt.savefig("FourierAudioNormalizado.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio filtrado
    plt.plot(t, audioFiltered, label="Áudio Filtrado")
    plt.title("Áudio filtrado x Tempo")
    plt.savefig("AudioFiltradoxTempo.jpg")
    plt.show()

    xf3, yf3 = calcFFT(audioFiltered, 44100)
    plt.plot(xf3, np.abs(yf3), label="Áudio Filtrado", color="red")
    plt.title("Fourier do áudio filtrado")
    plt.savefig("FourierAudioFiltrado.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio modulado
    plt.plot(t, audioModAM, label="Áudio Modulado")
    plt.title("Áudio modulado x Tempo")
    plt.savefig("AudioModuladoxTempo.jpg")
    plt.show()

    xf4, yf4 = calcFFT(audioModAM, 44100)
    plt.plot(xf4, np.abs(yf4), label="Áudio Modulado", color="brown")
    plt.title("Fourier do áudio modulado")
    plt.savefig("FourierAudioModulado.jpg")
    plt.show()

    ##=========================================== Demodulação================================
    print("\n[+]---Selecione um arquivo de áudio\n")
    file = askopenfilename(initialdir=os.getcwd(), title='Selecione o arquivo .wav', filetypes=[('Sound Files', '.wav')])
    
    print(f"\n[+]---Arquivo '{os.path.basename(file)}' selecionado\n")
    samplerateDemod, audioMODfriend = wavfile.read(file)

    ## Verificando se esta na banda de 16kHz e 24kHz
    xf5, yf5 = calcFFT(audioMODfriend, 44100)
    plt.plot(xf5, np.abs(yf5), label="Áudio do amigo", color="black")
    plt.title("Fourier do áudio do amigo")
    plt.savefig("FourierAudiodoAmigo.jpg")
    plt.show()

    ## Demodulando
    print(f"\n[+]---Demodulando o áudio\n")
    audioDemod = carrier*audioMODfriend

    ## Filtrando freqûencias superiores a 4kHz
    print(f"\n[+]---Filtrando frequências superiores a 4kHz\n")
    audioDemodFiltered = low_pass_filter(44100, 4000, audioDemod)

    ## Executando o áudio e vendo que é audível
    print(f"\n[+]---Tocando áudio demodularizado e filtrado\n")
    sd.play(audioDemodFiltered)
    sd.wait()

    ## Gráficos no tempo e Fourier do audio filtrado
    #Gráfico do tempo
    plt.plot(t, audioDemodFiltered, label="Áudio Demodulado e filtrado")
    plt.title("Áudio demodulado e filtrado x Tempo")
    plt.savefig("AudioDemoduladoxTempo.jpg")
    plt.show()

    #Gráfico Fourier
    xf6, yf6 = calcFFT(audioDemodFiltered, 44100)
    plt.plot(xf6, np.abs(yf6), label="Áudio do amigo demodulado e filtrado", color="black")
    plt.title("Fourier do áudio do amigo demodulado e filtrado")
    plt.savefig("FourierAudiodoAmigoDemoduladoeFiltrado.jpg")
    plt.show()
    
if __name__ == "__main__":
    main()
