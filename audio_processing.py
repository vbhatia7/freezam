#########################################
### Author: Vinni Bhatia
### Last Edited: Nov 21, 2020
### Use: Read in WAVs/Convert to MP3s
#########################################


import os
import wave
from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
import sys
import logging
import urllib.request

#need to specify path of tool that we use
AudioSegment.converter = "C:/Users/vinay/Documents/ffmpeg/ffmpeg/bin/ffmpeg.exe"

# audio_files = os.listdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/Test_MP3s")
# for filename in audio_files:
#     os.chdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/Test_MP3s")
#     name, ext = os.path.splitext(filename)
#     if filename.endswith(".mp3"): 
#         sound = AudioSegment.from_mp3(filename)
#         sound.export("../WAVs/{0}.wav".format(name), format="wav")

# audio_files = os.listdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/Songs_not_in_database/MP3s")
# for filename in audio_files:
#     os.chdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/Songs_not_in_database/MP3s")
#     name, ext = os.path.splitext(filename)
#     if filename.endswith(".mp3"): 
#         sound = AudioSegment.from_mp3(filename)
#         sound.export("../WAVs/{0}.wav".format(name), format="wav")        


#File takes one parameter - filename - which should lead to mp3
def convert_to_local_wav(path, source):
    """Function takes one mp3 from either your local PC or a URL
    and converts it to a WAV file.
    
    Input parameters: file path(str) 
                      source (str)
                      
    Output parameters: Nothing returned.                  
    """
    if(source == "local"):
        filename = os.path.basename(path)
        name,ext = os.path.splitext(filename)
        if ext==".mp3": 
            sound = AudioSegment.from_mp3(path)
            sound.export("WAVs/{0}.wav".format(name), format="wav")
    if(source == "url"):
        filename = os.path.basename(path)
        name,ext = os.path.splitext(filename)
        if ext==".mp3": 
            fullfilename = os.path.join("Test_MP3s", filename)
            urllib.request.urlretrieve(path,fullfilename)
            sound = AudioSegment.from_mp3(fullfilename)
            sound.export("WAVs/{0}.wav".format(name), format="wav")
        if ext==".wav": 
            fullfilename = os.path.join("WAVs", filename)
            urllib.request.urlretrieve(path,fullfilename)
   

