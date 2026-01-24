"""JavaCard Application Identifier (AID) handling."""

from dataclasses import dataclass
from typing import Self


class AIDError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AID:
    """JavaCard Application Identifier (5-16 bytes)."""

    _bytes: bytes

    MIN_LENGTH = 5
    MAX_LENGTH = 16

    def __post_init__(self) -> None:
        if not (self.MIN_LENGTH <= len(self._bytes) <= self.MAX_LENGTH):
            raise AIDError(f"AID must be {self.MIN_LENGTH}-{self.MAX_LENGTH} bytes, got {len(self._bytes)}")

    @classmethod
    def from_hex(cls, hex_string: str) -> Self:
        hex_string = hex_string.strip().upper()
        if len(hex_string) % 2 != 0:
            raise AIDError(f"Hex string must have even length: {hex_string}")
        try:
            data = bytes.fromhex(hex_string)
        except ValueError as e:
            raise AIDError(f"Invalid hex string: {hex_string}") from e
        return cls(data)

    @classmethod
    def from_bytes(cls, data: bytes | list[int]) -> Self:
        if isinstance(data, list):
            data = bytes(data)
        return cls(data)

    @classmethod
    def parse(cls, value: str | bytes | list[int] | AID) -> Self:
        if isinstance(value, AID):
            return value  # type: ignore[return-value]  # AID is compatible with Self
        match value:
            case bytes() | bytearray():
                return cls.from_bytes(value)
            case list():
                return cls.from_bytes(value)
            case str():
                return cls.from_hex(value)
            case _:
                raise AIDError(f"Cannot parse AID from {type(value).__name__}")

    def to_hex(self) -> str:
        return self._bytes.hex().upper()

    def to_jca(self) -> str:
        """Return as JCA format (0xA0:0x0:...) for capgen."""
        return ":".join(f"0x{b:X}" for b in self._bytes)

    def to_bytes(self) -> bytes:
        return self._bytes

    def __len__(self) -> int:
        return len(self._bytes)

    def __str__(self) -> str:
        return self.to_hex()

    def __repr__(self) -> str:
        return f"AID('{self.to_hex()}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AID):
            return self._bytes == other._bytes
        return False

    def __hash__(self) -> int:
        return hash(self._bytes)

    def __add__(self, other: bytes | int) -> AID:
        if isinstance(other, int):
            other = bytes([other])
        return AID(self._bytes + other)
