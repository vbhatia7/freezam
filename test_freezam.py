#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 17, 2020
### Use: Test the functions that make up Freezam.
#########################################

## pytest -v test_freezam.py
## All test functions must start with test_.

import pytest
import audio_processing
import spectral_analysis
import database_manager
import random
import math
import psycopg2
import credentials


conn = psycopg2.connect(
    host="sculptor.stat.cmu.edu",
    database=credentials.DB_USER,
    user=credentials.DB_USER,
    password=credentials.DB_PASSWORD
)
cur = conn.cursor()

@pytest.mark.parametrize("path,h,delta", [("WAVs/betty_Taylor Swift_folklore_2020.wav", 5, 1), ("WAVs/Cruel Summer_Taylor Swift_Lover_2019.wav", 10, 3), ("WAVs/Paper Rings_Taylor Swift_Lover_2019.wav", 12, 7)])
def test_get_window(path,h,delta):
    """
    Function tests the get_window() function.

    Inputs: path (string, filepath to wav)
            h (integer, length of window in seconds)
            delta (integer, length of window step in seconds)

    Outputs: assertion        
    """
    samplerate,series_results = spectral_analysis.analyze_song(path)
    song_in_seconds = len(series_results)/samplerate
    rounded_sec = math.ceil(song_in_seconds)
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h = h, delta = delta)
    assert (len(windows) == math.ceil((rounded_sec-h)/delta))
    assert (len(windows[1])) == (samplerate*h)

@pytest.mark.parametrize("path,h,delta", [("WAVs/betty_Taylor Swift_folklore_2020.wav", 5, 1), ("WAVs/Cruel Summer_Taylor Swift_Lover_2019.wav", 10, 3), ("WAVs/Paper Rings_Taylor Swift_Lover_2019.wav", 12, 7)])
def test_get_periodogram(path,h,delta):
    """
    Function tests the get_periodogram() function.

    Inputs: path (string, filepath to wav)
            h (integer, length of window in seconds)
            delta (integer, length of window step in seconds)

    Outputs: assertion        
    """
    samplerate,series_results = spectral_analysis.analyze_song(path)
    song_in_seconds = len(series_results)/samplerate
    rounded_sec = math.ceil(song_in_seconds)
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h = h, delta = delta)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h = h,delta = delta)
    assert (len(freq) == math.ceil((rounded_sec-h)/delta))
    assert (len(freq[1])) == ((samplerate*h/2) + 1)

    assert (len(pd) == math.ceil((rounded_sec-h)/delta))
    assert (len(pd[1])) == ((samplerate*h/2) + 1)


@pytest.mark.parametrize("path,h,delta", [("WAVs/betty_Taylor Swift_folklore_2020.wav", 5, 1), ("WAVs/Cruel Summer_Taylor Swift_Lover_2019.wav", 10, 3), ("WAVs/Paper Rings_Taylor Swift_Lover_2019.wav", 12, 7)])
def test_fingerprint_two(path,h,delta):
    """
    Function tests the get_fingerprint_two() function.

    Inputs: path (string, filepath to wav)
            h (integer, length of window in seconds)
            delta (integer, length of window step in seconds)

    Outputs: assertion        
    """
    samplerate,series_results = spectral_analysis.analyze_song(path)
    song_in_seconds = len(series_results)/samplerate
    rounded_sec = math.ceil(song_in_seconds)
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h = h, delta = delta)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h = h,delta = delta)
    fingers_two = spectral_analysis.fingerprint_two(pd,freq)
    
    assert (len(fingers_two) == math.ceil((rounded_sec-h)/delta))
    #only because I truncate the frequences at 2000
    assert (len(fingers_two[1]) == 2000*h + 1)


def test_return_match():
    """
    Function tests the return_match() function using various assertions. NOTE: I need to add tests here

    Inputs: Nothing

    Outputs: assertion        
    """
    samplerate,series_results = spectral_analysis.analyze_song("snippets/betty_snippet2.wav")
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h=5,delta=1)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h=5,delta=1)

    samplerate_song,series_results_song = spectral_analysis.analyze_song("WAVs/betty_Taylor Swift_folklore_2020.wav")
    windows_song = spectral_analysis.get_window(series = series_results_song, sample_rate = samplerate_song, h=5,delta=1)
    freq_song,pd_song = spectral_analysis.get_periodogram(series_results_song,windows_song,samplerate_song,h=5,delta=1)

    fingers_two = spectral_analysis.fingerprint_two(pd,freq)
    fingers_two_song = spectral_analysis.fingerprint_two(pd_song,freq_song)
    df_dist = spectral_analysis.match_fingerprints(fingers_two,fingers_two_song)
    assert (spectral_analysis.return_match(df_dist,150) == "Match!")


