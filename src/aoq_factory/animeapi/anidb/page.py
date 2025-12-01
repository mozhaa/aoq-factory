from typing import Self

from pyquery import PyQuery as pq

from aoq_factory.database.models import Category, Song

from .tools import get_page


class Page:
    def __init__(self, html: str, anidb_id: int) -> None:
        self.page = pq(html)
        self.anidb_id = anidb_id

    @classmethod
    async def from_id(cls, anidb_id: int) -> Self:
        return cls(await get_page(anidb_id), anidb_id)

    @property
    def qitems(self) -> list[Song]:
        songs = []
        counters = {}
        anidb_ids = set()
        for song in self.page("table#songlist > tbody td.name.song"):
            song = pq(song)
            anidb_id = int(song("a").eq(0).attr("href").split("/")[-1])
            if anidb_id in anidb_ids:
                continue
            category = (
                song.parent()
                .prev_all()
                .children()
                .extend(song.prev_all())
                .filter(".reltype")
                .eq(-1)
                .text()
                .strip()
                .lower()
            )
            if category == "opening":
                category = Category.OP
            elif category == "ending":
                category = Category.ED
            else:
                break
            number = counters[category] = counters.get(category, 0) + 1
            name = song.text().strip()
            name = name if name != "" else None
            try:
                artist = song.next_all("td.name.creator").text().strip()
            except Exception:
                artist = None
            anidb_ids.add(anidb_id)
            songs.append(
                Song(
                    anime_id=self.anidb_id,
                    category=category,
                    number=number,
                    song_name=name,
                    song_artist=artist,
                )
            )
        return songs
