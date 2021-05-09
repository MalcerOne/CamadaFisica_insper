from scipy.fftpack import fft, next_fast_len
from scipy import signal as window
import numpy as np
import scipy.signal as sg

def filtro(y, samplerate, cutoff_hz):
  # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
    nyq_rate = samplerate/2
    width = 5.0/nyq_rate
    ripple_db = 60.0 #dB
    N , beta = sg.kaiserord(ripple_db, width)
    taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    yFiltrado = sg.lfilter(taps, 1.0, y)
    return yFiltrado

def LPF(signal, cutoff_hz, fs):
        from scipy import signal as sg
        #####################
        # Filtro
        #####################
        # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
        nyq_rate = fs/2
        width = 5.0/nyq_rate
        ripple_db = 60.0 #dB
        N , beta = sg.kaiserord(ripple_db, width)
        taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
        return( sg.lfilter(taps, 1.0, signal))

def calcFFT(self, signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        W = window.hamming(N)
        T  = 1/fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal*W)
        return(xf, np.abs(yf[0:N//2]))

def generateSin(self, freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return x, s

def normalizeAudio(wavfile):
        minimum = abs(wavfile.min())
        maximum = abs(wavfile.max())

        if maximum > minimum:
                maxAbs = maximum
        else:
                maxAbs = minimum
        
        return wavfile*(1/maxAbs)

def play(audio):
        sd.play(audio, 44100)
        sd.wait()