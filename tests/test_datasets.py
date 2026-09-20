"""Tests for the dataset catalog."""

from sidha.datasets import catalog, with_loaders


def test_catalog_lists_sources():
    sources = catalog()
    assert len(sources) >= 7
    assert all({"name", "modality", "access", "loader", "notes"} <= set(s) for s in sources)


def test_with_loaders_returns_available_only():
    available = with_loaders()
    assert available
    assert all(s["loader"] == "available" for s in available)
