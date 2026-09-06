#!/usr/bin/env python3
"""Reliable health probe for the deployed Streamlit dashboard.

Designed for GitHub Actions and local use. It checks Streamlit's documented
/_stcore/health endpoint, retries transient failures, validates the response,
and exits non-zero when the dashboard cannot be confirmed healthy.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


APP_URL = os.environ.get("APP_URL", "").strip().rstrip("/")
ATTEMPTS = int(os.environ.get("HEALTH_ATTEMPTS", "5"))
TIMEOUT_SECONDS = float(os.environ.get("HEALTH_TIMEOUT_SECONDS", "20"))
INITIAL_BACKOFF_SECONDS = float(os.environ.get("HEALTH_INITIAL_BACKOFF_SECONDS", "2"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_healthy_body(body: str) -> bool:
    """Accept current Streamlit health response formats without being brittle."""
    normalized = body.strip().lower()
    if normalized in {"ok", "healthy"}:
        return True

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return "ok" in normalized and len(normalized) < 256

    if isinstance(payload, dict):
        status = str(payload.get("status", "")).strip().lower()
        return status in {"ok", "healthy"}
    return False


def probe(url: str) -> tuple[bool, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "nlp-dashboard-health-monitor/1.0",
            "Accept": "text/plain, application/json;q=0.9, */*;q=0.1",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )

    started = time.monotonic()
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", response.getcode())
            body = response.read(4096).decode("utf-8", errors="replace")
            latency_ms = int((time.monotonic() - started) * 1000)
            if status != 200:
                return False, f"HTTP {status} in {latency_ms} ms"
            if not is_healthy_body(body):
                preview = " ".join(body.strip().split())[:160]
                return False, f"HTTP 200 but unexpected health body in {latency_ms} ms: {preview!r}"
            return True, f"HTTP 200, healthy, {latency_ms} ms"
    except HTTPError as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        return False, f"HTTP {exc.code} after {latency_ms} ms"
    except URLError as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        return False, f"network error after {latency_ms} ms: {exc.reason}"
    except TimeoutError:
        latency_ms = int((time.monotonic() - started) * 1000)
        return False, f"timeout after {latency_ms} ms"
    except Exception as exc:  # Defensive: monitor must fail loudly, not crash silently.
        latency_ms = int((time.monotonic() - started) * 1000)
        return False, f"{type(exc).__name__} after {latency_ms} ms: {exc}"


def main() -> int:
    if not APP_URL:
        print("ERROR: APP_URL is not configured.")
        print("Create the GitHub Actions repository secret APP_URL with your Replit deployment URL.")
        return 2

    if not APP_URL.startswith(("https://", "http://")):
        print(f"ERROR: APP_URL must start with http:// or https://, got: {APP_URL!r}")
        return 2

    health_url = urljoin(APP_URL + "/", "_stcore/health")
    print(f"[{utc_now()}] Monitoring {health_url}")
    print(f"Attempts={ATTEMPTS}, timeout={TIMEOUT_SECONDS:g}s")

    backoff = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, ATTEMPTS + 1):
        healthy, detail = probe(health_url)
        marker = "PASS" if healthy else "FAIL"
        print(f"[{utc_now()}] {marker} attempt {attempt}/{ATTEMPTS}: {detail}")
        if healthy:
            print(f"[{utc_now()}] Dashboard is healthy: {APP_URL}")
            return 0

        if attempt < ATTEMPTS:
            print(f"Retrying in {backoff:g}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, 20)

    print(f"[{utc_now()}] ERROR: dashboard did not become healthy after {ATTEMPTS} attempts.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
