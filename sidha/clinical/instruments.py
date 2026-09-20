"""Clinical instrument helpers for HS research.

- :func:`hurley_stage`: Hurley staging from structured clinical features.
- :func:`score_likert_scale`: generic scorer for Likert-style instruments
  (HiSQOL, HSSD, DLQI, ...). Item lists must be verified against the published
  instrument before use in a study; this module handles the arithmetic, not
  the instrument definitions.
"""

from __future__ import annotations


def hurley_stage(
    *,
    abscesses: bool,
    sinus_tracts: bool,
    scarring: bool,
    diffuse_involvement: bool,
) -> str:
    """Assign a Hurley stage from structured clinical features.

    - Stage I: abscess formation, single or multiple, without sinus tracts
      or scarring.
    - Stage II: recurrent abscesses with sinus tracts and scarring, but
      lesions remain separated (not diffuse).
    - Stage III: diffuse involvement with interconnected sinus tracts and
      scarring across the affected region.

    Returns "I", "II", "III", or "indeterminate" when the features do not
    describe active HS disease.
    """
    if not abscesses:
        return "indeterminate"
    if diffuse_involvement and sinus_tracts and scarring:
        return "III"
    if sinus_tracts or scarring:
        return "II"
    return "I"


def score_likert_scale(
    responses: list[int | None],
    *,
    max_per_item: int,
    min_answered: int | None = None,
) -> dict[str, float | int | None]:
    """Score a Likert-style instrument from item responses.

    ``responses`` holds one value per item (None for unanswered). Scoring
    follows the common convention: prorate by answered items when at least
    ``min_answered`` items (default: all) are present, otherwise the score
    is None (insufficient data).
    """
    answered = [r for r in responses if r is not None]
    required = min_answered if min_answered is not None else len(responses)
    if len(answered) < required or not answered:
        return {"score": None, "n_items": len(responses), "n_answered": len(answered)}
    if any(r < 0 or r > max_per_item for r in answered):
        raise ValueError(f"responses must be within 0..{max_per_item}")
    prorated = round(sum(answered) / len(answered) * len(responses), 2)
    return {"score": prorated, "n_items": len(responses), "n_answered": len(answered)}
