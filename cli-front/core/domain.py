# core/domain.py
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AnyVote:
    tokenID: str
    encryptedVotes: List[str]  # hex / bytetree serializado
    metadata: Dict[str, Any]
