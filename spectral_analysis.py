#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 7, 2020
### Use: Analyze MP3s from audio_processing file.
#########################################

import os
import wave
from pydub import AudioSegment
from scipy import signal
from scipy.io import wavfile
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import sys
import logging
from skimage import util
from scipy.spatial import distance
from pandas import DataFrame
from pandas import Series
from sklearn import preprocessing
import sounddevice as sd
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Started')


#Function which reads in WAV and returns time series
def analyze_song(path):
    """
    Function reads in a WAV, processes it, and returns a series.

    Inputs: Path to WAV file (string)

    Outputs: The samplerate (integer) and series data (numpy.ndarray) of the WAV file
    """
    name,ext = os.path.splitext(path)
    assert ext == ".wav", "Must input a .wav!"
    samplerate, data = wavfile.read(path)
    #Convert to mono
    if len(data.shape) > 1:
        series_results = np.mean(data,axis=1) 
    else:
        series_results = np.array(data)      
    logger.info('Read in WAV, returned series') 
    return([samplerate, series_results])


def record_song(length = 15):
    """
    Function allows user to record audio for specified time period (> 5 seconds, < 23 seconds!)

    Inputs: Length of song in seconds

    Outputs: The samplerate (integer) and series data (numpy.ndarray) of the WAV recording
    """
    #assert length > 10 and length < 30, "Length cannot be too short or too long!"
    samplerate = 44100  
    seconds = length
    logger.info("Starting recording now!") 
    print("Recording in:")
    print("3...")
    time.sleep(0.99)
    print("2...")
    time.sleep(0.99)
    print("1...")
    time.sleep(0.99)
    print("Go!")
    data = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()
    logger.info("Just finished recording!") 
    wavfile.write("temp/output.wav", samplerate, data)
    if len(data.shape) > 1:
        series_results = np.mean(data,axis=1) 
    else:
        series_results = np.array(data)      
    series_results_final = series_results
    logger.info('Recorded audio, returned series') 
    return([samplerate, series_results_final])


   

def get_window(series, sample_rate, h = 5, delta = 1):
    """
    Function reads in a series (from analyze_song), and returns the windowing of the function.

    Inputs: Series of WAV file (numpy.ndarray), 
            Sample_rate (integer), 
            h (integer meant to represent window length, default is 5s), 
            delta (integer meant to represent window size, default is 1s)

    Outputs: Windowed Series (numpy.ndarray)
    """

    #song_in_seconds = len(series)/sample_rate
    #window_centers = np.arange(start=0, stop=song_in_seconds,step=1)
    hamming_window = signal.get_window("hamming", h*sample_rate)
    window_signals = util.view_as_windows(series, window_shape=(h*sample_rate,), step=delta*sample_rate)
    windowed_results = np.multiply(hamming_window, window_signals)
    logger.info('Got windows of series')
    return(windowed_results)


def get_periodogram(series,windows,sampling_rate,h,delta):
    """
    Function reads in a window (from get_window), windows the function, and returns the periodogram.

    Inputs: Windowed Series (numpy.ndarray)
            Sampling Rate (integer)
            h (integer meant to represent window length, default is 5s), 
            delta (integer meant to represent window size, default is 1s)

    Outputs: frequencies (list of frequencies for each window)
             power_densities (list of power_densities for each window)
    """
    # Analyze each window piece
    frequencies =[]
    power_densities =[]
    for window in windows:
        sample_freq, power_density = signal.periodogram(x = window, fs = sampling_rate, scaling="spectrum")
        frequencies.append(sample_freq)
        power_densities.append(power_density)
    logger.info('Computed periodogram of series')    
    return(frequencies,power_densities)
 

def plot_spectrogram(series,sampling_rate):
    """
    Function reads in a series and plots the spectrogram.
    
    Inputs: Series (numpy.ndarray)
            Sampling_Rate (integer)
            
    Outputs: Plot of a spectrogram
    """
    plt.specgram(series, Fs=sampling_rate, cmap="gist_rainbow")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.show()
    logger.info('Plotted spectrogram of series')


def plot_spectrogram_file(filepath):
    """
    Function reads in a series and plots the spectrogram.
    
    Inputs: Series (numpy.ndarray)
            Sampling_Rate (integer)
            
    Outputs: Plot of a spectrogram
    """
    sampling_rate,series = analyze_song(filepath)
    plt.specgram(x = series, Fs=sampling_rate, cmap="gist_rainbow")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.title("Spectrogram of given audio file")
    plt.savefig("temp/temp_plot.png")
    logger.info('Plotted spectrogram of series')    


