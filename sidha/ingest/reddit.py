"""Reddit collector — public, read-only, ToS-compliant.

Credentials come from the environment and are never committed::

    export REDDIT_CLIENT_ID="..."
    export REDDIT_CLIENT_SECRET="..."
    export REDDIT_USER_AGENT="sidha-research/0.1 by <contact>"

Requires the ``social`` extra:  ``pip install -e ".[social]"``
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

_ENV_VARS = ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT")


@dataclass
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str

    @classmethod
    def from_env(cls) -> "RedditConfig":
        missing = [v for v in _ENV_VARS if not os.environ.get(v)]
        if missing:
            raise RuntimeError(
                "Missing Reddit credentials in environment: "
                + ", ".join(missing)
                + ". Set them as environment variables; never commit them."
            )
        return cls(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
        )


def _require_praw():
    try:
        import praw
    except ImportError as exc:
        raise RuntimeError(
            'The Reddit collector needs the "social" extra: pip install -e ".[social]"'
        ) from exc
    return praw


def collect(
    subreddit: str,
    query: str,
    *,
    limit: int = 25,
    sort: str = "relevance",
    config: RedditConfig | None = None,
) -> list[dict]:
    """Collect public posts from a subreddit. Each record carries provenance.

    Read-only: never posts, votes, or messages. Keep ``limit`` modest and
    respect rate limits.
    """
    praw = _require_praw()
    cfg = config or RedditConfig.from_env()
    reddit = praw.Reddit(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        user_agent=cfg.user_agent,
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    records: list[dict] = []
    for post in reddit.subreddit(subreddit).search(query, sort=sort, limit=limit):
        records.append(
            {
                "id": post.id,
                "title": post.title,
                "selftext": post.selftext,
                "url": post.url,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": datetime.fromtimestamp(
                    post.created_utc, tz=timezone.utc
                ).isoformat(),
                "provenance": {
                    "source": "reddit",
                    "subreddit": subreddit,
                    "query": query,
                    "retrieved_at": retrieved_at,
                },
            }
        )
    return records
