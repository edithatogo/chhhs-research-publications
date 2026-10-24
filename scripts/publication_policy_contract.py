"""Publication inclusion-policy validation shared by offline comparators.

Extracted unchanged from the qualified publication policy; no enrichment import.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/publication-policy.json"


def load_policy(path=POLICY_PATH):
    policy = json.loads(Path(path).read_text())
    return validate_policy(policy)

def validate_policy(policy):
    expected = {'version', 'inclusion', 'retention', 'default_projection', 'uncertain_affiliation',
                'ambiguous_identity', 'source_disappearance', 'corrections_and_retractions',
                'fuzzy_names', 'manual_record_approval'}
    if set(policy) != expected or not isinstance(policy['version'], str) or not policy['version'].strip():
        raise ValueError('Invalid publication policy schema')
    required = {'inclusion': 'all-valid-configured-source-records',
                'retention': 'every-observation-and-version', 'default_projection': 'latest-valid-version',
                'uncertain_affiliation': 'include-with-label', 'ambiguous_identity': 'preserve-separate-source-records',
                'source_disappearance': 'retain-last-good', 'corrections_and_retractions': 'retain-and-label',
                'fuzzy_names': 'candidate-signal-only', 'manual_record_approval': False}
    if any(type(policy[k]) is not type(v) or policy[k] != v for k, v in required.items()):
        raise ValueError('Unsupported policy behaviour; implement changes before selecting them')
    return policy
