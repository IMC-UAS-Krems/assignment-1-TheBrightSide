"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from streaming.sessions import ListeningSession
    from streaming.albums import Album
    from streaming.playlists import Playlist
    from streaming.artists import Artist
    from streaming.users import User
    from streaming.tracks import Track


class StreamingPlatform:
    name: str
    _catalogue: dict[str, Track]
    _users: dict[str, User]
    _artists: dict[str, Artist]
    _albums: dict[str, Album]
    _playlists: dict[str, Playlist]
    _sessions: list[ListeningSession]

    def __init__(self, name: str):
        self.name = name        

    def add_track(self, track: Track) -> None:
        self._catalogue[track.track_id] = track

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def add_artist(self, artist: Artist) -> None:
        self._artists[artist.artist_id] = artist

    def add_album(self, album: Album) -> None:
        self._albums[album.album_id] = album

    def add_playlist(self, playlist: Playlist) -> None:
        self._playlists[playlist.playlist_id] = playlist
        
    def record_session(self, session: ListeningSession) -> None:
        self._sessions.append(session)
        
    def get_track(self, track_id: str) -> Track | None:
        return self._catalogue.get(track_id)
        
    def get_user(self, user_id: str) -> User | None:
        return self._users.get(user_id)
        
    def get_artist(self, artist_id: str) -> Artist | None:
        return self._artists.get(artist_id)
        
    def get_album(self, album_id) -> Album | None:
        return self._albums.get(album_id)
        
    def all_users(self) -> list[User]:
        return list(self._users.values())
        
    def all_tracks(self) -> list[Track]:
        return list(self._catalogue.values())

