import discord

class DiscordApp():
    def __init__(self, data: dict):
        self._dict = data
        self.embed = discord.Embed()
        self.dict_to_embed()

    def dict_to_embed(self):
        if "author" in self._dict:
            if "name" in self._dict["author"]:
                self.embed.set_author(name=self._dict["author"]["name"])
                self.embed.set_author(url = self._dict["author"].get("url", None))
                self.embed.set_author(icon_url = self._dict["author"].get("icon_url", None))
        
        self.embed.color = self._dict.get("color", discord.Color.green())
        self.embed.title = self._dict.get("title", None)
        self.embed.url = self._dict.get("url", None)
        self.embed.description = self._dict.get("description", None)
        self.embed.set_image(url=self._dict.get("image", None))
        self.embed.set_thumbnail(url=self._dict.get("thumbnail", None))
        self.embed.timestamp = self._dict.get("timestamp", None)

        if "footer" in self._dict:
            if "text" in self._dict["footer"]:
                self.embed.set_footer(text=self._dict["footer"]["text"])
            if "icon_url" in self._dict["footer"]:
                self.embed.set_footer(icon_url=self._dict["footer"]["icon_url"])
        
        if "fields" in self._dict:
            try:
                DiscordApp.embed_fields(self.embed, self._dict["fields"])
            except ValueError:
                print("Only 25 fields allowed per embed!")

    @staticmethod
    def embed_fields(embed: discord.Embed, fields: list):
        # Max 25 fields
        if len(fields) > 25:
            raise ValueError
        
        for field in fields:
            name = field.get("name", None)
            value = field.get("value", None)
            inline = field.get("inline", None)
            embed.add_field(name=name, value=value, inline=inline)