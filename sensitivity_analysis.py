#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 7, 2020
### Use: Tests sensitivity of our algorithm
#########################################


import os
import numpy as np
import sys
from audio_processing import convert_to_local_wav
import pandas
import spectral_analysis
import psycopg2
import credentials
import random
import time

#Connecting to database
conn = psycopg2.connect(
    host="sculptor.stat.cmu.edu",
    database=credentials.DB_USER,
    user=credentials.DB_USER,
    password=credentials.DB_PASSWORD
)
cur = conn.cursor()

# Songs that are in database (fast search)
def test_songs_in_database(N, method, epsilon, source):
    start = time.time()
    correct = 0
    incorrect = 0
    for _ in range(N):
        filename = random.choice(os.listdir("WAVs"))
        print(filename)
        path = "WAVs/" + filename
        samplerate,series_results = spectral_analysis.analyze_song(path)
        random_length = random.randrange(10,24)
        random_start = random.randrange(0,len(series_results) - random_length*samplerate)
        new_series = series_results[random_start:(random_start + random_length*samplerate - 1)]
        windows = spectral_analysis.get_window(series = new_series, sample_rate = samplerate, h=5,delta=1)
        freq,pd = spectral_analysis.get_periodogram(new_series,windows,samplerate,h=5,delta=1)
        cur.execute("SELECT songs.title,songs.artist,fingerprints.* from songs, fingerprints where fingerprints.song_id = songs.song_id;")
        finger_df = pandas.DataFrame(columns=['song_id', 'f_id', 'title', 'artist', 'distance'])     
        if method == "one":
            fingerprints = spectral_analysis.fingerprint_one(pd,freq)
            for index_row in range(int(len(fingerprints))):
                cur.execute("SELECT songs.song_id,fingerprint_id,songs.title,songs.artist,fingerprint1 <-> cube(%s) as euclidean FROM fingerprints,songs where fingerprints.song_id = songs.song_id ORDER BY fingerprint1 <-> cube(%s) LIMIT 1;", (list(fingerprints[index_row]), list(fingerprints[index_row])))
                matches_df_records = cur.fetchall()
                matches_df = pandas.DataFrame(matches_df_records, columns=['song_id', 'f_id', 'title', 'artist','distance']) 
                finger_df = finger_df.append(matches_df)
        if method == "five":
            fingerprints = spectral_analysis.fingerprint_five(pd,freq)
            for index_row in range(int(len(fingerprints))):
                cur.execute("SELECT songs.song_id,fingerprint_id,songs.title,songs.artist,fingerprint5 <-> cube(%s) as euclidean FROM fingerprints,songs where fingerprints.song_id = songs.song_id ORDER BY fingerprint5 <-> cube(%s) LIMIT 1;", (list(fingerprints[index_row]), list(fingerprints[index_row])))
                matches_df_records = cur.fetchall()
                matches_df = pandas.DataFrame(matches_df_records, columns=['song_id', 'f_id', 'title', 'artist','distance']) 
                finger_df = finger_df.append(matches_df)
        less_than_ep = (finger_df[finger_df['distance'] < epsilon].groupby(['song_id','title'])['distance'].count()).sort_values(ascending=False)
        positions = filename.split('_')
        print(less_than_ep)
        if not less_than_ep.empty:
            finger_song_mat = finger_df[finger_df['song_id']==less_than_ep.index[0][0]]
            if less_than_ep[0] > .05*len(fingerprints) and str(finger_song_mat['title'].iloc[0]) == positions[0]:
                correct += 1
            else:
                incorrect += 1
        else:
            incorrect += 1
    end = time.time()        
    print("# Correct (fast search): " + str(correct))
    print("# Num Incorrect (fast search): " + str(incorrect))    
    print("Time taken (fast search): " + str(end - start))


# Songs that are in database (fast search)
def test_songs_not_in_database(N, method, epsilon, source):
    start = time.time()
    correct = 0
    incorrect = 0
    for _ in range(N):
        filename = random.choice(os.listdir("Songs_not_in_database/WAVs"))
        print(filename)
        path = "Songs_not_in_database/WAVs/" + filename
        samplerate,series_results = spectral_analysis.analyze_song(path)
        random_length = random.randrange(10,24)
        random_start = random.randrange(0,len(series_results) - random_length*samplerate)
        new_series = series_results[random_start:(random_start + random_length*samplerate - 1)]
        windows = spectral_analysis.get_window(series = new_series, sample_rate = samplerate, h=5,delta=1)
        freq,pd = spectral_analysis.get_periodogram(new_series,windows,samplerate,h=5,delta=1)
        cur.execute("SELECT songs.title,songs.artist,fingerprints.* from songs, fingerprints where fingerprints.song_id = songs.song_id;")
        finger_df = pandas.DataFrame(columns=['song_id', 'f_id', 'title', 'artist', 'distance'])     
        if method == "one":
            fingerprints = spectral_analysis.fingerprint_one(pd,freq)
            for index_row in range(int(len(fingerprints))):
                cur.execute("SELECT songs.song_id,fingerprint_id,songs.title,songs.artist,fingerprint1 <-> cube(%s) as euclidean FROM fingerprints,songs where fingerprints.song_id = songs.song_id ORDER BY fingerprint1 <-> cube(%s) LIMIT 1;", (list(fingerprints[index_row]), list(fingerprints[index_row])))
                matches_df_records = cur.fetchall()
                matches_df = pandas.DataFrame(matches_df_records, columns=['song_id', 'f_id', 'title', 'artist','distance']) 
                finger_df = finger_df.append(matches_df)
        if method == "five":
            fingerprints = spectral_analysis.fingerprint_five(pd,freq)
            for index_row in range(int(len(fingerprints))):
                cur.execute("SELECT songs.song_id,fingerprint_id,songs.title,songs.artist,fingerprint5 <-> cube(%s) as euclidean FROM fingerprints,songs where fingerprints.song_id = songs.song_id ORDER BY fingerprint5 <-> cube(%s) LIMIT 1;", (list(fingerprints[index_row]), list(fingerprints[index_row])))
                matches_df_records = cur.fetchall()
                matches_df = pandas.DataFrame(matches_df_records, columns=['song_id', 'f_id', 'title', 'artist','distance']) 
                finger_df = finger_df.append(matches_df)
        less_than_ep = (finger_df[finger_df['distance'] < epsilon].groupby(['song_id','title'])['distance'].count()).sort_values(ascending=False)
        print(less_than_ep)
        if not less_than_ep.empty:
            #if no match - great! otherwise bad
            if less_than_ep[0] < .05*len(fingerprints):
                correct += 1
            else:
                incorrect += 1
        else:
            correct += 1
    end = time.time()         
    print("# Correct (fast search): " + str(correct))
    print("# Num Incorrect (fast search): " + str(incorrect))    
    print("Time taken (fast search): " + str(end - start))           

# epsilon_one = 1e-06

# print(test_songs_in_database(N = 50,method = "one", epsilon = epsilon_one, source = "local"))
# print(test_songs_not_in_database(N = 50,method = "one", epsilon = epsilon_one, source = "local"))


epsilon_five = 10000

print(test_songs_in_database(N = 50,method = "five", epsilon = epsilon_five, source = "local"))
print(test_songs_not_in_database(N = 50,method = "five", epsilon = epsilon_five, source = "local"))
