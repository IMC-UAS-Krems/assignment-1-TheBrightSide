"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""

from typing import TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from streaming.tracks import Track


@dataclass
class Artist:
    artist_id: str
    name: str
    genre: str
    tracks: list[Track]

    def add_track(self, track: Track) -> None:
        self.tracks.append(track)

    def track_count(self) -> int:
        return len(self.tracks)
