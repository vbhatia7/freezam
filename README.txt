#############################
### Author: Vinni Bhatia
### Last edited: Dec 17th, 2020
#############################

The goal of this program is to build a shazam-like program which takes in a snippet of an audio file 
and matches it to the closest match within a database of songs. For more details, including detailed
descriptions of the techniques I use, please see the shazam.pdf.


## Python files

There are 6 main python files and 1 main R file which compose the entire program:


audio_processing.py - This file allows the user to take in an mp3 from either their local PC or a URL. This file consists only of one function:
1.) convert_to_local_wav - Function takes one mp3 from either your local PC or a URL and converts it to a WAV file.


database_manager.py - Allows us to edit (add/remove/check if song exists) our song database, which exists as a Postgres table on a server on Sculptor. This file consists of 9 functions:
1.) create_tables - Takes no input, simply creates the table on Postgres. Does nothing if these already exist.
2.) add_function -  Function takes one filepath to audio file and adds it to our database, along with song features such as title, artist, and album. You can also add a song via a URL. 
3.) remove_function -  Function takes a title, artist, and album and removes the song in the directory if it exists.
4.) update_album_function - Function takes a title, artist, and a new album which is meant to replace the old album of a song which already exists in our database.
5.) update_artist_function - Function takes a title, album, and a new artist which is meant to replace the old artist of a song which already exists in our database.
6.) list_function - No inputs -  Function lists all the songs in our directory.
7.) slow_search -  Function implements a slow search over our database, given the database and a path to a snippet. You must specify which fingerprint method (see below) and the epsilon value you'd prefer. You can choose to do this via URL or local snippet.
8.) fast_search - Rather than slow_search, which loops over all songs, fast_search() implements fast hashing via cubes in Postgres. Again, you must provide the path to a snippet, fingerprint method, and epsilon value.
9.) recommend - Instead of matching, let's say you'd like to find some new music to listen to. Now, just insert a path to a database filled with mp3s/wavs, and this will output the 10 closest songs/artists based on our fingerprint method. Currently this uses fingerprint one method, as it's the certainly the most accurate.


spectral_analysis.py - For a WAV file, reads it in, computes the periodogram/spectrogram/signature and
provides a function to match two signature. There are currently 11 functions in this file:
1.) analyze_song - Function reads in a WAV, processes it, and returns a series.
2.) record_song - Function allows a user to record a song with a given length in seconds. Temporarily saves the WAV and outputs the sampling rate and series results.
3.) get_window - Function reads in a series (from analyze_song), and returns the windowing of the function.
4.) get_periodogram - Function reads in a window (from get_window), windows the function, and returns the periodogram.
5.) plot_spectrogram - Function reads in a series and plots the spectrogram.
6.) plot_spectrogram_file - Function reads in a WAV file and plots the spectrogram. (mostly used for Shiny app, see below)
7.) fingerprint_one - Function computes the fingerprints of an audio file using technique 4 in Shazam.pdf (frequencies which periodogram has peak)
8.) fingerprint_two -  Function computes the fingerprints of an audio file using roughly technique 1 in Shazam.pdf (local periodograms, but truncates them and to 0.35 power)
9.) fingerprint_five -  Function computes the fingerprints of an audio file using roughly technique 5 in Shazam.pdf (max power density in each increasing octave)
10.) match_fingerprints - Function computes the "distance" between two fingerprints for each window. Uses regular euclidean distance.
11.) return_match - Function returns whether a song and snippet are matched based on a prespecified epsilon value and the distance list between them. Primarily used for slow search.


sensitivity_analysis.py - Randomly generates an audio snippet from songs that are both in the database and not the database for a specified epsilon value and then tests it on the fast_search() function. There are currently 2 functions in this file:
1.) test_songs_in_database - for a given N and epsilon value, generates N audio snippets of songs in the database, and counts how many are accurately specified and how many are not. We find that the best epsilon is roughly 1e^06 for method one, and 25000 for method five (although method one is MUCH more accurate than method five). We also time this function just to check how quick it runs, in case we ever wished to compare it with slow_search().
2.) test_songs_not_in_database - for a given N and epsilon value, generates N audio snippets of songs NOT in the database. Proceeds similarly as above.


test_freezam.py - Provides unit tests meant to test the core functions of this program.
1.) test_get_window - asserts the results of get_window() are the correct length.
2.) test_get_periodogram - asserts the results of get_periodogram() are the correct length.
3.) test_fingerprint_two - asserts the length of fingerprint_two() are the correct length.
4.) test_return_match - asserts a particular snippet taken directly from a song results in a match from return_match()
5.) test_slow_search - assert three different snippets return the correct results from the slow_search() function.


freezam.py - A program which allows us to run the core of this program from the command line.
This file simply aggregates all the functions previously listed.


## R file

shiny_app.R - Much like freezam.py, this is an overarching program which allows us to run the core of this program, but now with an in interface using the shiny() package. Overall, users are allowed to do 3 things - either upload a snippet for comparison, enter a URL to a WAV or MP3 snippet, or even record their own audio. The program first accepts these inputs, plots the spectrogram of the WAV file associated with the inputted file, and checks it for comparison with the database. If it matches to a song in the database, we then scrape the lyrics (if applicable) of the song from Genius.com.

Note: There are a few examples of this in the "examples" subdirectory - please check it out!


## Directories

scrap - consists of scrap code/files which I may want to return to later
Test_MP3s - consists of mp3s
WAVs - consists of WAVs which comprise my database
snippets - consists of snippets created in 'Audacity' which I initially used to test my program.
Songs_not_in_database - consists of WAVs which I use to test the accuracy of my program.
examples - Example RShiny html pages
temp - temp files that are useful for recording audio/plotting spectrograms


