"""
Run once locally to create the Google Calendar OAuth token file used by the backend.
"""

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

from app.config import get_settings

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def main():
    settings = get_settings()
    secrets_path = Path(settings.google_client_secrets_file)
    token_path = Path(settings.google_token_file)
    token_path.parent.mkdir(parents=True, exist_ok=True)

    if not secrets_path.exists():
        raise FileNotFoundError(
            f"Client secret file not found at {secrets_path}. Download OAuth desktop credentials from Google Cloud first."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved token to {token_path}")


if __name__ == "__main__":
    main()
