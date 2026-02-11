"""APDU construction utilities."""


def build_apdu(
    ins: int,
    p1: int = 0,
    p2: int = 0,
    data: bytes = None,
    ne: int = 0,
    cla: int = 0x80,
    extended: bool = None,
) -> str:
    """Build an APDU hex string. Uses extended format when data > 255 or ne > 256."""
    apdu = f"{cla:02X}{ins:02X}{p1:02X}{p2:02X}"

    data_len = len(data) if data else 0
    use_extended = extended if extended is not None else (data_len > 255 or ne > 256)

    if data:
        if use_extended:
            # Extended Lc: 00 Lc1 Lc2
            apdu += f"00{data_len:04X}"
        else:
            # Short Lc
            apdu += f"{data_len:02X}"
        apdu += data.hex().upper()

    if ne > 0:
        if use_extended:
            if not data:
                apdu += "00"  # Extended format indicator
            # Extended Le: Le1 Le2 (0000 = 65536)
            if ne >= 65536:
                apdu += "0000"
            else:
                apdu += f"{ne:04X}"
        else:
            # Short Le (00 = 256)
            le_byte = 0 if ne == 256 else ne
            apdu += f"{le_byte:02X}"

    return apdu


def parse_response(data: bytes, sw: int) -> tuple[bytes, bool]:
    """
    Parse an APDU response.

    Args:
        data: Response data bytes
        sw: Status word (2 bytes as int)

    Returns:
        Tuple of (data, success) where success is True if SW=9000
    """
    return data, sw == 0x9000
