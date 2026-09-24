"""EDGAR HTTP client — D-023's rules, implemented.

D-023: a declared User-Agent with contact details; a hard client-side rate
limit; retry with backoff on 429 and 503; and **no retry that hides a 403**.
Every fetch records source URL, retrieval timestamp, and a hash of the payload.

WHY THE RATE LIMIT IS A CONSTANT AND NOT A SLEEP
------------------------------------------------
D-023 required "a hard client-side rate limit" and never named a figure. The SEC
publishes one:

    "our current maximum access rate is 10 requests per second. This is
     carefully monitored to preserve equitable access for all users."

A guessed sleep that happens to be slower than the limit is indistinguishable
from a correct one — until the limit changes, at which point it becomes
indistinguishable from a correct one that has silently become wrong. So the
number is named, attributed and citable, and the interval is derived from it
rather than chosen.

WHY 403 IS NOT RETRYABLE
------------------------
A 403 from EDGAR means the request was refused — usually a missing or
unacceptable User-Agent. Retrying makes the refusal worse rather than better,
and a retry that swallows it turns a policy failure into a silent data gap
(A-004). It raises immediately and says what it was doing.

This module lives outside ``app/``. The web process is read-only against
Postgres (D-031) and must not be able to import an ingestion path.
"""

from __future__ import annotations

import hashlib
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

# SEC-published maximum access rate. Source: SEC webmaster FAQ / developer
# guidance, retrieved 2026-09-23. See F-next/edgar-limits-established.
SEC_MAX_REQUESTS_PER_SECOND = 10

# We deliberately run below the published ceiling. Sitting exactly on a limit
# means any clock skew or burst puts us over it, and being throttled is a data
# gap that arrives as a success (A-004's failure mode).
TARGET_REQUESTS_PER_SECOND = 5

# SEC-published User-Agent format:
#   "Sample Company Name AdminContact@<sample company domain>.com"
USER_AGENT = "StockGraderMDK mdk32366@gmail.com"

RETRYABLE_STATUSES = (429, 503)
MAX_RETRIES = 4


class EdgarRefused(RuntimeError):
    """A 403. Never retried, never swallowed. See D-023."""


class EdgarUnavailable(RuntimeError):
    """429/503 that did not clear within MAX_RETRIES."""


@dataclass(frozen=True)
class Fetch:
    """One retrieval, with the provenance D-023 requires.

    D-023 says every fetch records source URL, retrieval timestamp and a hash of
    the payload, and that raw filings are **not** stored — EDGAR is the
    authoritative permanent copy, and accession plus hash makes any row
    re-derivable. This carries that triple so a caller can record it.

    NOTE, and it is an open gap rather than an oversight: there is currently
    nowhere in the schema to persist this. 0001 has no fetch/provenance table.
    See testplan OPEN-34 — the client produces provenance and slice 1 has no
    column to put it in.
    """

    url: str
    retrieved_at: datetime
    sha256: str
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8")


class RateLimiter:
    """Minimum-interval limiter.

    Deliberately the simplest thing that cannot burst: it holds a floor on the
    gap between consecutive requests. A token bucket would allow a burst that is
    momentarily over the published rate, which is the case the limit exists to
    prevent.
    """

    def __init__(self, requests_per_second: float = TARGET_REQUESTS_PER_SECOND,
                 *, sleep=time.sleep, clock=time.monotonic) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if requests_per_second > SEC_MAX_REQUESTS_PER_SECOND:
            raise ValueError(
                f"{requests_per_second} req/s exceeds the SEC published maximum "
                f"of {SEC_MAX_REQUESTS_PER_SECOND}. The limit is not a tuning "
                "parameter."
            )
        self._min_interval = 1.0 / requests_per_second
        self._sleep = sleep
        self._clock = clock
        self._last: float | None = None

    def wait(self) -> None:
        now = self._clock()
        if self._last is not None:
            elapsed = now - self._last
            if elapsed < self._min_interval:
                self._sleep(self._min_interval - elapsed)
        self._last = self._clock()


class EdgarClient:
    def __init__(self, *, user_agent: str = USER_AGENT,
                 limiter: RateLimiter | None = None,
                 opener=None, sleep=time.sleep) -> None:
        if "@" not in user_agent:
            # The SEC's format requires contact details. A User-Agent without
            # them is the thing that earns a 403, so refuse it here rather than
            # discover it mid-crawl.
            raise ValueError(
                "User-Agent must carry contact details in the SEC's published "
                f"format; got {user_agent!r}"
            )
        self.user_agent = user_agent
        self.limiter = limiter or RateLimiter()
        self._opener = opener or urllib.request.urlopen
        self._sleep = sleep

    def fetch(self, url: str) -> Fetch:
        attempt = 0
        while True:
            self.limiter.wait()
            request = urllib.request.Request(
                url, headers={"User-Agent": self.user_agent,
                              "Accept-Encoding": "gzip, deflate"}
            )
            try:
                with self._opener(request) as response:
                    body = response.read()
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 403:
                    # D-023: no retry that hides a 403.
                    raise EdgarRefused(
                        f"EDGAR refused {url} with 403. This is a refusal, not a "
                        "transient failure, and it is not retried. Check the "
                        f"User-Agent ({self.user_agent!r}) and the request rate. "
                        "A-004 is falsified until this is resolved."
                    ) from exc
                if exc.code in RETRYABLE_STATUSES and attempt < MAX_RETRIES:
                    # Exponential backoff. 429 and 503 are the platform asking
                    # us to slow down, which is a different statement from 403.
                    self._sleep(2 ** attempt)
                    attempt += 1
                    continue
                if exc.code in RETRYABLE_STATUSES:
                    raise EdgarUnavailable(
                        f"EDGAR returned {exc.code} for {url} after "
                        f"{MAX_RETRIES} retries."
                    ) from exc
                raise

        return Fetch(
            url=url,
            retrieved_at=datetime.now(timezone.utc),
            sha256=hashlib.sha256(body).hexdigest(),
            body=body,
        )
