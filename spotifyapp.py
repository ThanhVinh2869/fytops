import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
            
class SpotifyAppOAuth:
    @staticmethod
    def generate_auth_manager(
        client_id, client_secret, redirect_uri
    ):
        scopes = [
            "user-top-read",
            "user-read-recently-played"
            ]
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scopes
        )
        
        return auth_manager
        
        # TODO: catch error

class SpotifyApp:
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
    
    @staticmethod
    def standardize_time_range(range: str):
        if not range:
            raise ValueError
        
        if range in ["s", "small", "small_term"]:
            return "small_term"

        elif range in ["m", "medium", "medium_term"]:
            return "medium_term"

        elif range in ["l", "long", "long_term"]:
            return "long_term"
        
        else:
            raise ValueError
    
    
        
