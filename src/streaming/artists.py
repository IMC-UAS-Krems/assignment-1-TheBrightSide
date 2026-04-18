"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from streaming.tracks import Track


@dataclass
class Artist:
    artist_id: str
    name: str
    genre: str
    tracks: list[Track] = field(default_factory=list)

    def add_track(self, track: Track) -> None:
        self.tracks.append(track)

    def track_count(self) -> int:
        return len(self.tracks)
