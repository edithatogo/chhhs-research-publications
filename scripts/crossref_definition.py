"""Canonical fingerprint for exact Crossref definition preparation gates."""
from __future__ import annotations

import hashlib
import json


def fingerprint(definition):
    """Hash the complete definition without depending on a recovery builder."""
    return hashlib.sha256(json.dumps(
        definition, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False).encode()).hexdigest()
