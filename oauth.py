"""
services/oauth.py
─────────────────
Google OAuth 2.0 flow for per-user credential management.
Stores tokens in local JSON files (extend to DB for production).

Flow:
    1. generate_auth_url(user_id) → redirect user to Google consent screen
    2. exchange_code(user_id, code) → trades auth code for access+refresh tokens
    3. get_credentials(user_id) → returns valid Credentials (auto-refreshes)
"""

import os
import json
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

from config.settings import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
]

TOKEN_DIR = Path("data/tokens")
TOKEN_DIR.mkdir(parents=True, exist_ok=True)


def _token_path(user_id: int) -> Path:
    return TOKEN_DIR / f"{user_id}.json"


def generate_auth_url(user_id: int) -> str:
    """
    Step 1: Build the Google OAuth consent URL.
    Send this URL to the user so they can authorize the bot.

    Returns:
        str: Authorization URL to redirect user to.
    """
    flow = Flow.from_client_config(
        client_config=_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.OAUTH_REDIRECT_URI,
    )
    flow.code_verifier = str(user_id)  # simple state binding

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=str(user_id),
        prompt="consent",  # force refresh_token on every consent
    )
    logger.info("Generated auth URL for user %s", user_id)
    return auth_url


def exchange_code(user_id: int, code: str) -> Credentials:
    """
    Step 2: Exchange authorization code for tokens and persist them.

    Args:
        user_id: Telegram user ID (used as token filename)
        code: Authorization code returned by Google redirect

    Returns:
        google.oauth2.credentials.Credentials
    """
    flow = Flow.from_client_config(
        client_config=_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.OAUTH_REDIRECT_URI,
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    _save_credentials(user_id, creds)
    logger.info("Tokens saved for user %s", user_id)
    return creds


def get_credentials(user_id: int) -> Credentials:
    """
    Step 3: Load stored credentials, refreshing if expired.

    Raises:
        FileNotFoundError: If user hasn't authorized yet.
        google.auth.exceptions.RefreshError: If refresh token is revoked.
    """
    path = _token_path(user_id)
    if not path.exists():
        raise FileNotFoundError(f"No token for user {user_id}. Run /connect first.")

    creds = Credentials.from_authorized_user_file(str(path), SCOPES)

    if creds.expired and creds.refresh_token:
        logger.debug("Refreshing token for user %s", user_id)
        creds.refresh(Request())
        _save_credentials(user_id, creds)

    return creds


# ── Private helpers ──────────────────────────────────────────────────────────

def _client_config() -> dict:
    """Build client_config dict from environment variables (no JSON file needed)."""
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.OAUTH_REDIRECT_URI],
        }
    }


def _save_credentials(user_id: int, creds: Credentials) -> None:
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }
    _token_path(user_id).write_text(json.dumps(token_data, indent=2))
