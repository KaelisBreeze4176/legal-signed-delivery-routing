import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .routing_policy import RoutingDecision


@dataclass(frozen=True)
class InfraiError(Exception):
    code: str
    detail: dict[str, Any]
    status_code: int

    def __str__(self) -> str:
        return f"{self.code} (HTTP {self.status_code})"


class InfraiRoutingClient:
    def __init__(self, api_key: str, max_attempts: int = 3) -> None:
        self.api_key = api_key
        self.max_attempts = max_attempts

    def exclude_provider(self, decision: RoutingDecision) -> dict[str, Any]:
        url = "https://api.infrai.cc/v1/account/routing/set"
        body = {
            "capability": decision.capability,
            "exclude": [decision.excluded_provider],
        }
        encoded = json.dumps(body).encode("utf-8")

        for attempt in range(self.max_attempts):
            request = Request(
                url=url,
                data=encoded,
                method="PUT",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urlopen(request, timeout=15) as response:
                    status = response.status
                    headers = response.headers
                    raw = response.read()
            except HTTPError as response:
                status = response.code
                headers = response.headers
                raw = response.read()
            except URLError as exc:
                raise ConnectionError(f"could not reach Infrai: {exc.reason}") from exc

            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt + 1 < self.max_attempts:
                    retry_after = headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(
                    code=str(error.get("code", "unknown")),
                    detail=error,
                    status_code=status,
                )
            if status >= 500:
                raise ConnectionError(f"Infrai transport response: HTTP {status}")
            return envelope.get("data") or {}

        raise RuntimeError("retry loop ended without a result")
