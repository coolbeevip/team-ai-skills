"""Vendored common helpers for team-ai-skills scripts.

This file is the source copy. Keep skill-local copies synchronized with:

    python3 scripts/check_vendored_common.py
"""

from __future__ import annotations

import ipaddress
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class ApiRequestError(RuntimeError):
    """HTTP request failure with platform-specific context."""


def no_proxy_entries() -> list[str]:
    value = os.environ.get("no_proxy") or os.environ.get("NO_PROXY") or ""
    return [entry.strip() for entry in value.split(",") if entry.strip()]


def host_matches_no_proxy(host: str, entry: str) -> bool:
    host = host.lower().strip("[]")
    entry = entry.lower()
    if entry == "*":
        return True
    if "/" in entry:
        try:
            return ipaddress.ip_address(host) in ipaddress.ip_network(entry, strict=False)
        except ValueError:
            return False
    if entry.startswith("*."):
        suffix = entry[1:]
        return host.endswith(suffix)
    if entry.startswith("."):
        return host == entry[1:] or host.endswith(entry)
    return host == entry or host.endswith(f".{entry}")


def should_bypass_proxy(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    return any(host_matches_no_proxy(host, entry) for entry in no_proxy_entries())


def print_request_debug(
    service: str,
    method: str,
    url: str,
    payload: dict[str, Any] | None,
) -> None:
    request_info = {
        "method": method,
        "url": url,
        "payload": payload or {},
    }
    print(
        f"{service} request: "
        + json.dumps(request_info, ensure_ascii=False, sort_keys=True),
        file=sys.stderr,
    )


def api_request(
    method: str,
    url: str,
    token: str,
    headers: dict[str, str],
    *,
    payload: dict[str, Any] | None = None,
    service: str = "API",
    timeout: int = 30,
    debug: bool = False,
) -> Any:
    data = None
    request_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    if debug:
        print_request_debug(service, method, url, payload)
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    opener = (
        urllib.request.build_opener(urllib.request.ProxyHandler({}))
        if should_bypass_proxy(url)
        else urllib.request.build_opener()
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiRequestError(
            f"{service} API {method} {url} failed: {exc.code} {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise ApiRequestError(f"{service} API {method} {url} failed: {exc.reason}") from exc
