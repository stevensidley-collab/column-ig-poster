"""Update docs/redirect.json with the latest column URL and push via the local git/gh credentials."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REDIRECT_JSON = REPO_ROOT / "docs" / "redirect.json"


def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def update_bio_redirect(column_url: str, title: str) -> str:
    """Write the new column URL to docs/redirect.json and commit+push the change.

    Returns the git output (stdout) for display in the app.
    """
    REDIRECT_JSON.write_text(
        json.dumps({"url": column_url, "title": title}, indent=2) + "\n"
    )

    _run_git("add", "docs/redirect.json")
    status = _run_git("status", "--porcelain", "docs/redirect.json")
    if not status.stdout.strip():
        return "No change to bio redirect (already pointing at this URL)."

    _run_git("commit", "-m", f"Update bio redirect to: {title}")
    push = _run_git("push")
    return push.stdout + push.stderr
