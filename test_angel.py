import asyncio
from yline.tools.lyrics import fetch_synced_lyrics
from yline.tools.music_search import search_music

async def test():
    meta = await search_music("you are an angel kate said")
    print(meta)
    
    lyrics = await fetch_synced_lyrics("kate said", "you are an angel")
    print(len(lyrics) if lyrics else "No lyrics found")

asyncio.run(test())
