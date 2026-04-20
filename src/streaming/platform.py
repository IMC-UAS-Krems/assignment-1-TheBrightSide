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
from functools import reduce

from typing import TYPE_CHECKING, TypeGuard, cast


if TYPE_CHECKING:
    from streaming.sessions import ListeningSession
    from streaming.albums import Album
    from streaming.playlists import Playlist
    from streaming.artists import Artist
    from streaming.users import User
    from streaming.tracks import Track


class StreamingPlatform:

    def __init__(self, name: str):
        self.name: str = name
        self._catalogue: dict[str, Track] = {}
        self._users: dict[str, User] = {}
        self._artists: dict[str, Artist] = {}
        self._albums: dict[str, Album] = {}
        self._playlists: dict[str, Playlist] = {}
        self._sessions: list[ListeningSession] = []

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
                and (now - x.timestamp) < timedelta(days=days)
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

        return float(mean(grouped_distinct_count))

    def track_with_most_distinct_listeners(self) -> Track | None:
        if len(self._sessions) == 0:
            return None

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

        return self._catalogue[max(grouped_distinct_users_count, key=lambda x: x[1])[0]]

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
                lambda x: (x[0], mean(map(lambda y: y.duration_listened_seconds, x[1]))),
                grouped_by_user_class,
            )
        )

    def total_listening_time_underage_sub_users_minutes(
        self, age_threshold: int = 18
    ) -> float:
        # TODO: might be incorrect
        return sum(
            map(
                lambda x: x.duration_listened_minutes(),
                filter(
                    lambda x: (
                        isinstance(x.user, FamilyMember) and x.user.age < age_threshold
                    ),
                    self._sessions,
                ),
            ),
            start=0.
        )

    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        def is_tuple_int_song(x: tuple[int, Track]) -> TypeGuard[tuple[int, Song]]:
            return isinstance(x[0], int) and isinstance(x[1], Song)
        song_sessions = filter(is_tuple_int_song, map(lambda x: (x.duration_listened_seconds, x.track), self._sessions))
        artist_song_sessions = [
            (x, list(y))
            for x, y in groupby(
                sorted(song_sessions, key=lambda x: x[1].artist.artist_id),
                key=lambda x: x[1].artist.artist_id,
            )
        ]
        artists_listened_duration = map(
            lambda x: (self._artists[x[0]], sum(map(lambda y: y[0], x[1])) / 60),
            artist_song_sessions,
        )

        return list(islice(sorted(artists_listened_duration, key=lambda x: x[1], reverse=True), n))

    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user_sessions = filter(lambda x: x.user.user_id == user_id, self._sessions)
        sessions_by_genre = [
            (x, list(y))
            for x, y in groupby(
                sorted(user_sessions, key=lambda x: x.track.genre),
                key=lambda x: x.track.genre,
            )
        ]

        sessions_amount = sum(map(lambda x: len(x[1]), sessions_by_genre))

        return next(
            iter(
                sorted(
                    map(
                        lambda x: (
                            x[0],
                            (len(x[1]) / sessions_amount) * 100.,
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
        def is_song(x: Track) -> TypeGuard[Song]:
            return isinstance(x, Song)

        def is_collaborative_playlist(x: Playlist) -> TypeGuard[CollaborativePlaylist]:
            return isinstance(x, CollaborativePlaylist)

        return list(
            filter(
                lambda x: (
                    len(
                        set(
                            map(
                                lambda y: y.artist.artist_id,
                                filter(is_song, x.tracks),
                            )
                        )
                    )
                    > threshold
                ),
                filter(is_collaborative_playlist, self._playlists.values()),
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
        def is_album_track(x: Track) -> TypeGuard[AlbumTrack]:
            return isinstance(x, AlbumTrack)

        album_id_tracks = reduce(
            lambda x, y: (
                x + [((y.album.album_id, y.album.title), y)]
                if is_album_track(y) and y.album is not None
                else x
            ),
            self._catalogue.values(),
            cast(list[tuple[tuple[str, str], AlbumTrack]], []),
        )

        tracks_grouped_by_albums = (
            (x[0][1], set(map(lambda x: x[1].track_id, y)))
            for x, y in groupby(
                sorted(album_id_tracks, key=lambda x: x[0]),
                key=lambda x: x[0]
            )
        )

        sessions_grouped_by_users = (
            (x, set(map(lambda x: x.track.track_id, y)))
            for x, y in groupby(
                sorted(self._sessions, key=lambda x: x.user.user_id),
                key=lambda x: x.user.user_id
            )
        )

        return [
            (self._users[user_sessions[0]], [
                album_tracks[0]
                for album_tracks in tracks_grouped_by_albums
                if (album_tracks[1] - user_sessions[1]) == set()
            ])
            for user_sessions in sessions_grouped_by_users
        ]

