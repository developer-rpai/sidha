"""Synthetic HS cohort generator.

Produces realistic-but-fake patient timelines for demos, tutorials, and tests.
No real patient data is involved: every value is drawn from seeded random
distributions shaped by published HS epidemiology (diagnostic delays of
several years, common misdiagnosis codes, typical comorbidity rates).

Deterministic: the same ``seed`` always yields the same cohort.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from ..ehr.events import ClinicalEvent

# (code, display, probability among HS patients)
_COMORBIDITIES: list[tuple[str, str, float]] = [
    ("E66.9", "Obesity, unspecified", 0.35),
    ("F32.9", "Major depressive disorder, single episode, unspecified", 0.30),
    ("F41.1", "Generalized anxiety disorder", 0.26),
    ("E28.2", "Polycystic ovary syndrome", 0.12),
    ("K50.90", "Crohn's disease, unspecified, without complications", 0.04),
    ("E11.9", "Type 2 diabetes mellitus without complications", 0.15),
    ("F17.210", "Nicotine dependence, cigarettes, uncomplicated", 0.30),
]

_PRE_DX_CODES: list[tuple[str, str]] = [
    ("L02.9", "Cutaneous abscess, furuncle and carbuncle, unspecified"),
    ("L70.0", "Acne vulgaris"),
    ("L05.91", "Pilonidal cyst without abscess"),
]

_POST_DX_MEDS: list[tuple[str, str]] = [
    ("RXNORM:1014673", "adalimumab"),
    ("RXNORM:260350", "clindamycin phosphate"),
    ("RXNORM:108729", "doxycycline"),
    ("RXNORM:1806098", "secukinumab"),
]


def generate_cohort(
    n_patients: int = 50,
    seed: int = 42,
    start_year: int = 2015,
) -> list[ClinicalEvent]:
    """Generate synthetic clinical events for ``n_patients`` HS patients."""
    rng = random.Random(seed)
    events: list[ClinicalEvent] = []
    for i in range(n_patients):
        pid = f"SYN-{i:04d}"
        base = date(start_year, 1, 1) + timedelta(days=rng.randint(0, 1500))
        # Diagnostic delay: 1-9 years from first suggestive code to HS diagnosis.
        delay_days = rng.randint(365, 365 * 9)
        first_symptom = base
        dx_date = base + timedelta(days=delay_days)

        # Pre-diagnosis: 2-6 misdiagnosis-coded encounters.
        n_pre = rng.randint(2, 6)
        for _ in range(n_pre):
            code, display = rng.choice(_PRE_DX_CODES)
            d = first_symptom + timedelta(
                days=rng.randint(0, max(delay_days - 30, 1))
            )
            events.append(
                ClinicalEvent(pid, d, "condition", code, "ICD10", display)
            )
        # The confirmed HS diagnosis.
        events.append(
            ClinicalEvent(
                pid, dx_date, "condition", "L73.2", "ICD10", "Hidradenitis suppurativa"
            )
        )
        # Post-diagnosis medications.
        for _ in range(rng.randint(1, 3)):
            rx, name = rng.choice(_POST_DX_MEDS)
            d = dx_date + timedelta(days=rng.randint(14, 700))
            events.append(ClinicalEvent(pid, d, "medication", rx, "RXNORM", name))
        # Comorbidities.
        for code, display, prob in _COMORBIDITIES:
            if rng.random() < prob:
                d = base + timedelta(days=rng.randint(0, delay_days + 700))
                events.append(
                    ClinicalEvent(pid, d, "condition", code, "ICD10", display)
                )
        # Flare observations: 0-8 dated flare events after diagnosis.
        for _ in range(rng.randint(0, 8)):
            d = dx_date + timedelta(days=rng.randint(30, 900))
            events.append(
                ClinicalEvent(
                    pid, d, "observation", "FLARE", "SIDHA", "HS flare episode", value="1"
                )
            )
    events.sort(key=lambda e: (e.patient_id, e.event_date))
    return events
