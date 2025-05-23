import discord

class DiscordApp():
    @staticmethod
    def dict_to_embed(data: dict):
        embed = discord.Embed()

        if "author" in data:
            if "name" in data["author"]:
                embed.set_author(name=data["author"]["name"])
                embed.set_author(url = data["author"].get("url", None))
                embed.set_author(icon_url = data["author"].get("icon_url", None))
        
        embed.color = data.get("color", discord.Color.green())
        embed.title = data.get("title", None)
        embed.url = data.get("url", None)
        embed.description = data.get("description", None)
        embed.set_image(data.get("image", None))
        embed.set_thumbnail(data.get("thumbnail", None))
        embed.timestamp = data.get("timestamp", None)

        if "footer" in data:
            if "text" in data["footer"]:
                embed.set_footer(text=data["footer"]["text"])
            if "icon_url" in data["footer"]:
                embed.set_footer(icon_url=data["footer"]["icon_url"])
        
        if "fields" in data:
            try:
                DiscordApp.embed_field(embed, data["fields"])
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
            embed.add_field(name, value, inline)