"""Store a downloaded Desktop OAuth client JSON in DVC's ignored local config.

Usage: python assignment/configure_drive.py PATH_TO_DOWNLOADED_CLIENT_JSON
Never paste the client secret into a chat or commit the downloaded JSON.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
os.chdir(root)
if len(sys.argv) != 2:
    raise SystemExit(__doc__)
if not (root / ".dvc/config").exists():
    raise SystemExit("Run the history step first to initialize DVC.")
document = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if "installed" not in document:
    raise SystemExit("Use OAuth credentials for a Desktop app, not a Web app or service account.")
client = document["installed"]
for key in ("client_id", "client_secret"):
    value = client.get(key)
    if not value:
        raise SystemExit(f"Missing {key} in the downloaded OAuth file.")
    subprocess.run([sys.executable, "-m", "dvc", "remote", "modify", "--local",
                    "gdrive_storage", "gdrive_" + key, value], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("OAuth settings saved in .dvc/config.local. Values were not printed.")
print("Run dvc push and complete the Google sign-in in your browser.")
