from anime_utils.clients.anidb.types import AniDBSong

from aoq_factory.database.models import Category, Song


def anidb_song_to_song(anidb_song: AniDBSong) -> Song:
    song = Song()

    category = anidb_song["category"].lower()
    if "op" in category:
        song.category = Category.OP
    elif "ed" in category:
        song.category = Category.ED
    else:
        raise ValueError(f"invalid category: {category}")

    song.number = anidb_song["number"]
    song.song_name = anidb_song["song_name"]

    if (song_artist := anidb_song["staff"].get("Vocals/Performed by (歌)", None)) is not None:
        song.song_artist = song_artist

    return song
