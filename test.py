from discordapp import DiscordApp

data = {
    "image": "image_url",
    "thumbnail": "thumbnail_url"
}

print(data.get("image", None))

print(DiscordApp.dict_to_embed(data))