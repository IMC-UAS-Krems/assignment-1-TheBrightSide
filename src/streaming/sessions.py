"""
sessions.py
-----------
Implement the ListeningSession class for recording listening events.

Classes to implement:
  - ListeningSession
"""

from typing import TYPE_CHECKING


from dataclasses import dataclass

if TYPE_CHECKING:
    from datetime import datetime
    from streaming.tracks import Track
    from streaming.users import User


@dataclass
class ListeningSession:
    session_id: str
    user: User
    track: Track
    timestamp: datetime
    duration_listened_seconds: int

    def duration_listened_minutes(self) -> float:
        return self.duration_listened_seconds / 60
