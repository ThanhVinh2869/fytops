import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import dateutil.parser as dp
            
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
        self, oauth_manager=None
    ):
        self.oauth_manager = oauth_manager
        self.sp_object = spotipy.Spotify(auth_manager=self.oauth_manager)
    
    def get_user_top_artists(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        try:
            time_range = self.standardize_time_range(time_range)
        except ValueError:
            print("Invalid term")
            return None
        
        return self.sp_object.current_user_top_artists(
            limit=limit, offset=offset, time_range=time_range
        )
    
    def get_user_top_tracks(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        try:
            time_range = self.standardize_time_range(time_range)
        except ValueError:
            print("Invalid term")
            return None
        
        return self.sp_object.current_user_top_tracks(
            limit=limit, offset=offset, time_range=time_range
        )
        
    def get_user_recently_played(
        self, limit=20
    ):
        return self.sp_object.current_user_recently_played(limit=limit)
    
    @staticmethod
    def format_top_artists(data: dict):
        formatted = {
            "color": 0x07e380,
            "title": f"Top Artists",
            "fields": []
        }

        for rank, item in enumerate(data["items"], 1):
            name = item["name"]
            url = item["external_urls"]["spotify"]
            followers = item["followers"]["total"]
            
            # Format field
            field = {
                "name": f"{SpotifyApp.rank_emojify(rank)} {name}",
                "value": f"[page]({url}) - {followers} followers",
                "inline": False
            }      

            formatted["fields"].append(field)
            
        return formatted
    
    @staticmethod
    def format_top_tracks(data: dict):
        formatted = {
            "color": 0x07e380,
            "title": f"Top Tracks",
            "fields": []
        }

        for rank, item in enumerate(data["items"], 1):
            album_name = item["album"]["name"]
            album_url = item["external_urls"]["spotify"]
            
            artists = ", ".join([artist["name"] for artist in item["artists"]])
            
            song_name = item["name"]
            song_url = item["external_urls"]["spotify"]
            
            # Format field
            field = {
                "name": f"{SpotifyApp.rank_emojify(rank)} {song_name} - {artists}",
                "value": f"[page]({song_url}) - from album [{album_name}]({album_url})",
                "inline": False
            }
            
            formatted["fields"].append(field)

        return formatted
    
    @staticmethod
    def format_recent(data: dict):
        formatted = {
            "color": 0x07e380,
            "title": f"Recent played Tracks",
            "fields": []
        }

        for item in data["items"]:
            song_name = item["track"]["name"]
            song_url = item["track"]["external_urls"]["spotify"]
            
            iso_time = item["played_at"]
            unix_time = round(SpotifyApp.iso_to_unix(iso_time))
            
            artists = ", ".join([artist["name"] for artist in item["track"]["artists"]])

            field = {
                "name": f"{song_name} - {artists}",
                "value": f"Played <t:{unix_time}:R> (<t:{unix_time}:f>) - [url]({song_url})",
                "inline": False
            }
            
            formatted["fields"].append(field)
        
        return formatted
    
    @staticmethod
    def rank_emojify(rank: int):
        if rank == 1:
            return ":first_place:"
        elif rank == 2:
            return ":second_place:"
        elif rank == 3:
            return ":third_place:"
        else:
            return f"{rank}."
    
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
    
    @staticmethod
    def iso_to_unix(time):
        return dp.parse(time).timestamp()
    
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
