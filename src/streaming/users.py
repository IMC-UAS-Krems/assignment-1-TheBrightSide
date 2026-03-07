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
        return set(map(lambda x: x.track.track_id, self.sessions))


@dataclass
class FamilyMember(User):
    parent: FamilyAccountUser


@dataclass
class FamilyAccountUser(User):
    sub_users: list[FamilyMember] = field(default_factory=list)

    def all_members(self) -> list[User]:
        return [self, *self.sub_users]

    def add_sub_user(self, member: FamilyMember) -> None:
        self.sub_users.append(member)


@dataclass
class FreeUser(User):
    MAX_SKIPS_PER_HOUR: int = 6


@dataclass
class PremiumUser(User):
    subscription_start: date
