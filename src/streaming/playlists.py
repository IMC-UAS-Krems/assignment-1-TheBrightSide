"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""

from typing import TYPE_CHECKING

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from streaming.tracks import Track
    from streaming.users import User


@dataclass
class Playlist:
    playlist_id: str
    name: str
    owner: User
    tracks: list[Track] = field(default_factory=list)

    def add_track(self, track: Track) -> None:
        if track in self.tracks:
            return

        self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        self.tracks = list(filter(lambda x: x.track_id != track_id, self.tracks))

    def total_duration_seconds(self) -> int:
        return sum(map(lambda x: x.duration_seconds, self.tracks))


@dataclass
class CollaborativePlaylist(Playlist):
    contributors: list[User] = field(default_factory=list)

    def __post_init__(self):
        if self.owner in self.contributors:
            return

        self.contributors.insert(0, self.owner)

    def add_contributor(self, user: User) -> None:
        if user in self.contributors:
            return

        self.contributors.append(user)

    def remove_contributor(self, user: User) -> None:
        if user is self.owner:
            return

        self.contributors = list(
            filter(lambda x: x.user_id != user.user_id, self.contributors)
        )
