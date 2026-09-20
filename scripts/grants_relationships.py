"""Review-gated typed relationships between grants and existing RIMS entities."""
from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlsplit

RELATION_TYPES = {
    'funded_by_award', 'relevant_to_opportunity', 'investigator_affiliation',
}
CONFIDENCE = {'confirmed', 'review', 'candidate'}
REVIEW_STATUSES = {'Needs Review', 'Included', 'Excluded'}


def _valid_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value.strip())
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def normalize_relationship(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError('relationship record must be an object')
    required = ('RelationshipType', 'FromKey', 'ToKey', 'EvidenceURL')
    if any(not isinstance(record.get(field), str) for field in required):
        raise ValueError('relationship fields must be strings')
    relation = record['RelationshipType'].strip()
    source_key = record['FromKey'].strip()
    target_key = record['ToKey'].strip()
    evidence = record['EvidenceURL'].strip()
    confidence_value = record.get('Confidence', 'review')
    if not isinstance(confidence_value, str):
        raise ValueError('confidence must be a string')
    confidence = confidence_value.strip().lower()
    if relation not in RELATION_TYPES:
        raise ValueError('unsupported relationship type')
    if not source_key or not target_key or not _valid_http_url(evidence):
        raise ValueError('relationship requires from/to keys and evidence')
    if confidence not in CONFIDENCE:
        raise ValueError('unsupported confidence')
    award_value = record.get('AwardID', '')
    if not isinstance(award_value, str):
        raise ValueError('AwardID must be a string')
    award_id = award_value.strip()
    if confidence == 'confirmed' and relation == 'funded_by_award' and not award_id:
        raise ValueError('confirmed award relationship requires AwardID')
    review_value = record.get('ReviewStatus', 'Needs Review')
    if not isinstance(review_value, str):
        raise ValueError('ReviewStatus must be a string')
    review_status = review_value.strip() or 'Needs Review'
    if review_status not in REVIEW_STATUSES:
        raise ValueError('unsupported review status')
    basis = '|'.join((relation, source_key, target_key, award_id, evidence))
    return {
        'RelationshipKey': 'REL:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24],
        'RelationshipType': relation,
        'FromKey': source_key,
        'ToKey': target_key,
        'AwardID': award_id,
        'EvidenceURL': evidence,
        'Confidence': confidence,
        'ReviewStatus': review_status,
    }
