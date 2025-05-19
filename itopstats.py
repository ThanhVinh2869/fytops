import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
            
class ItopStatsOAuth:
    @staticmethod
    def generate_token(
        client_id=None, client_secret=None, redirect_uri='http://127.0.0.1:3000'
    ):
        scopes = [
            "user-top-read",
            "user-read-recently-played"
            ]
        
        token = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scopes
        )
        
        return token
        
        # TODO: token validation (time < 60 minutes)
        # TODO: catch error

class ItopStats:
    def __init__(
        self, token=None
    ):
        self.oauth_token = token
        self.sp_object = spotipy.Spotify(auth_manager=self.oauth_token)
    
    def get_user_top_artists(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        top_artists = self.sp_object.current_user_top_artists()
        return top_artists
    
    def get_user_top_tracks(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        top_tracks = self.sp_object.current_user_top_tracks()
        return top_tracks
        
    def get_user_recently_played(
        self, limit=50
    ):
        recently_played = self.sp_object.current_user_recently_played()
        return recently_played
    
    @staticmethod
    def dict_to_json(
        data, filename
    ):
        """Writes a Python dictionary to a JSON file.
        
        Args:
            data (dict): The dictionary to write.
            filename (str): The name of the file to write to.
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
