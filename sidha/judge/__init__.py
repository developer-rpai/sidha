"""judge — LLM-as-judge evaluation harness.

Given a case vignette and candidate diagnoses, an LLM judge scores the quality
of differential-diagnosis ranking against a rubric. Prompt templates, rubrics,
and scoring logic live here and are swappable across models.

Research evaluation only — not a diagnostic device.
"""
