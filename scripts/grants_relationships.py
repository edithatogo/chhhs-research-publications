"""Review-gated typed relationships between grants and existing RIMS entities."""
from __future__ import annotations

import hashlib
from typing import Any

RELATION_TYPES = {
    'funded_by_award', 'relevant_to_opportunity', 'investigator_affiliation',
}
CONFIDENCE = {'confirmed', 'review', 'candidate'}


def normalize_relationship(record: dict[str, Any]) -> dict[str, Any]:
    relation = str(record.get('RelationshipType', '')).strip()
    source_key = str(record.get('FromKey', '')).strip()
    target_key = str(record.get('ToKey', '')).strip()
    evidence = str(record.get('EvidenceURL', '')).strip()
    confidence = str(record.get('Confidence', 'review')).strip().lower()
    if relation not in RELATION_TYPES:
        raise ValueError('unsupported relationship type')
    if not source_key or not target_key or not evidence:
        raise ValueError('relationship requires from/to keys and evidence')
    if confidence not in CONFIDENCE:
        raise ValueError('unsupported confidence')
    if confidence == 'confirmed' and relation == 'funded_by_award' and not record.get('AwardID'):
        raise ValueError('confirmed award relationship requires AwardID')
    basis = '|'.join((relation, source_key, target_key, str(record.get('AwardID', '')), evidence))
    return {
        'RelationshipKey': 'REL:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24],
        'RelationshipType': relation,
        'FromKey': source_key,
        'ToKey': target_key,
        'AwardID': str(record.get('AwardID', '')).strip(),
        'EvidenceURL': evidence,
        'Confidence': confidence,
        'ReviewStatus': str(record.get('ReviewStatus', 'Needs Review')).strip() or 'Needs Review',
    }
