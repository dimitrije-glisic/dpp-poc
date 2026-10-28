"""Application settings, read from environment variables with demo-friendly defaults."""

import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dpp.db")

# Base URL encoded into QR codes. Set this to your LAN address (e.g. http://192.168.1.20:8000)
# if you want to scan QR codes with a phone; "localhost" only works on this machine.
# PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "http://192.168.1.221:8000").rstrip("/")