def test_slow_search():
    """
    Function tests the slow_search() function using various assertions. 

    Inputs: Nothing

    Outputs: assertion        
    """
    assert (database_manager.slow_search(path = "snippets/heavenisaplaceonearth_snippet.wav", 
            source = "local",
            epsilon = 1000,
            method = "five") == "Match Found!: Heaven Is A Place On Earth by Belinda Carlisle.")
    
    #test song NOT in database
    assert (database_manager.slow_search(path = "snippets/perfect_snippet.wav",
            source = "local",
            epsilon = 1000,
            method = "five") == "Freezam could not find accurate match.")


    #Now use other fingerprint method
    assert (database_manager.slow_search(path = "snippets/jarofhearts_snippet.wav", 
            source = "local",
            epsilon = 1e-05,
            method = "one") == "Match Found!: Jar of Hearts by Christina Perri.")

    assert (database_manager.slow_search(path = "snippets/countryroads_snippet.wav", 
            source = "local",
            epsilon = 1e-05,
            method = "one") == "Match Found!: Take Me Home, Country Roads by John Denver.")

    #test song NOT in database
    assert  (database_manager.slow_search(path = "snippets/perfect_snippet.wav",
            source = "local",
            epsilon = 1e-05,
            method = "one")) == "Freezam could not find accurate match."


@pytest.mark.xfail
def test_search_fails():
        #To demonstrate that our algorithm doesn't work 100% of the time
        assert (database_manager.slow_search(path = "snippets/jarofhearts_snippet.wav", 
            source = "local",
            epsilon = 50000,
            method = "five") == "Match Found!: Jar of Hearts by Christina Perri.") 

        assert (database_manager.slow_search(path = "snippets/countryroads_snippet.wav", 
            source = "local",
            epsilon = 50000,
            method = "five") == "Match Found!: Take Me Home, Country Roads by John Denver.")      

                       

## NOTE: extensive testing of fast_search() is done in the sensitivity_analysis.py file. Please refer there for more details.
def test_fast_search():
    """
    Function tests the fast_search() function using various assertions. 

    Inputs: Nothing

    Outputs: assertion        
    """
    assert (database_manager.fast_search(path = "snippets/jarofhearts_snippet.wav", 
            source = "local",
            epsilon = 15000,
            method = "five") == "Match Found!: Jar of Hearts by Christina Perri.")

    assert (database_manager.fast_search(path = "snippets/countryroads_snippet.wav", 
            source = "local",
            epsilon = 15000,
            method = "five") == "Match Found!: Take Me Home, Country Roads by John Denver.")

    #test song NOT in database
    assert ("Freezam could not find accurate match." in database_manager.fast_search(path = "snippets/perfect_snippet.wav",
            source = "local",
            epsilon = 15000,
            method = "five"))       


    #Now use other fingerprint method
    assert (database_manager.fast_search(path = "snippets/jarofhearts_snippet.wav", 
            source = "local",
            epsilon = 1e-06,
            method = "one") == "Match Found!: Jar of Hearts by Christina Perri.")

    assert (database_manager.fast_search(path = "snippets/countryroads_snippet.wav", 
            source = "local",
            epsilon = 1e-06,
            method = "one") == "Match Found!: Take Me Home, Country Roads by John Denver.")

    #test song NOT in database
    assert ("Freezam could not find accurate match" in database_manager.fast_search(path = "snippets/perfect_snippet.wav",
            source = "local",
            epsilon = 1e-06,
            method = "one"))     


def test_add_remove_song():
    """
    Function tests the add_function() and remove_function() functions. 
    NOTE: you should attempt these while betty exists IN the database
    """
    database_manager.remove_function(title = "betty", 
              artist = "Taylor Swift",
              album = "folklore")

    cur.execute("SELECT COUNT(*) from songs where title = %s and artist = %s and album = %s;", ("betty", "Taylor Swift", "folklore")) 
    is_song_there = cur.fetchall()  
    assert is_song_there[0][0] == 0        
    
    database_manager.add_function(path = "Test_MP3s/betty_Taylor Swift_folklore_2020.mp3", 
              title = "betty", 
              artist = "Taylor Swift",
              album = "folklore",
              date = "2020",
              source = "local")


    cur.execute("SELECT COUNT(*) from songs where title = %s and artist = %s and album = %s;", ("betty", "Taylor Swift", "folklore")) 
    is_song_there_now = cur.fetchall() 
    assert is_song_there_now[0][0] != 0            
          
