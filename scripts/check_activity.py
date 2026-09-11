#!/usr/bin/env python3
"""
Check if the user has pushed any actual commits/contributions
to repositories OTHER than the profile README repository (username/username).
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Add scripts directory to path for config
sys.path.append(str(Path(__file__).parent))
try:
    import config
    USERNAME = getattr(config, "USERNAME", "KenBoi26")
    CONTRIBUTIONS_JSON_PATH = getattr(config, "CONTRIBUTIONS_JSON_PATH", Path(__file__).parent.parent / "data" / "contributions.json")
except ImportError:
    USERNAME = os.getenv("GITHUB_USERNAME", "KenBoi26")
    CONTRIBUTIONS_JSON_PATH = Path(__file__).parent.parent / "data" / "contributions.json"

def set_github_output(name: str, value: str):
    """Writes an output parameter to $GITHUB_OUTPUT if running in GitHub Actions."""
    output_file = os.getenv("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
    print(f"[check_activity] Set output: {name}={value}")

def parse_iso_datetime(dt_str: str) -> datetime:
    """Safely parses ISO-8601 timestamps into UTC datetime."""
    clean_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(clean_str).astimezone(timezone.utc)

def get_last_updated_time() -> datetime | None:
    """Reads the last updated timestamp from data/contributions.json."""
    if not CONTRIBUTIONS_JSON_PATH.exists():
        return None
    try:
        data = json.loads(CONTRIBUTIONS_JSON_PATH.read_text(encoding="utf-8"))
        updated_str = data.get("updated_at")
        if updated_str:
            return parse_iso_datetime(updated_str)
    except Exception as e:
        print(f"[check_activity] Warning: Could not parse last updated time from {CONTRIBUTIONS_JSON_PATH}: {e}")
    return None

def check_recent_pushes(username: str, last_updated: datetime | None) -> bool:
    """
    Queries GitHub's Events API to check if there were any PushEvents
    to repositories OTHER than username/username since last_updated.
    """
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Profile-Art-Updater"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/users/{username}/events?per_page=30"
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                print(f"[check_activity] Events API returned HTTP {resp.status}.")
                return False
            events = json.loads(resp.read().decode("utf-8"))

        if not isinstance(events, list):
            return False

        profile_repo = f"{username}/{username}".lower()

        for event in events:
            if event.get("type") != "PushEvent":
                continue

            repo_name = event.get("repo", {}).get("name", "").lower()
            if repo_name == profile_repo:
                # Ignore automated or manual pushes to the profile README repo itself
                continue

            event_time_str = event.get("created_at")
            if not event_time_str:
                continue

            event_time = parse_iso_datetime(event_time_str)

            # If this push happened after our last recorded update:
            if last_updated is None or event_time > last_updated:
                print(f"[check_activity] Detected new push to project repo: '{repo_name}' at {event_time_str}")
                return True

        print(f"[check_activity] No new PushEvents found in project repos since {last_updated}.")
        return False

    except urllib.error.HTTPError as e:
        print(f"[check_activity] HTTP error querying Events API: {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"[check_activity] Error querying Events API: {e}")
        return False

def check_calendar_increase(username: str) -> bool:
    """
    Fallback check: queries GitHub contribution calendar to see if today's count
    increased beyond what was saved in data/contributions.json.
    Because bot commits use github-actions[bot], they are not in the calendar,
    so an increase represents genuine user activity.
    """
    if not CONTRIBUTIONS_JSON_PATH.exists():
        return False

    try:
        data = json.loads(CONTRIBUTIONS_JSON_PATH.read_text(encoding="utf-8"))
        days_map = {d["date"]: d["count"] for d in data.get("days", [])}

        url = f"https://github.com/users/{username}/contributions"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Accept": "text/html"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")

        import re
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        stored_today = days_map.get(today_str, 0)

        # Look for today's date in calendar html
        pattern = rf'data-date="{today_str}"[^>]*data-level="(\d+)"'
        match = re.search(pattern, html)
        if match:
            level = int(match.group(1))
            if level > 0 and stored_today == 0:
                print(f"[check_activity] Activity detected in calendar for {today_str} (level {level}).")
                return True

    except Exception as e:
        print(f"[check_activity] Calendar check error: {e}")

    return False

def should_update() -> bool:
    event_name = os.getenv("EVENT_NAME", "").lower()

    # Manual workflow runs or external webhooks always update
    if event_name in ["workflow_dispatch", "repository_dispatch"]:
        print(f"[check_activity] Run triggered via '{event_name}'. Proceeding with update.")
        return True

    # If triggered by a direct push by the user to main, update
    if event_name == "push":
        actor = os.getenv("GITHUB_ACTOR", "")
        if actor and "bot" not in actor.lower():
            print(f"[check_activity] Push event by user '{actor}'. Proceeding with update.")
            return True

    last_updated = get_last_updated_time()
    if last_updated:
        print(f"[check_activity] Last profile update was at: {last_updated.isoformat()}")
    else:
        print("[check_activity] No prior update timestamp found. Running initial update.")
        return True

    # 1. Primary check: PushEvents on GitHub Events API for other repos
    if check_recent_pushes(USERNAME, last_updated):
        return True

    # 2. Fallback check: Did contribution count increase in the calendar?
    if check_calendar_increase(USERNAME):
        return True

    return False

def main():
    update = should_update()
    set_github_output("should_update", "true" if update else "false")
    if update:
        print("[check_activity] Result: Real project activity found -> Proceeding with update.")
    else:
        print("[check_activity] Result: No new pushes to other projects -> Skipping update.")

if __name__ == "__main__":
    main()
