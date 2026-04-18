"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""

from __future__ import annotations
from streaming.tracks import Song, AlbumTrack
from streaming.users import PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import CollaborativePlaylist

from statistics import mean
from datetime import datetime, timezone, timedelta
from itertools import groupby, islice

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
    _catalogue: dict[str, Track] = {}
    _users: dict[str, User] = {}
    _artists: dict[str, Artist] = {}
    _albums: dict[str, Album] = {}
    _playlists: dict[str, Playlist] = {}
    _sessions: list[ListeningSession] = []

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
        if session.user.user_id in self._users.values():
            self._users[session.user.user_id].add_session(session)

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

    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        return (
            sum(
                map(
                    lambda x: x.duration_listened_seconds,
                    filter(
                        lambda x: x.timestamp >= start and x.timestamp <= end,
                        self._sessions,
                    ),
                ),
                start=0.0,
            )
            / 60
        )

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        now = datetime.now(timezone.utc)
        last_premium_sessions = filter(
            lambda x: (
                isinstance(x.user, PremiumUser)
                and (now - x.timestamp) > timedelta(days=days)
            ),
            self._sessions,
        )

        grouped_by_user_sessions = [
            list(x)
            for _, x in groupby(
                sorted(last_premium_sessions, key=lambda x: x.user.user_id),
                key=lambda x: x.user.user_id,
            )
        ]

        if len(grouped_by_user_sessions) == 0:
            return 0.0

        grouped_distinct_count = [
            len(set(map(lambda x: x.track.track_id, x)))
            for x in grouped_by_user_sessions
        ]

        return mean(grouped_distinct_count)

    def track_with_most_distinct_listeners(self) -> Track | None:
        grouped_by_tracks_sessions = [
            (x, list(y))
            for x, y in groupby(
                sorted(self._sessions, key=lambda x: x.track.track_id),
                key=lambda x: x.track.track_id,
            )
        ]

        grouped_distinct_users_count = [
            (x, len(set(map(lambda y: y.user.user_id, y))))
            for x, y in grouped_by_tracks_sessions
        ]

        return max(grouped_distinct_users_count, key=lambda x: x[1])[0]

    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        grouped_by_user_class = [
            (x, list(y))
            for x, y in groupby(
                sorted(self._sessions, key=lambda x: x.__class__.__name__),
                key=lambda x: x.__class__.__name__,
            )
        ]

        return list(
            map(
                lambda x: (x[0], mean(map(lambda y: y.duration_seconds, x[1]))),
                grouped_by_user_class,
            )
        )

    def total_listening_time_underage_sub_users_minutes(
        self, age_threshold: int = 18
    ) -> float:
        # TODO: might be incorrect
        return sum(
            map(
                lambda x: x.duration_listened_seconds,
                filter(
                    lambda x: (
                        isinstance(x.user, FamilyMember) and x.user.age < age_threshold
                    ),
                    self._sessions,
                ),
            )
        )

    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        song_sessions = filter(lambda x: isinstance(x.track, Song), self._sessions)
        artist_song_sessions = [
            (x, list(y))
            for x, y in groupby(
                sorted(song_sessions, key=lambda x: x.artist.artist_id),
                key=lambda x: x.artist.artist_id,
            )
        ]
        artists_listened_duration = map(
            lambda x: (x[0], sum(map(lambda y: y.duration_listened_seconds, x[1]))),
            artist_song_sessions,
        )

        return list(islice(sorted(artists_listened_duration, key=lambda x: x[1]), n))

    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user_sessions = filter(lambda x: x.user.user_id == user_id, self._sessions)
        sessions_by_genre = [
            (x, list(y))
            for x, y in groupby(
                sorted(user_sessions, key=lambda x: x.track.genre),
                key=lambda x: x.track.genre,
            )
        ]

        return next(
            iter(
                sorted(
                    map(
                        lambda x: (
                            x[0],
                            sum(map(lambda y: y.duration_listened_seconds, x[1])),
                        ),
                        sessions_by_genre,
                    ),
                    key=lambda x: x[1],
                )
            ),
            None,
        )

    def collaborative_playlists_with_many_artists(
        self, threshold: int = 3
    ) -> list[CollaborativePlaylist]:
        return list(
            filter(
                lambda x: (
                    isinstance(x, CollaborativePlaylist)
                    and len(
                        set(
                            map(
                                lambda y: y.artist.artist_id,
                                filter(lambda y: isinstance(y, Song), x.tracks),
                            )
                        )
                    )
                    > threshold
                ),
                list(self._playlists.values()),
            )
        )

    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        grouped_by_playlist_class = [
            (x, list(y))
            for x, y in groupby(
                sorted(self._playlists.values(), key=lambda x: x.__class__.__name__),
                key=lambda x: x.__class__.__name__,
            )
        ]

        return {
            k: mean(map(lambda x: len(x.tracks), v))
            for k, v in grouped_by_playlist_class
        }

    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        # out = {}
        # for user in self._users.values():
        #     filter(lambda x: isinstance(x.track, AlbumTrack), user.sessions)
        
        raise NotImplementedError()
