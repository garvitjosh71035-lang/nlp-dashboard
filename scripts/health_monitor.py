from __future__ import annotations

import os
import sys
import time
from urllib.parse import urljoin

import requests


APP_URL = os.environ.get("APP_URL", "").strip().rstrip("/")
ATTEMPTS = int(os.environ.get("HEALTH_ATTEMPTS", "5"))
TIMEOUT = int(os.environ.get("HEALTH_TIMEOUT", "20"))


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def check_once(session: requests.Session, attempt: int) -> bool:
    health_url = urljoin(APP_URL + "/", "_stcore/health")
    started = time.perf_counter()

    try:
        health = session.get(health_url, timeout=TIMEOUT, allow_redirects=True)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        body = health.text.strip().lower()

        health_ok = health.status_code == 200 and (body in {"ok", "healthy"} or "ok" in body)
        if not health_ok:
            print(
                f"FAIL attempt {attempt}/{ATTEMPTS}: health endpoint returned "
                f"HTTP {health.status_code} in {elapsed_ms} ms; body={body[:120]!r}"
            )
            return False

        # Also verify that the public root page is reachable. This catches cases
        # where the Streamlit process answers health checks but the deployment
        # route itself is broken.
        root_started = time.perf_counter()
        root = session.get(APP_URL + "/", timeout=TIMEOUT, allow_redirects=True)
        root_ms = round((time.perf_counter() - root_started) * 1000)
        content_type = root.headers.get("content-type", "").lower()
        root_ok = root.status_code == 200 and ("text/html" in content_type or len(root.content) > 200)

        if not root_ok:
            print(
                f"FAIL attempt {attempt}/{ATTEMPTS}: root page returned "
                f"HTTP {root.status_code} in {root_ms} ms; content-type={content_type!r}"
            )
            return False

        print(
            f"PASS attempt {attempt}/{ATTEMPTS}: health HTTP 200 ({elapsed_ms} ms), "
            f"root HTTP 200 ({root_ms} ms). Dashboard is healthy."
        )
        return True

    except requests.RequestException as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        print(f"FAIL attempt {attempt}/{ATTEMPTS} after {elapsed_ms} ms: {exc}")
        return False


def main() -> None:
    if not APP_URL:
        fail("APP_URL is missing. Add it as a GitHub Actions repository secret.")
    if not APP_URL.startswith(("http://", "https://")):
        fail("APP_URL must start with http:// or https://")

    print(f"Monitoring {APP_URL}")
    print(f"Attempts={ATTEMPTS}, timeout={TIMEOUT}s")

    session = requests.Session()
    session.headers.update({"User-Agent": "nlp-dashboard-health-monitor/1.0"})

    for attempt in range(1, ATTEMPTS + 1):
        if check_once(session, attempt):
            return
        if attempt < ATTEMPTS:
            delay = min(5 * (2 ** (attempt - 1)), 30)
            print(f"Retrying in {delay}s…")
            time.sleep(delay)

    fail(f"Dashboard remained unhealthy after {ATTEMPTS} attempts.")


if __name__ == "__main__":
    main()
