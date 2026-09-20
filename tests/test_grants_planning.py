import unittest
from scripts.grants_planning import institutional_deadline, subscribers, validate_policy
from scripts.grants_registry import normalize_opportunity


class PlanningTests(unittest.TestCase):
    def test_business_days_skip_supplied_holidays(self):
        self.assertEqual(institutional_deadline('2026-09-28', 1, holidays=['2026-09-25']), '2026-09-24')

    def test_unknown_precision_does_not_invent_deadline(self):
        self.assertIsNone(institutional_deadline('2026-09', 5))

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            institutional_deadline('2026-09-28', -1)

    def test_policy_rejects_reversed_effective_range_and_bad_holiday(self):
        policy = {
            'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1.0', 'OrganisationKey': 'CHHHS',
            'AnchorKind': 'application_close', 'LeadDays': 10,
            'CalendarOrBusinessDays': 'business', 'HolidayCalendarVersion': 'qld-2026',
            'EffectiveFrom': '2026-01-01', 'EffectiveTo': '2026-12-31',
        }
        reversed_policy = {**policy, 'EffectiveTo': '2025-12-31'}
        self.assertFalse(validate_policy(reversed_policy))
        bad_holiday = {**policy, 'HolidayDates': ['2026-02-30']}
        self.assertFalse(validate_policy(bad_holiday))

    def test_overlapping_subscriptions_deduplicate_and_respect_pause(self):
        grant = {'OpportunityKey': 'g1', 'CategoryKeys': ['health']}
        rules = [
            {'UserKey': 'u1', 'Active': True, 'Scope': 'category', 'TargetKey': 'health'},
            {'UserKey': 'u1', 'Active': True, 'Scope': 'opportunity', 'TargetKey': 'g1'},
            {'UserKey': 'u2', 'Active': False, 'Scope': 'opportunity', 'TargetKey': 'g1'},
        ]
        self.assertEqual(subscribers(grant, rules), ['u1'])

    def test_malformed_subscription_rule_fails_closed(self):
        with self.assertRaises(ValueError):
            subscribers({'OpportunityKey': 'g1'}, [{'UserKey': 'u1', 'Active': True, 'Scope': 'unknown', 'TargetKey': 'g1'}])
        with self.assertRaises(ValueError):
            subscribers({'OpportunityKey': 'g1'}, [{'UserKey': 'u1', 'Active': 'yes', 'Scope': 'opportunity', 'TargetKey': 'g1'}])

    def test_subscription_matching_requires_opportunity_identity(self):
        with self.assertRaises(ValueError):
            subscribers({}, [])

    def test_alias_input_has_same_identity(self):
        a = normalize_opportunity({'title': 'Call', 'link': 'https://example.org/call'})
        b = normalize_opportunity({'Title': 'Call', 'URL': 'https://example.org/call'})
        self.assertEqual(a['OpportunityKey'], b['OpportunityKey'])

    def test_impossible_deadline_is_unknown(self):
        self.assertEqual(normalize_opportunity({'Deadline': '2027-02-30'})['DeadlinePrecision'], 'unknown')

    def test_rounds_do_not_merge(self):
        a = {'Source': 'f', 'SourceID': 'scheme', 'RoundID': '2026'}
        b = {**a, 'RoundID': '2027'}
        self.assertNotEqual(normalize_opportunity(a)['OpportunityKey'], normalize_opportunity(b)['OpportunityKey'])
