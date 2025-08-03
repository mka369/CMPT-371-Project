## Define shared objects (e.g., items, players, etc.)
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Gem:
    id: int
    position: Tuple[int, int] = (300, 250)
    owner_id: Optional[int] = None
    is_collected: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "owner_id": self.owner_id,
            "is_collected": self.is_collected
        }

@dataclass
class Player:
    id: int
    name: str
    score: int = 0
    base: Tuple[int, int, int, int] = (0, 0, 0, 0) # x, y, width, height

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "base": self.base
        }