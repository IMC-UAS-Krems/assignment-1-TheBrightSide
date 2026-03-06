"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""

from typing import TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from streaming.tracks import Track
    from streaming.users import User


@dataclass
class Playlist:
    playlist_id: str
    name: str
    owner: User
    tracks: list[Track]

    def add_track(self, track: Track) -> None:
        self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        self.tracks = list(filter(lambda x: x.track_id != track_id, self.tracks))

    def total_duration_seconds(self) -> int:
        return sum(map(lambda x: x.duration_seconds, self.tracks))


@dataclass
class CollaborativePlaylist:
    contributors: list[User]

    def add_contributor(self, user: User) -> None:
        self.contributors.append(user)

    def remove_contributor(self, user: User) -> None:
        self.contributors = list(
            filter(lambda x: x.user_id != user.user_id, self.contributors)
        )
