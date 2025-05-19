from dotenv import load_dotenv
import os
from itopstats import ItopStats, ItopStatsOAuth

# Load credential information
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://127.0.0.1:3000'

# Request token
token = ItopStatsOAuth().generate_token(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

# Perform requests
current_object = ItopStats(token)
top_artists = current_object.get_user_top_artists()
top_tracks = current_object.get_user_top_tracks()
recently_played = current_object.get_user_recently_played()

# Convert to JSON
ItopStats.dict_to_json(top_artists, "top_artists.json")
ItopStats.dict_to_json(top_tracks, "top_tracks.json")
ItopStats.dict_to_json(recently_played, "recently_played.json")