from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, BOT_TOKEN

from spotifyapp import SpotifyApp, SpotifyAppOAuth

import discord
from fytops import FyTops

# Request token
token = SpotifyAppOAuth().generate_auth_manager(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

# Perform requests
# current_object = SpotifyApp(token)
# top_artists = current_object.get_user_top_artists()
# top_tracks = current_object.get_user_top_tracks()
# recently_played = current_object.get_user_recently_played()

# Convert to JSON
# SpotifyApp.dict_to_json(top_artists, "top_artists.json")
# SpotifyApp.dict_to_json(top_tracks, "top_tracks.json")
# SpotifyApp.dict_to_json(recently_played, "recently_played.json")

fytops = FyTops()

fytops.run(BOT_TOKEN)