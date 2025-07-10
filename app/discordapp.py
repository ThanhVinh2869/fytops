import discord
from app.pagination import Pagination

class DiscordApp():
    def __init__(self, data: dict):
        fields = data.pop("fields", None)
        self._dict = data
        self.fields = fields
        self.embed = discord.Embed()
        self.dict_to_embed()

    def dict_to_embed(self):
        """Convert a Python dictionary to a standard embed message"""
        
        if "author" in self._dict and "name" in self._dict["author"]:
            self.embed.set_author(
                name = self._dict["author"]["name"],
                url = self._dict["author"].get("url", None),
                icon_url = self._dict["author"].get("icon_url", None)
            )
        
        self.embed.color = self._dict.get("color", discord.Color.green())
        self.embed.title = self._dict.get("title", None)
        self.embed.url = self._dict.get("url", None)
        self.embed.description = self._dict.get("description", None)
        self.embed.set_image(url=self._dict.get("image", None))
        self.embed.set_thumbnail(url=self._dict.get("thumbnail", None))
        self.embed.timestamp = self._dict.get("timestamp", None)
        
        self.set_fields()
        
        if "footer" in self._dict:
            if "text" in self._dict["footer"]:
                self.embed.set_footer(text=self._dict["footer"]["text"])
            if "icon_url" in self._dict["footer"]:
                self.embed.set_footer(icon_url=self._dict["footer"]["icon_url"])
                
    def set_fields(self):
        count = min(len(self.fields) - 1, 24) # max 25 fields per embed
        for field in self.fields[0:count]:
            self.embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        
    async def fields_pagination(self, interaction: discord.Interaction, L: int = 10):
        """Apply pagination to fields"""
        
        if not self.fields:
            await interaction.response.send_message(content="You have no records", embed=self.embed)
            
        async def get_page(page: int):
            # Clear current fields
            self.embed.clear_fields()
            
            # Add new fields to embed
            offset = (page-1) * L
            for field in self.fields[offset:offset+L]:
                self.embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
            
            # Set footer to display current page
            n = Pagination.compute_total_pages(len(self.fields), L)
            self.embed.set_footer(text=f"Page {page} of {n}")
            
            return self.embed, n

        await Pagination(interaction, get_page).navigate()