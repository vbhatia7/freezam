#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 17, 2020
### Use: Adds ability to run this program from the command line
#########################################

import sys
import os
import argparse
import logging

#import my functions
import audio_processing
import database_manager
import spectral_analysis

## NOTE: To run, use: (example queries)
#  python freezam.py slow_search --path="snippets/jarofhearts_snippet.wav" --source="local" --epsilon=50000 --method="five"
#  python freezam.py update_album --title="betty" --new_album="folklore" --artist="Taylor Swift"
#  python freezam.py update_artist --title="betty" --album="folklore" --new_artist="Taylor Swift"
#  python freezam.py list
#  python freezam.py fast_search --path="snippets/jarofhearts_snippet.wav" --source="local" --epsilon=50000 --method="five"
#  python freezam.py recommend --path_to_data="C:/snippets"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info('Started')

parser = argparse.ArgumentParser(description="Function which reads in and matches songs.")
parser.add_argument("-v", "--version", action = "version", version = "Freezam 0.1")

#adding subcommands - add, remove, identify, list
subcommands = parser.add_subparsers(dest="command_name")

#add
parser_add = subcommands.add_parser("add", help = "Adding a song to the database")
parser_add.add_argument("--path", help = "File path to song")
parser_add.add_argument("--title", help = "Title of song")
parser_add.add_argument("--artist", help = "Artist of song")
parser_add.add_argument("--album", help = "Album of song")
parser_add.add_argument("--date", help = "Date of song")
parser_add.add_argument("--source", help = "Local or URL?")

#remove (same syntax as add? -- could update in future)
parser_remove = subcommands.add_parser("remove", help = "Removing a song from the database")
parser_remove.add_argument("--title", help = "Title of song")
parser_remove.add_argument("--artist", help = "Artist of song")
parser_remove.add_argument("--album", help = "Album of song")

# update artist
parser_update_artist = subcommands.add_parser("update_artist", help = "Updating the artist of a particular song")
parser_update_artist.add_argument("--title", help = "Title of song")
parser_update_artist.add_argument("--new_artist", help = "(New) artist of the song")
parser_update_artist.add_argument("--album", help = "Album of song")


# update album
parser_update_album = subcommands.add_parser("update_album", help = "Updating the album of a particular song")
parser_update_album.add_argument("--title", help = "Title of song")
parser_update_album.add_argument("--artist", help = "Artist of song")
parser_update_album.add_argument("--new_album", help = "(New) album of song")

#slowsearch
parser_slow_search = subcommands.add_parser("slow_search", help = "Identify a song!")
parser_slow_search.add_argument("--path", type=str, help = "File path to song")
parser_slow_search.add_argument("--source", type=str, help = "Local or URL?")
parser_slow_search.add_argument("--epsilon", type=float, help = "Tolerance level?")
parser_slow_search.add_argument("--method", help = "Which fingerprint, one or five?")

#fastsearch
parser_slow_search = subcommands.add_parser("fast_search", help = "Identify a song, but quickly! Great if you're in a rush.")
parser_slow_search.add_argument("--path", type=str, help = "File path to song")
parser_slow_search.add_argument("--source", type=str, help = "Local, recording, or URL?")
parser_slow_search.add_argument("--epsilon", type=float, help = "Tolerance level?")
parser_slow_search.add_argument("--method", help = "Which fingerprint, one or five?")


#recommend
parser_slow_search = subcommands.add_parser("recommend", help = "Recommend some songs/artists. Just input a path to a directly")
parser_slow_search.add_argument("--path_to_data", type=str, help = "Path to folder with mp3s/wavs")

#list
parser_list = subcommands.add_parser("list", help = "List all the songs in the database")

results = parser.parse_args()

def main():
    """Function allows all our functions to work from the command line."""
    if results.command_name == "add":
        database_manager.add_function(results.path, results.title, results.artist, results.album, results.date, results.source)
    if results.command_name == "remove":
        database_manager.remove_function(results.title, results.artist, results.album)
    if results.command_name == "update_artist":
        database_manager.update_artist_function(results.title, results.new_artist, results.album)    
    if results.command_name == "update_album":
        database_manager.update_album_function(results.title, results.artist, results.new_album)        
    if results.command_name == "slow_search":
        logger.info('Trying to identify a match...')
        pr_result = database_manager.slow_search(path = results.path, source =  results.source, epsilon = results.epsilon, method = results.method)
        print(pr_result)
    if results.command_name == "fast_search":
        logger.info('Trying to identify a match...')
        pr_result = database_manager.fast_search(path = results.path, source =  results.source, epsilon = results.epsilon, method = results.method)
        print(pr_result)    
    if results.command_name == "list":
        print(database_manager.list_function())
    if results.command_name == "recommend":
        songs,artists = database_manager.recommend(path_to_data = results.path_to_data)
        print("10 Closest Songs:")
        print(songs)
        print("10 Closest Artists:")
        print(artists)

if __name__ == '__main__':
    main()    

