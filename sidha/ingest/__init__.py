"""ingest — capture layer.

Collectors for public social-listening data (Reddit, X, HS-related Facebook
groups) and loaders for episodic clinical/diagnostic record exports.

Rules: public data only; honor platform terms of service and robots.txt;
log provenance (source, retrieval timestamp, query) with every payload;
never commit credentials — use environment variables.
"""

from sidha.ingest.reddit import RedditConfig, collect

__all__ = ["RedditConfig", "collect"]
