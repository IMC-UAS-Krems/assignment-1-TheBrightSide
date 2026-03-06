"""
users.py
--------
Implement the class hierarchy for platform users.

Classes to implement:
  - User (base class)
    - FreeUser
    - PremiumUser
    - FamilyAccountUser
    - FamilyMember
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from datetime import date
    from streaming.sessions import ListeningSession


@dataclass
class User:
    user_id: str
    name: str
    age: int
    sessions: list[ListeningSession] = field(default_factory=list, kw_only=True)

    def add_session(self, session: ListeningSession) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(map(lambda x: x.duration_listened_seconds, self.sessions))

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self) -> set[str]:
        return set(map(lambda x: x.track, self.sessions))


@dataclass
class FamilyMember:
    parent: FamilyAccountUser


@dataclass
class FamilyAccountUser:
    sub_users: list[FamilyMember]


@dataclass
class FreeUser(User):
    MAX_SKIPS_PER_HOUR: int = 6


@dataclass
class PremiumUser(User):
    subscription_start: date
