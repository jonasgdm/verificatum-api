from typing import Protocol


class EncryptPort(Protocol):
    def encrypt(self, value: str) -> str: ...
