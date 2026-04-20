"""
conftest.py
-----------
Shared pytest fixtures used by both the public and private test suites.
"""

import pytest
from datetime import date, datetime, timedelta, timezone

from streaming.platform import StreamingPlatform
from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import (
    AlbumTrack,
    SingleRelease,
    InterviewEpisode,
    NarrativeEpisode,
    AudiobookTrack,
)
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


# ---------------------------------------------------------------------------
# Helper - timestamps relative to the real current time so that the
# "last 30 days" window in Q2 always contains RECENT sessions.
# ---------------------------------------------------------------------------
FIXED_NOW = datetime.now(timezone.utc).replace(microsecond=0)
RECENT = FIXED_NOW - timedelta(days=10)   # well within 30-day window
OLD    = FIXED_NOW - timedelta(days=60)   # outside 30-day window


@pytest.fixture
def platform() -> StreamingPlatform:
    """Return a fully populated StreamingPlatform instance."""
    platform = StreamingPlatform("TestStream")

    # ------------------------------------------------------------------
    # Artists
    # ------------------------------------------------------------------
    pixels  = Artist("a1", "Pixels",    genre="pop")
    platform.add_artist(pixels)

    lotus_thread = Artist("a2", 'Lotus & Thread', genre="Funk Rock")
    platform.add_artist(lotus_thread)

    false_compass = Artist("a3", 'False Compass', genre="Ambient")
    platform.add_artist(false_compass)

    # ------------------------------------------------------------------
    # Albums & AlbumTracks
    # ------------------------------------------------------------------
    dd = Album("alb1", "Digital Dreams", artist=pixels, release_year=2022)
    t1 = AlbumTrack("t1", "Pixel Rain",      180, "pop",  pixels, track_number=1)
    t2 = AlbumTrack("t2", "Grid Horizon",    210, "pop",  pixels, track_number=2)
    t3 = AlbumTrack("t3", "Vector Fields",   195, "pop",  pixels, track_number=3)

    for track in (t1, t2, t3):
        dd.add_track(track)
        platform.add_track(track)
        pixels.add_track(track)
    platform.add_album(dd)

    reflections_and_riffs = Album("alb2", "Reflections & Riffs", artist=lotus_thread, release_year=2022)
    t = AlbumTrack("t4", "Velvet Transcript", 211, "Funk", lotus_thread, track_number=1)
    reflections_and_riffs.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t5", "Blue Ribbon Static", 217, "Funk", lotus_thread, track_number=2)
    reflections_and_riffs.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t6", "Rust & Neon", 213, "Funk", lotus_thread, track_number=3)
    reflections_and_riffs.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t7", "Lantern Alley", 247, "Funk", lotus_thread, track_number=4)
    reflections_and_riffs.add_track(t)
    platform.add_track(t)

    quiet_signals = Album("alb3", "Quiet Signals", artist=lotus_thread, release_year=2023)
    t = AlbumTrack("t14", "Paper Lanterns", 205, "Progressive Rock", lotus_thread, track_number=1)
    quiet_signals.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t15", "Polaroid Rain", 194, "Progressive Rock", lotus_thread, track_number=2)
    quiet_signals.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t16", "Amber Compass", 199, "Progressive Rock", lotus_thread, track_number=3)
    quiet_signals.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t17", "Venus on Vinyl", 184, "Progressive Rock", lotus_thread, track_number=4)
    quiet_signals.add_track(t)
    platform.add_track(t)

    instant_lights = Album("alb4", "Instant Light", artist=false_compass, release_year=2022)
    t = AlbumTrack("t45", "Clockwork Orchard", 280, "Synthwave", false_compass, track_number=1)
    instant_lights.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t46", "Lanterns Down the Line", 268, "Synthwave", false_compass, track_number=2)
    instant_lights.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t47", "Echo Chamber Waltz", 295, "Synthwave", false_compass, track_number=3)
    instant_lights.add_track(t)
    platform.add_track(t)
    t = AlbumTrack("t48", "Paperweight Heart", 238, "Synthwave", false_compass, track_number=4)
    instant_lights.add_track(t)
    platform.add_track(t)

    careful_hands = Album("alb5", "Careful Hands", artist=false_compass, release_year=2024)
    AlbumTrack("t55", "Neon Boulevard", 252, "Country Pop", false_compass, track_number=1)
    careful_hands.add_track(t)
    platform.add_track(t)
    AlbumTrack("t56", "Saffron Sky", 245, "Country Pop", false_compass, track_number=2)
    careful_hands.add_track(t)
    platform.add_track(t)
    AlbumTrack("t57", "Concrete Garden", 230, "Country Pop", false_compass, track_number=3)
    careful_hands.add_track(t)
    platform.add_track(t)
    AlbumTrack("t58", "Glasshouse Window", 258, "Country Pop", false_compass, track_number=4)
    careful_hands.add_track(t)
    platform.add_track(t)



    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    alice = FreeUser("u1", "Alice",   age=30)
    bob   = PremiumUser("u2", "Bob",   age=25, subscription_start=date(2023, 1, 1))
    john  = PremiumUser("u3", "John",   age=18, subscription_start=date(2023, 2, 2))
    jane  = PremiumUser("u4", "Jane",   age=21, subscription_start=date(2023, 2, 2))

    for user in (alice, bob, john, jane):
        platform.add_user(user)

    # ------------------------------------------------------------------
    # ListeningSessions
    # ------------------------------------------------------------------
    platform.record_session(ListeningSession("s1", alice, dd.tracks[1], RECENT, dd.tracks[1].duration_seconds))
    platform.record_session(ListeningSession("s2", alice, dd.tracks[2], RECENT, dd.tracks[2].duration_seconds))
    platform.record_session(ListeningSession("s3", alice, dd.tracks[1], OLD, dd.tracks[1].duration_seconds))
    platform.record_session(ListeningSession("s4", alice, dd.tracks[2], RECENT, dd.tracks[2].duration_seconds))

    platform.record_session(ListeningSession("s5", bob, careful_hands.tracks[0], RECENT, careful_hands.tracks[0].duration_seconds))
    platform.record_session(ListeningSession("s6", bob, careful_hands.tracks[2], RECENT, careful_hands.tracks[2].duration_seconds))
    platform.record_session(ListeningSession("s7", bob, careful_hands.tracks[3], RECENT, careful_hands.tracks[3].duration_seconds))
    platform.record_session(ListeningSession("s8", bob, instant_lights.tracks[0], OLD, instant_lights.tracks[0].duration_seconds))
    platform.record_session(ListeningSession("s9", bob, instant_lights.tracks[2], RECENT, instant_lights.tracks[2].duration_seconds))

    platform.record_session(ListeningSession("s10", john, instant_lights.tracks[0], RECENT, instant_lights.tracks[0].duration_seconds))
    platform.record_session(ListeningSession("s11", john, instant_lights.tracks[2], RECENT, instant_lights.tracks[2].duration_seconds))
    platform.record_session(ListeningSession("s12", john, reflections_and_riffs.tracks[1], OLD, reflections_and_riffs.tracks[1].duration_seconds))
    platform.record_session(ListeningSession("s13", john, reflections_and_riffs.tracks[1], OLD, reflections_and_riffs.tracks[1].duration_seconds))
    platform.record_session(ListeningSession("s14", john, reflections_and_riffs.tracks[1], RECENT, reflections_and_riffs.tracks[1].duration_seconds))

    # ------------------------------------------------------------------
    # Playlists
    # ------------------------------------------------------------------
    p1 = Playlist(
        "p1",
        "Nice playlist 1",
        bob,
        [
            dd.tracks[0],
            reflections_and_riffs.tracks[0],
            careful_hands.tracks[1],
            reflections_and_riffs.tracks[2],
            instant_lights.tracks[0]
        ]
    )
    p2 = Playlist(
        "p2",
        "this might be some good music",
        bob,
        [
            dd.tracks[0],
            careful_hands.tracks[2],
            reflections_and_riffs.tracks[0],
            reflections_and_riffs.tracks[1],
            reflections_and_riffs.tracks[2],
            reflections_and_riffs.tracks[3],
            instant_lights.tracks[0]
        ]
    )
    p3 = CollaborativePlaylist(
        "p3",
        "songs to eat yoghurt to",
        bob,
        [
            instant_lights.tracks[0],
            careful_hands.tracks[2],
            instant_lights.tracks[2],
            instant_lights.tracks[1],
        ],
        [bob, alice]
    )
    p4 = CollaborativePlaylist(
        "p4",
        "The only one",
        bob,
        [
            reflections_and_riffs.tracks[0],
            instant_lights.tracks[1],
            dd.tracks[0],
            dd.tracks[1],
            dd.tracks[2],
            careful_hands.tracks[2],
        ],
        [john, jane]
    )

    for p in (p1, p2, p3, p4):
        platform.add_playlist(p)

    return platform


@pytest.fixture
def fixed_now() -> datetime:
    """Expose the shared FIXED_NOW constant to tests."""
    return FIXED_NOW


@pytest.fixture
def recent_ts() -> datetime:
    return RECENT


@pytest.fixture
def old_ts() -> datetime:
    return OLD
