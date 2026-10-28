"""QR code generation for passport URLs."""

import io

import segno

from app.config import PUBLIC_BASE_URL


def passport_url(product_id: str, base_url: str = PUBLIC_BASE_URL) -> str:
    return f"{base_url.rstrip('/')}/passport/{product_id}"


def make_qr(data: str, kind: str = "png", scale: int = 6) -> bytes:
    """Return QR code image bytes. kind is 'png' or 'svg'."""
    qr = segno.make(data, error="m")
    buffer = io.BytesIO()
    qr.save(buffer, kind=kind, scale=scale, border=2)
    return buffer.getvalue()
