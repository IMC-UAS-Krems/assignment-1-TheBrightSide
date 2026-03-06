"""
albums.py
---------
Implement the Album class for collections of AlbumTrack objects.

Classes to implement:
  - Album
"""

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from streaming.artists import Artist
    from streaming.tracks import AlbumTrack


@dataclass
class Album:
    album_id: str
    title: str
    artist: Artist
    release_year: int
    tracks: list[AlbumTrack]

    def add_track(self, track: AlbumTrack) -> None:
        self.tracks.append(track)

    def track_ids(self) -> set[str]:
        return set(map(lambda x: x.track_id, self.tracks))

    def duration_seconds(self) -> int:
        return sum(map(lambda x: x.duration_seconds, self.tracks))