def fingerprint_one(power_density,freq):
    """
    Function computes the fingerprints of an audio file using technique 4 in Shazam.pdf (frequencies which periodogram has peak)
    
    Inputs: power_density (list of power_densities for each window)
            freq (list of frequencies for each window)

    Outputs: finger1 (list of fingerprints for each window)
    """
    finger1 = []
    for index1 in range(int(len(power_density))):
        freq2 = np.array(freq[index1])
        peaks,_ = signal.find_peaks(power_density[index1])
        if len(peaks >= 3):
            freq_peaks = freq2[peaks]
            max100 = np.argpartition(power_density[index1][peaks], -3)[-3:]
            f1 = freq_peaks[max100]
            max_f1 = max(freq_peaks)
            f2 = np.true_divide(f1, max_f1)
            finger1.append(f2)
        else: 
            f2 = (0,0,0)
            finger1.append(f2)
    logger.info('Computed fingerprint method 1')    
    return(finger1) 


def fingerprint_two(power_density,freq):
    """
    Function computes the fingerprints of an audio file using roughly technique 1 in Shazam.pdf (local periodograms, but truncates them and to 0.35 power)
    
    Inputs: power_density (list of power_densities for each window)
            freq (list of frequencies for each window)

    Outputs: finger2 (list of fingerprints for each window)
    """
    finger2 = []
    for index1 in range(int(len(power_density))):
        pd_short = [j for (i,j) in zip(freq[index1],power_density[index1]) if i <= 2000]
        pd_mod = [x**0.35 for x in pd_short]
        finger2.append(pd_mod)
    logger.info('Computed fingerprint method 2')     
    return(finger2)   


def fingerprint_five(power_density,freq):
    """
    Function computes the fingerprints of an audio file using roughly technique 5 in Shazam.pdf (max at octaves)
    
    Inputs: power_density (list of power_densities for each window)
            freq (list of frequencies for each window)

    Outputs: finger5 (list of fingerprints for each window)
    """
    finger5 = []
    num_octaves = 8
    samplerate = len(power_density[1])
    for index1 in range(int(len(power_density))):
        pd_short = [j for (i,j) in zip(freq[index1],power_density[index1]) if i <= 5000]
        #pd_short = power_density[index1]
        finger5_octave = []
        for octave_iter in range(num_octaves):
            start_freq = round(2**(-(num_octaves - octave_iter))*5000/2)
            end_freq = round(2**(-(num_octaves - octave_iter)+1)*5000/2)
            pd_mod = pd_short[start_freq:end_freq]
            max_pd_octave = max(pd_mod)
            finger5_octave.append(max_pd_octave)
        finger5.append(finger5_octave)    
    logger.info('Computed fingerprint method 5')     
    return(finger5)         


def match_fingerprints(snip_fingerprint,song_fingerprint):
    """
    Function computes the "distance" between two fingerprints for each window.
    
    Inputs: snip_fingerprints (list of fingerprints for snippet)
            song_fingerprints (list of fingerprints for song)

    Outputs: dist (pandas DataFrame)
    """
    df1 = DataFrame(snip_fingerprint).T
    df2 = DataFrame(song_fingerprint).T
    dist = np.empty([int(len(df2.columns)), int(len(df1.columns))])
    for index1 in range(int(len(df1.columns))):
        array_dist = []
        for index2 in range(int(len(df2.columns))):
            distance_pd = distance.euclidean(df1[index1], df2[index2])
            array_dist.append(distance_pd)
        dist[:, index1] = array_dist 
    df_dist = DataFrame(dist)
    logger.info('Computed distance between fingerprints') 
    return(df_dist) 


def return_match(dist,epsilon):
    """
    Function returns whether a song and snippet are matched based on a prespecified epsilon value and the distance list between them
    
    Inputs: dist (pandas DataFrame of distances between snippet fingerprints and song fingerprints)
            epsilon (integer meant to represent acceptable tolerance between two fingerprints)

    Outputs: Either match or no match (string)
    """
    tf_matrix = ((dist < epsilon))
    logger.info('Computing distance between two fingerprints') 
    for index1 in range(int(-abs(len(dist.index) - len(dist.columns))),0):
        ind_tf = np.diag(tf_matrix,index1)
        if (all(ind_tf) or sum(ind_tf) >= .05*len(ind_tf)):
            return("Match!")
    return("Not a match.")        

## EPSILON VALUES

# Finger 1 ~ 1e-6 (by far the most accurate method!!)
# Finger 2 ~ 100
# Finger 5 ~ 10000

