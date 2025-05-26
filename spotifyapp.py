import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import dateutil.parser as dp

class SpotifyApp(spotipy.Spotify):
    def __init__(
        self, client_id, client_secret, redirect_uri
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.set_auth_manager()
        super().__init__(auth_manager=self.auth_manager)
    
    def set_auth_manager(self):
        scopes = [
            "user-top-read",
            "user-read-recently-played"
            ]
        
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scopes
        )
        
        self.auth_manager = auth_manager

    def format_top_artists(self, limit=20, offset=0, time_range="medium_term"):
        data = self.current_user_top_artists(
            limit=limit,
            offset=offset,
            time_range=self.alias_time_range(time_range)
        )
        
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
    
    def format_top_tracks(self, limit=20, offset=0, time_range="medium_term"):
        data = self.current_user_top_tracks(
            limit=limit,
            offset=offset,
            time_range=self.alias_time_range(time_range)
        )

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
    
    def format_recent(self, limit=20):
        data = self.current_user_recently_played(limit=limit)

        EMOJI = ":musical_note:"
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
                "name": f"{EMOJI} {song_name} - {artists}",
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
    def alias_time_range(range: str):
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
