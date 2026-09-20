"""Tests for the clinical ICD-10 mapping module (synthetic fixtures only)."""

import pytest

from sidha.clinical.icd10 import (
    COMORBIDITIES,
    HS_FAMILY,
    describe,
    find_by_keyword,
    is_hs_code,
    normalize_code,
)


def test_describe_hs():
    assert describe("L73.2") == "Hidradenitis suppurativa"


def test_describe_case_insensitive():
    assert describe("l73.2") == describe("L73.2")


def test_describe_unknown_returns_none():
    assert describe("Z99.9") is None


def test_is_hs_code():
    assert is_hs_code("L73.2")
    assert is_hs_code("l73.0")
    assert not is_hs_code("E11.9")
    assert not is_hs_code("Z99.9")


def test_normalize_code():
    assert normalize_code("l73.2") == "L73.2"
    assert normalize_code(" L732 ") == "L73.2"
    assert normalize_code("E11") == "E11"


def test_find_by_keyword():
    hits = find_by_keyword("hidradenitis")
    assert any(code == "L73.2" for code, _ in hits)


def test_find_by_keyword_case_insensitive():
    assert find_by_keyword("DIABETES") == find_by_keyword("diabetes")


def test_hs_family_complete():
    assert set(HS_FAMILY) == {"L73.0", "L73.1", "L73.2", "L73.8", "L73.9"}


def test_comorbidity_codes_present():
    for code in ("E66.9", "E11.9", "F32.9", "K50.90"):
        assert code in COMORBIDITIES
