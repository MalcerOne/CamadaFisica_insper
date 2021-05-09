## Importando bibliotecas
from funcoes_LPF import *
from tkinter.filedialog import askopenfilename
import time, os
from scipy.io import wavfile
from pyfiglet import Figlet
import scipy.signal as sps
import sounddevice as sd

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

    ## Normalizar o sinal
    audioNormalizado = normalizeAudio(audio)
    print(f"\n[+]---Faixa do áudio normalizado: '[{audioNormalizado.min(), audioNormalizado.max()}]'\n")

    ## Reproduzir o sinal normalizado
    print(f"\n[+]---Tocando o audio normalizado\n")
    sd.play(audioNormalizado, samplerate)
    sd.wait()
    
    ## Filtrar as altas frequências
    print(f"\n[+]---Filtrando altas frequências do audio\n")
    audioFiltered = LPF(audioNormalizado, 4000, samplerate)

    ## Reproduzir o sinal (opaco)
    print(f"\n[+]---Tocando o audio com altas frequências filtradas\n")
    sd.play(audioFiltered, samplerate)
    sd.wait()
    ## Modular o sinal em AM com Carrierde 20 MHz
    ## Reproduzir o sinal (não é perfeitamente audível)
    ## Gráfico Fourier x Tempo do áudio original
    ## Gráfico Fourier x Tempo do áudio normalizado
    ## Gráfico Fourier x Tempo do áudio filtrado
    ## Gráfico Fourier x Tempo do áudio modulado

if __name__ == "__main__":
    main()
