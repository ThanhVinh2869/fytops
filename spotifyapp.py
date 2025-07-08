from spotipy import Spotify 
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO
from colorthief import ColorThief
from discord import Color
import json
import dateutil.parser as dp
from datetime import datetime 

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
    def __init__(self, auth_manager):
        super().__init__(auth_manager=auth_manager)
        self.user_info = {}
        self.__set_spotify_user_info()

    def __set_spotify_user_info(self):
        user = self.me()
        
        # Compute embed description
        username = user["display_name"]
        user_url = user["external_urls"]["spotify"]
        now = datetime.now().isoformat()
        now = self.iso_to_unix(now)
        description = f"[{username}]({user_url}) on Spotify\nData generated on <t:{now}:f>\n\u200b"

        # Get user profile picture
        null_image = "https://media.discordapp.net/attachments/1374160501877248113/1377302749628076062/null_avatar.png?ex=683878a4&is=68372724&hm=91a9d8e64bcdd49ae6a57b5684bd8ea47c84d910b5e961ba08a6c6eecd7b80f7&=&format=webp&quality=lossless&width=1260&height=1260"
        user_image = null_image if not user["images"] else user["images"][0]["url"]
        
        # Get dominant color in user profile picture
        response = requests.get(user_image)
        response.raise_for_status()
        
        image = BytesIO(response.content)
        
        color_thief = ColorThief(image)
        r, g, b = color_thief.get_color(quality=5)
        
        # Compute user attributes and update
        attributes = {
            "description": description, 
            "thumbnail": user_image, 
            "color": Color.from_rgb(r, g, b)
        }
        
        self.user_info.update(attributes)

    def format_top_artists(self, limit=20, offset=0, time_range="medium_term"):
        time_range = self.alias_time_range(time_range)
        
        # Set embed attributes
        artists = {
            "title": self.time_range_definition("Top Artists", time_range),
            "fields": []
        }   
        
        # Request data using API call
        data = self.current_user_top_artists(limit=limit, offset=offset, time_range=time_range)

        # Reformat the raw data
        for rank, item in enumerate(data["items"], 1):
            name = item["name"]
            url = item["external_urls"]["spotify"]
            followers = item["followers"]["total"]
            
            # Format individual fields
            field = {
                "name": f"{self.rank_emojify(rank)} {name}",
                "value": f"[Artist on Spotify]({url}) with {followers:,} followers",
                "inline": False
            }      

            artists["fields"].append(field)
            
        return self.user_info | artists
    
    def format_top_tracks(self, limit=20, offset=0, time_range="medium_term"):
        time_range=self.alias_time_range(time_range)
        
        # Set embed attributes
        tracks = {
            "title": self.time_range_definition("Top Tracks", time_range),
            "fields": []
        }   
     
        # Request data using API call
        data = self.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)
        
        # Reformat the raw data
        for rank, item in enumerate(data["items"], 1):
            album_name = item["album"]["name"]
            album_url = item["external_urls"]["spotify"]
            
            artists = ", ".join([artist["name"] for artist in item["artists"]])
            
            song_name = item["name"]
            song_url = item["external_urls"]["spotify"]
            
            # Format individual fields
            field = {
                "name": f"{self.rank_emojify(rank)} {song_name} - {artists}",
                "value": f"[Track on Spotify]({song_url}) from album [{album_name}]({album_url})",
                "inline": False
            }
            
            tracks["fields"].append(field)

        return self.user_info | tracks
    
    def format_recent(self, limit=20):
        EMOJI = ":musical_notes:"
        
        # Set embed attributes
        recent = { 
            "title": self.time_range_definition("Recently played Tracks"),
            "fields": []
        }   

        # Request data using API call
        data = self.current_user_recently_played(limit=limit)
        
        # Reformat the raw data
        for item in data["items"]:
            song_name = item["track"]["name"]
            song_url = item["track"]["external_urls"]["spotify"]
            
            iso_time = item["played_at"]
            unix_time = self.iso_to_unix(iso_time)
            
            artists = ", ".join([artist["name"] for artist in item["track"]["artists"]])

            # Format individual fields
            field = {
                "name": f"{EMOJI} {song_name} - {artists}",
                "value": f"[Track on Spotify]({song_url})\nPlayed <t:{unix_time}:R> (<t:{unix_time}:f>)",
                "inline": False
            }
            
            recent["fields"].append(field)
        
        return self.user_info | recent
    
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
        if range in ["s", "short", "small_term", "30", "4", "1"]:
            return "short_term"
        
        elif range in ["l", "long", "long_term", "365", "52", "12"]:
            return "long_term"
        
        else:
            return "medium_term"
    
    @staticmethod
    def time_range_definition(data: str, range: str=None):
        range_mapping = {
            "short_term": "30 days",
            "medium_term": "6 months",
            "long_term": "12 months"
        }
        
        if not range:
            string = f"Your **{data}**"
        else:
            string = f"Your **{data}** in the last  `{range_mapping[range]}`"
        
        return string
    
    @staticmethod
    def iso_to_unix(time):
        return round(dp.parse(time).timestamp())
    
    @staticmethod
    def dict_to_json(data, filename):
        """Writes a Python dictionary to a JSON file.
        
        Args:
            data (dict): The dictionary to write.
            filename (str): The name of the file to write to.
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
