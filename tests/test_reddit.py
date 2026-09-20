"""Tests for the Reddit ingest collector (no network; config validation only)."""

import pytest

from sidha.ingest.reddit import RedditConfig


def test_config_missing_env_raises_helpful_error(monkeypatch):
    for var in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(RuntimeError, match="Missing Reddit credentials"):
        RedditConfig.from_env()


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "agent")
    cfg = RedditConfig.from_env()
    assert cfg.client_id == "id"
