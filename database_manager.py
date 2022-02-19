#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 17, 2020
### Use: Manages songs in a database
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
import ast
import matplotlib.pyplot as plt


#Connecting to database
conn = psycopg2.connect(
    host="sculptor.stat.cmu.edu",
    database=credentials.DB_USER,
    user=credentials.DB_USER,
    password=credentials.DB_PASSWORD
)
cur = conn.cursor()

# Creating our main tables

def create_tables():
     """
    Function takes no arguments but.
    
    Inputs: None

    Outputs: Creates two tables in Postgres database
    """
cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    song_id SERIAL PRIMARY KEY,
    title text NOT NULL CHECK (char_length(title) > 0),
    artist text NOT NULL CHECK (char_length(artist) > 0),
    album text NOT NULL CHECK (char_length(album) > 0),
    path text NOT NULL CHECK (char_length(path) > 0),
    sample_rate numeric NOT NULL CHECK (sample_rate > 0),
    date text NOT NULL CHECK (char_length(date) > 0),
    source text NOT NULL CHECK (char_length(source) > 0)
);
CREATE TABLE IF NOT EXISTS fingerprints_slow_search (
    song_id integer NOT NULL CHECK (song_id > 0),
    fingerprint_id SERIAL NOT NULL,
    num_fingerprints numeric NOT NULL CHECK (num_fingerprints > 0),
    fingerprint1 NUMERIC ARRAY NOT NULL,
    fingerprint5 NUMERIC ARRAY NOT NULL,
    PRIMARY KEY (song_id, fingerprint_id),
    FOREIGN KEY (song_id) REFERENCES songs (song_id) MATCH FULL ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS fingerprints (
    song_id integer NOT NULL CHECK (song_id > 0),
    fingerprint_id SERIAL NOT NULL,
    num_fingerprints numeric NOT NULL CHECK (num_fingerprints > 0),
    fingerprint1 cube NOT NULL,
    fingerprint5 cube NOT NULL,
    PRIMARY KEY (song_id, fingerprint_id),
    FOREIGN KEY (song_id) REFERENCES songs (song_id) MATCH FULL ON DELETE CASCADE
);
    """)
conn.commit()


def add_function(path, title, artist, album, date, source):
    """
    Function takes one filepath to audio file and adds it to our database.
    
    Inputs: path (str, path to mp3 or wav file)
            title (str)
            artist (str)
            album (str)
            date (str)
            source (str, either local or url)

    Outputs: Nothing
    """
    # First, convert to local wav and get fingerprints
    convert_to_local_wav(path, source)
    filename = os.path.basename(path)
    name,ext = os.path.splitext(filename)
    wav_name = name + ".wav"
    wav_path = os.path.join("WAVs", wav_name)
    samplerate,series_results = spectral_analysis.analyze_song(wav_path)
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h=5,delta=1)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h=5,delta=1)
    fingerprints1 = spectral_analysis.fingerprint_one(pd,freq)
    len_fingerprints = int(len(fingerprints1))
    fingerprints5 = spectral_analysis.fingerprint_five(pd,freq)

    # add it to our database
    cur.execute("INSERT INTO songs (title, artist, album, path, sample_rate, date, source) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)", (title, artist, album, path, samplerate, date, source))

    cur.execute("DELETE FROM songs a USING songs b WHERE a.song_id > b.song_id AND a.title = b.title AND a.artist = b.artist AND a.album = b.album and a.path = b.path and a.sample_rate = b.sample_rate;")            
    conn.commit()

    cur.execute("SELECT song_id from songs where title = %s and artist = %s and album = %s", (title,artist,album))
    song_id = cur.fetchall() 

    for i in range(len(fingerprints1)):
        cur.execute("INSERT INTO fingerprints (song_id, num_fingerprints, fingerprint1, fingerprint5) "
                "VALUES (%s, %s, cube(%s), cube(%s))", (song_id[0][0], len_fingerprints, list(fingerprints1[i]), list(fingerprints5[i])))
        conn.commit()  

    cur.execute("DELETE FROM fingerprints a USING fingerprints b WHERE a.fingerprint_id > b.fingerprint_id AND a.num_fingerprints = b.num_fingerprints AND a.fingerprint1 = b.fingerprint1 AND a.fingerprint5 = b.fingerprint5;")            
    conn.commit()

    return(print(title + " by " + artist + " added."))

# wav_files = os.listdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/WAVs")
# for filename in wav_files:
#     #os.chdir("C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/WAVs")
#     name, ext = os.path.splitext(filename)
#     path = "WAVs/" + filename
#     positions = name.split('_')
#     print(positions)
#     add_function(path = "WAVs/" + filename,
#                                   title = positions[0],
#                                   artist = positions[1],
#                                   album = positions[2],
#                                   date = positions[3],
#                                   source = "local")



def remove_function(title, artist, album):
    """
    Function takes a title, artist, and album and removes the song in the directory if it exists.
    
    Inputs: title (str)
            artist (str)
            album (str)

    Outputs: Nothing
    """

    cur.execute("DELETE FROM songs where title = %s and artist = %s and album = %s", (title,artist,album))       
    conn.commit()
    return(print(title + " by " + artist + " removed, if it exists."))


# remove_function(title = "SoundHelix-Song-6",
#                 album = "SH",
#                 artist = "SH")  


def update_album_function(title, artist, new_album):
    """
    Function updates the album of a track in our database, provided with the title and artist.
    
    Inputs: title (str)
            artist (str)
            new_album (str)

    Outputs: Nothing
    """
    cur.execute("UPDATE songs set album = %s where title = %s and artist = %s", (new_album, title, artist))
    conn.commit()
    return(print(title + " by " + artist + " has been updated with a new album: " + new_album))


# update_album_function(title = "betty",
#                        artist = "Taylor Swift",
#                        new_album = "folklore")
              

def update_artist_function(title, new_artist, album):
    """
    Function updates the artist of a track in our database, provided with the title and album.
    
    Inputs: title (str)
            new_artist (str)
            album (str)

    Outputs: Nothing
    """
    cur.execute("UPDATE songs set artist = %s where title = %s and album = %s",(new_artist, title, album))
    conn.commit()
    return(print(title + " by " + new_artist + " has been updated to reflect the correct artist."))


# update_artist_function(title = "betty",
#                        new_artist = "Taylor Swift",
#                        album = "folklore")

def list_function():
    """
    Function lists all the songs in our directory.
    
    Inputs: Nothing

    Outputs: Nothing
    """
    cur.execute("SELECT * from songs;")
    df_to_print = cur.fetchall()
    df_to_print = pandas.DataFrame(df_to_print, columns=['song_id','title','artist', "album", "path", "sample_rate", "year", "source"])
    return(print(df_to_print))    

# list_function()

## this is my slowSearch function
def slow_search(path, source, epsilon, method):
    """
    Function implements a slow search over our database
    
    Inputs: path (string, path to snippet)
            source (string, local, recording, or url)
            epsilon (integer, what threshold level is acceptable to you)
            method (str, which fingerprint you'd like to use! probably a better way to do this. ideally allow users to input their own fingerprint)

    Outputs: Either match found and the match or no match found.
    """
    samplerate,series_results = spectral_analysis.analyze_song(path)
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h=5,delta=1)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h=5,delta=1)
    if method == "one":
        fingerprints = spectral_analysis.fingerprint_one(pd,freq)
    if method == "five":
        fingerprints = spectral_analysis.fingerprint_five(pd,freq)
    cur.execute("SELECT songs.title,songs.artist,fingerprints.* from songs, fingerprints where fingerprints.song_id = songs.song_id;")
    finger_df = cur.fetchall()
    finger_df = pandas.DataFrame(finger_df, columns=['title', 'artist', 'song_id', 'finger_id','num_fingerprints','finger1', 'finger5']) 
    for index_row in finger_df.song_id.unique():
        if method == "one":
            finger_song_mat = finger_df[finger_df['song_id']==index_row] 
            finger_mat=list()
            for i in range(len(finger_song_mat.finger1)):
                finger_mat.append(list(ast.literal_eval(finger_song_mat.finger1.iloc[i])))
            df_dist = spectral_analysis.match_fingerprints(snip_fingerprint = fingerprints,
                                    song_fingerprint = np.array(finger_mat))                                  
            if spectral_analysis.return_match(df_dist,epsilon) == "Match!":
                return("Match Found!: " + str(finger_song_mat['title'].iloc[0]) + " by " + str(finger_song_mat['artist'].iloc[0])  + ".") 
            else:
                next
        if method == "five":
            finger_song_mat = finger_df[finger_df['song_id']==index_row] 
            finger_mat=list()
            for i in range(len(finger_song_mat.finger5)):
                finger_mat.append(list(ast.literal_eval(finger_song_mat.finger5.iloc[i])))
            df_dist = spectral_analysis.match_fingerprints(snip_fingerprint = fingerprints,
                                    song_fingerprint = np.array(finger_mat))  
            if spectral_analysis.return_match(df_dist,epsilon) == "Match!":
                return("Match Found!: " + str(finger_song_mat['title'].iloc[0]) + " by " + str(finger_song_mat['artist'].iloc[0])  + ".") 
            else:
                next
    #If no songs are returned            
    return("Freezam could not find accurate match.")  


def fast_search(source, epsilon, method, path = ""):
    """
    Function implements a fast search over our database using hashing (cube function from Postgres)
    
    Inputs: path (string, path to snippet)
            source (string, local, recording, or url)
            epsilon (integer, what threshold level is acceptable to you)
            method (str, which fingerprint you'd like to use! probably a better way to do this. ideally allow users to input their own fingerprint)

    Outputs: Either match found and the match or no match found.
    """
    if source == "local":
        samplerate,series_results = spectral_analysis.analyze_song(path)
    if source == "recording":
        samplerate,series_results = spectral_analysis.record_song() 
    windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h=5,delta=1)
    freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h=5,delta=1)
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
    if not less_than_ep.empty:
        finger_song_mat = finger_df[finger_df['song_id']==less_than_ep.index[0][0]]
        if less_than_ep.iloc[0] > .05*len(fingerprints):
            return("Match Found!: " + str(finger_song_mat['title'].iloc[0]) + " by " + str(finger_song_mat['artist'].iloc[0]) + ".")
    notmatch = (finger_df.groupby(['song_id','title'])['distance'].count()).sort_values(ascending=False)
    finger_song_mat = finger_df[finger_df['song_id']==notmatch.index[0][0]]
    return("Freezam could not find accurate match. The closest song is " + str(finger_song_mat['title'].iloc[0]) + " by " + str(finger_song_mat['artist'].iloc[0]) + ".")  

def recommend(path_to_data):
    """
    Function allows a user to input a directory of songs and outputs a list of songs/artists that the user may like
    
    Inputs: path (string, path to database)

    Outputs: Provides a list of the 10 closest songs and 10 closest artists to the given directory.
    """
    wav_files = os.listdir(path_to_data)
    owd = os.getcwd()
    os.chdir(path_to_data)
    ultimate_df = pandas.DataFrame(columns=['song_id', 'f_id', 'title', 'artist', 'distance'])
    for filename in wav_files:
        samplerate,series_results = spectral_analysis.analyze_song(filename)
        windows = spectral_analysis.get_window(series = series_results, sample_rate = samplerate, h=5,delta=1)
        freq,pd = spectral_analysis.get_periodogram(series_results,windows,samplerate,h=5,delta=1)
        cur.execute("SELECT songs.title,songs.artist,fingerprints.* from songs, fingerprints where fingerprints.song_id = songs.song_id;")
        finger_df = pandas.DataFrame(columns=['song_id', 'f_id', 'title', 'artist', 'distance'])
        fingerprints = spectral_analysis.fingerprint_one(pd,freq)
        for index_row in range(int(len(fingerprints))):
            cur.execute("SELECT songs.song_id,fingerprint_id,songs.title,songs.artist,fingerprint1 <-> cube(%s) as euclidean FROM fingerprints,songs where fingerprints.song_id = songs.song_id ORDER BY fingerprint1 <-> cube(%s) LIMIT 1;", (list(fingerprints[index_row]), list(fingerprints[index_row])))
            matches_df_records = cur.fetchall()
            matches_df = pandas.DataFrame(matches_df_records, columns=['song_id', 'f_id', 'title', 'artist','distance'])
            finger_df = finger_df.append(matches_df)      
        min_dist_df = finger_df[finger_df['distance'] == finger_df['distance'].min()]
        ultimate_df = ultimate_df.append(min_dist_df)  
    closest_songs = ultimate_df.groupby(['title'])['distance'].count().sort_values(ascending=False).head(10)
    closest_artists =  ultimate_df.groupby(['artist'])['distance'].count().sort_values(ascending=False).head(10)
    os.chdir(owd)    
    return(closest_songs,closest_artists)
    