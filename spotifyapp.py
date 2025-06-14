from spotipy import Spotify 
from spotipy.oauth2 import SpotifyOAuth
import json
import dateutil.parser as dp

class SpotifyAppOAuth(SpotifyOAuth):
    def __init__(self, user_id: int, client_id, client_secret, redirect_uri):
        cache_path = self.get_user_cache_path(user_id)
        
        scopes = [
            "user-top-read",
            "user-read-recently-played"
            ]
        
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scopes,
            cache_path=cache_path,
        )
        
    @staticmethod
    def get_user_cache_path(user_id):
        return f"user_tokens/{user_id}.cache"
        
class SpotifyApp(Spotify):
    def spotify_user_info(self):
        null_image = "https://media.discordapp.net/attachments/1374160501877248113/1377302749628076062/null_avatar.png?ex=683878a4&is=68372724&hm=91a9d8e64bcdd49ae6a57b5684bd8ea47c84d910b5e961ba08a6c6eecd7b80f7&=&format=webp&quality=lossless&width=1260&height=1260"
        
        user = self.me()
        username = user["display_name"]
        user_url = user["external_urls"]["spotify"]
        user_image = null_image if not user["images"] else user["images"][0]["url"]
        
        description = f"[{username}]({user_url}) on Spotify"
        
        return description, user_image

    def format_top_artists(self, limit=20, offset=0, time_range="medium_term"):
        # Get current user info
        description, user_image = self.spotify_user_info()
        
        # Set embed attributes
        formatted = {
            "color": 0x07e380,
            "title": f"Top Artists",
            "description": description,
            "thumbnail": user_image,
            "fields": []
        }
        
        # Set embed fields
        data = self.current_user_top_artists(
            limit=limit,
            offset=offset,
            time_range=self.alias_time_range(time_range)
        )

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
        # Get current user info
        description, user_image = self.spotify_user_info()

        # Set embed attributes
        formatted = {
            "color": 0x07e380,
            "title": f"Top Tracks",
            "description": description,
            "thumbnail": user_image,
            "fields": []
        }   
     
        # Set embed fields
        data = self.current_user_top_tracks(
            limit=limit,
            offset=offset,
            time_range=self.alias_time_range(time_range)
        )

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
        # Get current user info
        description, user_image = self.spotify_user_info()
        
        # Set embed attributes
        formatted = {
            "color": 0x07e380,
            "title": f"Recently Played Tracks",
            "description": description,
            "thumbnail": user_image,
            "fields": []
        }   

        EMOJI = ":musical_note:"
        data = self.current_user_recently_played(limit=limit)
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
