import unittest
import json
from pathlib import Path

from scripts.grants_operations import evaluate_run
from scripts.grants_planning import delivery_event_key, validate_policy
from scripts.grants_relationships import normalize_relationship


class GrantsRelationshipTests(unittest.TestCase):
    def test_relationship_schema_matches_normalized_projection(self):
        schema = json.loads((Path(__file__).parents[1] / 'config/grant-relationships.schema.json').read_text())
        row = normalize_relationship({'RelationshipType':'funded_by_award','FromKey':'GRANT:1','ToKey':'PUB:1','AwardID':'MRFF-1','EvidenceURL':'https://evidence','Confidence':'confirmed'})
        self.assertEqual(schema['identity_field'], 'RelationshipKey')
        self.assertEqual({f['display_name'] for f in schema['fields']}, set(row))
        self.assertEqual(schema['list_name'], 'Grant Relationships')

    def test_confirmed_award_requires_exact_award_id(self):
        with self.assertRaises(ValueError):
            normalize_relationship({'RelationshipType':'funded_by_award','FromKey':'GRANT:1','ToKey':'PUB:1','EvidenceURL':'https://evidence','Confidence':'confirmed'})
        row = normalize_relationship({'RelationshipType':'funded_by_award','FromKey':'GRANT:1','ToKey':'PUB:1','AwardID':'MRFF-1','EvidenceURL':'https://evidence','Confidence':'confirmed'})
        self.assertTrue(row['RelationshipKey'].startswith('REL:'))

    def test_topic_relevance_is_not_promoted_to_funding(self):
        row = normalize_relationship({'RelationshipType':'relevant_to_opportunity','FromKey':'PUB:1','ToKey':'GRANT:1','EvidenceURL':'https://evidence','Confidence':'candidate'})
        self.assertEqual(row['RelationshipType'], 'relevant_to_opportunity')
        self.assertEqual(row['Confidence'], 'candidate')

    def test_relationship_requires_http_evidence_url(self):
        with self.assertRaisesRegex(ValueError, 'requires from/to keys and evidence'):
            normalize_relationship({'RelationshipType':'relevant_to_opportunity','FromKey':'PUB:1','ToKey':'GRANT:1','EvidenceURL':'evidence','Confidence':'candidate'})

    def test_relationship_review_status_is_constrained(self):
        with self.assertRaisesRegex(ValueError, 'unsupported review status'):
            normalize_relationship({'RelationshipType':'relevant_to_opportunity','FromKey':'PUB:1','ToKey':'GRANT:1','EvidenceURL':'https://evidence','Confidence':'candidate','ReviewStatus':'Reviewed'})

    def test_run_rejects_failed_source_and_preserves_last_batch(self):
        result = evaluate_run([{'OpportunityKey':'GRANT:1'}], [{'source':'nhmrc','status':'failed'}], [{'OpportunityKey':'GRANT:old'}])
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['records'], [{'OpportunityKey':'GRANT:old'}])

    def test_run_rejects_missing_source_health(self):
        result = evaluate_run([{'OpportunityKey':'GRANT:1', 'Source':'nhmrc'}], [], [{'OpportunityKey':'GRANT:old'}])
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('missing_source_health', result['errors'])

    def test_run_rejects_record_from_unreported_source(self):
        result = evaluate_run(
            [{'OpportunityKey':'GRANT:1', 'Source':'mrff'}],
            [{'source':'nhmrc', 'status':'succeeded'}],
        )
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('unreported_source', result['errors'])

    def test_policy_and_delivery_keys_are_versioned(self):
        policy = {'PolicyKey':'CHHHS-DEFAULT','Version':'1.0','OrganisationKey':'CHHHS','AnchorKind':'final','LeadDays':10,'CalendarOrBusinessDays':'business','HolidayCalendarVersion':'qld-2026','EffectiveFrom':'2026-01-01'}
        self.assertTrue(validate_policy(policy))
        self.assertEqual(delivery_event_key('u','g','new','1',10,'email'), delivery_event_key('u','g','new','1',10,'email'))


if __name__ == '__main__':
    unittest.main()
