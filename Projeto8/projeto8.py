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

    ## Normalizar o sinal
    audioNormalizado = normalizeAudio(audio)
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
    audioModAM = np.dot(carrier, audioFiltered)

    ## Reproduzir o sinal (não é perfeitamente audível)
    print(f"\n[+]---Tocando o audio modulado (não é audível)\n")
    print(audioModAM)
    sd.play(audioModAM)
    sd.wait()

    ## Gráfico Fourier x Tempo do áudio original
    arrayAudioOriginal = np.ndarray(shape=(88200,),dtype=np.float32)
    for i in range(0,arrayAudioOriginal.shape[0]):
        arrayAudioOriginal[i] = audio[i][0]

    tempo = np.linspace(0, duration, 44100)
    xf, yf = calcFFT(arrayAudioOriginal, 44100)
    plt.plot(xf, yf, label="Áudio Original")
    plt.title("Fourier do áudio original")
    plt.xlabel("Frequências")
    plt.legend()
    plt.savefig("FourierAudioOriginal.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio normalizado
    arrayAudioNormalizado = np.ndarray(shape=(88200,),dtype=np.float32)
    for i in range(0,arrayAudioNormalizado.shape[0]):
        arrayAudioNormalizado[i] = audioNormalizado[i][0]

    tempo = np.linspace(0, duration, 44100)
    xf, yf = calcFFT(arrayAudioNormalizado, 44100)
    plt.plot(xf, yf, label="Áudio Normalizado")
    plt.title("Fourier do áudio normalizado")
    plt.xlabel("Frequências")
    plt.legend()
    plt.savefig("FourierAudioNormalizado.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio filtrado
    arrayAudioFiltered = np.ndarray(shape=(88200,),dtype=np.float32)
    for i in range(0,arrayAudioFiltered.shape[0]):
        arrayAudioFiltered[i] = audioFiltered[i][0]

    tempo = np.linspace(0, duration, 44100)
    xf, yf = calcFFT(arrayAudioFiltered, 44100)
    plt.plot(xf, yf, label="Áudio Filtrado")
    plt.title("Fourier do áudio filtrado")
    plt.xlabel("Frequências")
    plt.legend()
    plt.savefig("FourierAudioFiltrado.jpg")
    plt.show()

    ## Gráfico Fourier x Tempo do áudio modulado
    arrayAudioModAM = np.ndarray(shape=(88200,),dtype=np.float32)
    for i in range(0,arrayAudioModAM.shape[0]):
        arrayAudioModAM[i] = audioModAM[i][0]

    tempo = np.linspace(0, duration, 44100)
    xf, yf = calcFFT(arrayAudioModAM, 44100)
    plt.plot(xf, yf, label="Áudio Modulado")
    plt.title("Fourier do áudio modulado")
    plt.xlabel("Frequências")
    plt.legend()
    plt.savefig("FourierAudioModulado.jpg")
    plt.show()
if __name__ == "__main__":
    main()
