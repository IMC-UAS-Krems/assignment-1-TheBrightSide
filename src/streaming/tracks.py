"""
tracks.py
---------
Implement the class hierarchy for all playable content on the platform.

Classes to implement:
  - Track (abstract base class)
    - Song
      - SingleRelease
      - AlbumTrack
    - Podcast
      - InterviewEpisode
      - NarrativeEpisode
    - AudiobookTrack
"""

from typing import TYPE_CHECKING


from dataclasses import dataclass

if TYPE_CHECKING:
    from streaming.albums import Artist, Album
    from datetime import date


@dataclass
class Track:
    track_id: str
    title: str
    duration_seconds: int
    genre: str

    def duration_minutes(self) -> float:
        return self.duration_seconds / 60


@dataclass
class Song(Track):
    artist: Artist


@dataclass
class SingleRelease(Song):
    release_date: date


@dataclass
class AlbumTrack(Song):
    track_number: int
    album: Album | None


@dataclass
class Podcast(Track):
    host: str
    description: str


@dataclass
class InterviewEpisode(Podcast):
    guest: str


@dataclass
class NarrativeEpisode(Podcast):
    season: int
    episode_number: int


@dataclass
class AudiobookTrack(Track):
    author: str
    narrator: str
