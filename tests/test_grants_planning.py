import unittest
import hashlib
import json
from pathlib import Path
try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # Optional test extra; runtime has no third-party dependencies.
    Draft202012Validator = FormatChecker = None
from scripts.grants_planning import (
    delivery_event_key, institutional_deadline, institutional_policy_status,
    reconcile_institutional_override_history, subscribers, validate_policy,
)
from scripts.grants_registry import normalize_opportunity


SYNTHETIC_HOLIDAY_COVERAGE = {
    'CalendarVersion': 'qld-2026',
    'SourceID': 'fixture:holidays-2026',
    'SourceURL': 'https://example.org/holidays/2026',
    'ObservedAtUTC': '2026-01-01T00:00:00Z',
    'CoverageStart': '2026-01-01',
    'CoverageEnd': '2026-12-31',
    'CoverageVerified': True,
    'EvidenceSHA256': '0' * 64,
}


class PlanningTests(unittest.TestCase):
    def _override(self, revision=1, *, anchor_key='deadline:close', anchor_date='2026-10-15',
                  policy_key='CHHHS-DEFAULT', policy_version='1', calculated='2026-10-10',
                  override_date='2026-10-08', status='Reviewed', recorded=None):
        basis = json.dumps([anchor_key, policy_key, policy_version, revision],
                           separators=(',', ':'))
        return {
            'OverrideKey': 'OVERRIDE:' + hashlib.sha256(basis.encode()).hexdigest()[:24],
            'OverrideRevision': revision,
            'AnchorDeadlineKey': anchor_key,
            'AnchorDate': anchor_date,
            'AnchorPrecision': 'day',
            'PolicyKey': policy_key,
            'PolicyVersion': policy_version,
            'CalculatedDate': calculated,
            'OverrideDate': override_date,
            'OverrideReason': f'Synthetic reviewer reason {revision}',
            'ReviewStatus': status,
            'RecordedAtUTC': recorded or f'2026-10-0{revision}T00:00:00Z',
        }

    def _calendar_policy(self, **changes):
        return {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                'AnchorKind': 'final', 'LeadDays': 5, 'CalendarOrBusinessDays': 'calendar',
                'HolidayCalendarVersion': 'qld-2026', 'EffectiveFrom': '2026-01-01',
                **changes}

    def test_override_history_is_append_only_revisioned_and_keeps_official_anchor(self):
        anchor = {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
                  'Precision': 'day', 'Cancelled': False}
        history = [self._override(1), self._override(2, override_date='2026-10-07')]
        before = json.loads(json.dumps(history))
        result = reconcile_institutional_override_history(
            history, current_anchor=anchor, current_policy=self._calendar_policy(),
            as_of='2026-10-03')
        self.assertEqual(history, before)
        self.assertEqual([row['SupersededByRevision'] for row in result], [2, None])
        self.assertTrue(all(row['MatchesCurrentInputs'] for row in result))
        self.assertTrue(all(row['ReviewStatusIsReviewed'] for row in result))
        self.assertEqual(result[1]['OfficialAnchorDateCurrent'], '2026-10-15')
        self.assertEqual(result[1]['CurrentCalculatedDate'], '2026-10-10')
        self.assertFalse(result[1]['Stale'])
        self.assertNotIn('Approved', str(result))

    def test_override_becomes_stale_when_source_anchor_or_policy_changes(self):
        row = self._override()
        anchor = {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-16',
                  'Precision': 'day', 'Cancelled': False}
        policy = self._calendar_policy(Version='2')
        result = reconcile_institutional_override_history(
            [row], current_anchor=anchor, current_policy=policy, as_of='2026-10-03')
        self.assertTrue(result[0]['Stale'])
        self.assertEqual(result[0]['StaleReasons'], [
            'source_anchor_date_changed', 'policy_version_changed', 'calculated_date_changed'])
        self.assertEqual(result[0]['OverrideDate'], '2026-10-08')

    def test_policy_version_history_is_retained_as_separate_stale_revision_group(self):
        anchor = {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
                  'Precision': 'day', 'Cancelled': False}
        history = [self._override(1, policy_version='1'),
                   self._override(1, policy_version='2')]
        result = reconcile_institutional_override_history(
            history, current_anchor=anchor, current_policy=self._calendar_policy(Version='2'),
            as_of='2026-10-03')
        by_version = {row['PolicyVersion']: row for row in result}
        self.assertTrue(by_version['1']['Stale'])
        self.assertIn('policy_version_changed', by_version['1']['StaleReasons'])
        self.assertTrue(by_version['2']['MatchesCurrentInputs'])

    def test_override_is_stale_for_expired_policy_cancelled_or_uncertain_anchor(self):
        row = self._override()
        policy = self._calendar_policy(EffectiveTo='2026-10-02')
        for anchor in (
            {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
             'Precision': 'day', 'Cancelled': True},
            {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
             'Precision': 'month', 'Cancelled': False},
        ):
            result = reconcile_institutional_override_history(
                [row], current_anchor=anchor, current_policy=policy, as_of='2026-10-03')
            self.assertTrue(result[0]['Stale'])
            self.assertIn('policy_expired', result[0]['StaleReasons'])

    def test_incomplete_duplicate_or_rebound_override_history_fails_closed(self):
        anchor = {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
                  'Precision': 'day', 'Cancelled': False}
        policy = self._calendar_policy()
        cases = (
            ([self._override(2)], 'contiguous revision'),
            ([self._override(), self._override()], 'duplicate identities'),
            ([{**self._override(), 'OverrideKey': 'OVERRIDE:forged'}], 'typed history identity'),
            ([{**self._override(), 'Unknown': 'ignored'}], 'exact history contract'),
            ([{**self._override(), 'RecordedAtUTC': '2026-10-01T00:00:00'}], 'timezone-aware'),
            ([{**self._override(), 'RecordedAtUTC': '2026-10-01T00:00:00+10:00'}], 'UTC offset'),
            ([{**self._override(), 'AnchorPrecision': ['day']}], 'AnchorPrecision is unsupported'),
        )
        for rows, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                reconcile_institutional_override_history(
                    rows, current_anchor=anchor, current_policy=policy, as_of='2026-10-03')

    @unittest.skipIf(Draft202012Validator is None, 'optional jsonschema package is not installed')
    def test_g08_json_schemas_match_policy_and_override_runtime_contracts(self):
        root = Path(__file__).resolve().parents[1]
        policy_schema = json.loads((root / 'contracts/g08-institutional-date-policy.schema.json').read_text())
        override_schema = json.loads((root / 'contracts/g08-institutional-deadline-override.schema.json').read_text())
        Draft202012Validator.check_schema(policy_schema)
        Draft202012Validator.check_schema(override_schema)
        policy_validator = Draft202012Validator(policy_schema, format_checker=FormatChecker())
        override_validator = Draft202012Validator(override_schema, format_checker=FormatChecker())

        policy = self._calendar_policy()
        self.assertTrue(validate_policy(policy))
        self.assertEqual(list(policy_validator.iter_errors(policy)), [])
        for invalid in ({**policy, 'EffectiveUntil': '2026-12-31'},
                        {**policy, 'LeadDays': True},
                        {**policy, 'EffectiveTo': '2026-02-30'},
                        {**policy, 'HolidayCoverage': {'ObservedAtUtc': '2026-01-01T00:00:00Z'}}):
            self.assertFalse(validate_policy(invalid))
            self.assertTrue(list(policy_validator.iter_errors(invalid)))
        business_policy = self._calendar_policy(
            CalendarOrBusinessDays='business', HolidayDates=['2026-01-26'],
            HolidayCoverage=SYNTHETIC_HOLIDAY_COVERAGE)
        self.assertTrue(validate_policy(business_policy))
        self.assertEqual(list(policy_validator.iter_errors(business_policy)), [])

        override = self._override()
        self.assertEqual(list(override_validator.iter_errors(override)), [])
        anchor = {'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
                  'Precision': 'day', 'Cancelled': False}
        self.assertEqual(len(reconcile_institutional_override_history(
            [override], current_anchor=anchor, current_policy=policy,
            as_of='2026-10-03')), 1)
        for invalid in ({**override, 'Unknown': 'ignored'},
                        {**override, 'OverrideRevision': True},
                        {**override, 'RecordedAtUTC': '2026-10-01T00:00:00+10:00'}):
            self.assertTrue(list(override_validator.iter_errors(invalid)))

    def test_unreviewed_override_is_never_reported_as_reviewed_or_accepted(self):
        row = self._override(status='Needs Review')
        result = reconcile_institutional_override_history(
            [row], current_anchor={'DeadlineKey': 'deadline:close', 'LocalDate': '2026-10-15',
                                   'Precision': 'day', 'Cancelled': False},
            current_policy=self._calendar_policy(), as_of='2026-10-03')
        self.assertTrue(result[0]['MatchesCurrentInputs'])
        self.assertFalse(result[0]['ReviewStatusIsReviewed'])
        self.assertNotIn('Applied', str(result[0]))

    def test_business_days_skip_supplied_holidays(self):
        self.assertEqual(institutional_deadline('2026-09-28', 1, holidays=['2026-09-25']), '2026-09-24')

    def test_unknown_precision_does_not_invent_deadline(self):
        self.assertIsNone(institutional_deadline('2026-09', 5))

    def test_calendar_boundary_underflow_is_an_unknown_projection(self):
        self.assertIsNone(institutional_deadline(
            '0001-01-01', 1, business_days=False))
        self.assertIsNone(institutional_deadline(
            '0001-01-01', 1, holidays=[]))

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            institutional_deadline('2026-09-28', -1)

    def test_policy_effective_window_is_validated_and_classified(self):
        policy = {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                  'AnchorKind': 'final', 'LeadDays': 10, 'CalendarOrBusinessDays': 'business',
                  'HolidayCalendarVersion': 'qld-2026', 'HolidayDates': ['2026-01-26'],
                  'HolidayCoverage': SYNTHETIC_HOLIDAY_COVERAGE, 'EffectiveFrom': '2026-01-01',
                  'EffectiveTo': '2026-09-24'}
        self.assertTrue(validate_policy(policy))
        self.assertEqual(institutional_policy_status(policy, '2025-12-31'), 'future')
        self.assertEqual(institutional_policy_status(policy, '2026-09-24'), 'current')
        self.assertEqual(institutional_policy_status(policy, '2026-09-25'), 'expired')
        self.assertEqual(institutional_policy_status(policy, '2026-02-30'), 'invalid')
        for invalid in ({**policy, 'EffectiveFrom': '2026-02-30'},
                        {**policy, 'EffectiveTo': '2025-12-31'}):
            self.assertFalse(validate_policy(invalid))

    def test_policy_identity_fields_and_explicit_end_date_fail_closed(self):
        policy = {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                  'AnchorKind': 'final', 'LeadDays': 10, 'CalendarOrBusinessDays': 'business',
                  'HolidayCalendarVersion': 'qld-2026', 'HolidayDates': ['2026-01-26'],
                  'HolidayCoverage': SYNTHETIC_HOLIDAY_COVERAGE, 'EffectiveFrom': '2026-01-01'}
        for field, value in (('PolicyKey', []), ('Version', 1), ('OrganisationKey', False),
                             ('AnchorKind', {}), ('HolidayCalendarVersion', '  '),
                             ('EffectiveFrom', 20260101), ('EffectiveTo', '')):
            with self.subTest(field=field, value=value):
                self.assertFalse(validate_policy({**policy, field: value}))

    def test_policy_rejects_unknown_or_misspelled_fields(self):
        policy = {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                  'AnchorKind': 'final', 'LeadDays': 10, 'CalendarOrBusinessDays': 'calendar',
                  'HolidayCalendarVersion': 'qld-2026', 'EffectiveFrom': '2026-01-01',
                  'EffectiveTo': '2026-12-31'}
        for field in ('EffectiveUntil', 'HolidayCalendarVer', 'Timezone'):
            with self.subTest(field=field):
                self.assertFalse(validate_policy({**policy, field: 'ignored'}))

    def test_business_day_policy_requires_well_formed_holiday_calendar(self):
        policy = {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                  'AnchorKind': 'final', 'LeadDays': 10, 'CalendarOrBusinessDays': 'business',
                  'HolidayCalendarVersion': 'qld-2026', 'HolidayDates': ['2026-01-26'],
                  'HolidayCoverage': SYNTHETIC_HOLIDAY_COVERAGE,
                  'EffectiveFrom': '2026-01-01'}
        malformed = (
            {key: value for key, value in policy.items() if key != 'HolidayDates'},
            {**policy, 'HolidayDates': '2026-01-26'},
            {**policy, 'HolidayDates': ['2026-02-30']},
            {**policy, 'HolidayDates': ['2026-01-26', '2026-01-26']},
            {**policy, 'HolidayDates': [20260126]},
        )
        self.assertTrue(validate_policy(policy))
        incomplete_coverage = {**policy, 'HolidayCoverage': {**SYNTHETIC_HOLIDAY_COVERAGE,
                                                              'CoverageVerified': False}}
        missing_coverage = {key: value for key, value in policy.items() if key != 'HolidayCoverage'}
        bad_hash = {**policy, 'HolidayCoverage': {**SYNTHETIC_HOLIDAY_COVERAGE,
                                                  'EvidenceSHA256': 'bad'}}
        misspelled_coverage = {**policy, 'HolidayCoverage': {
            **SYNTHETIC_HOLIDAY_COVERAGE, 'ObservedAtUtc': '2026-01-01T00:00:00Z'}}
        self.assertFalse(validate_policy(incomplete_coverage))
        self.assertFalse(validate_policy(missing_coverage))
        self.assertFalse(validate_policy(bad_hash))
        self.assertFalse(validate_policy(misspelled_coverage))
        self.assertFalse(validate_policy({**policy, 'HolidayDates': ['2025-12-31']}))
        for url in ('https://example.org:bad/holidays', 'https://example.org:65536/holidays',
                    'https://example.org:0/holidays'):
            with self.subTest(url=url):
                invalid_url = {**policy, 'HolidayCoverage': {
                    **SYNTHETIC_HOLIDAY_COVERAGE, 'SourceURL': url}}
                self.assertFalse(validate_policy(invalid_url))
        for candidate in malformed:
            with self.subTest(candidate=candidate):
                self.assertFalse(validate_policy(candidate))

    def test_calendar_day_policy_does_not_require_unused_holiday_dates(self):
        policy = {'PolicyKey': 'CHHHS-DEFAULT', 'Version': '1', 'OrganisationKey': 'CHHHS',
                  'AnchorKind': 'final', 'LeadDays': 10, 'CalendarOrBusinessDays': 'calendar',
                  'HolidayCalendarVersion': 'qld-2026', 'EffectiveFrom': '2026-01-01'}
        self.assertTrue(validate_policy(policy))

    def test_direct_business_day_calculation_rejects_malformed_holidays(self):
        for holidays in ('2026-01-26', ['2026-02-30'], ['2026-01-26', '2026-01-26']):
            with self.subTest(holidays=holidays), self.assertRaises(ValueError):
                institutional_deadline('2026-01-28', 1, holidays=holidays)
        with self.assertRaisesRegex(ValueError, 'explicit holiday calendar'):
            institutional_deadline('2026-01-28', 1)

    def test_overlapping_subscriptions_deduplicate_and_respect_pause(self):
        grant = {'OpportunityKey': 'g1', 'CategoryKeys': ['health']}
        rules = [
            {'UserKey': 'u1', 'Active': True, 'Scope': 'category', 'TargetKey': 'health'},
            {'UserKey': 'u1', 'Active': True, 'Scope': 'opportunity', 'TargetKey': 'g1'},
            {'UserKey': 'u2', 'Active': False, 'Scope': 'opportunity', 'TargetKey': 'g1'},
        ]
        self.assertEqual(subscribers(grant, rules), ['u1'])

    def test_subscription_candidate_matching_rejects_malformed_categories_and_preferences(self):
        rule = {'UserKey': 'u1', 'Active': True, 'Scope': 'category', 'TargetKey': 'h'}
        for categories in ('health', ['health', 7], [' health']):
            with self.subTest(categories=categories), self.assertRaisesRegex(
                    ValueError, 'CategoryKeys'):
                subscribers({'OpportunityKey': 'g1', 'CategoryKeys': categories}, [rule])
        for active, scope in (('true', 'category'), (True, 'unknown'), (True, [])):
            with self.subTest(active=active, scope=scope), self.assertRaises(ValueError):
                subscribers({'OpportunityKey': 'g1', 'CategoryKeys': ['h']},
                            [{**rule, 'Active': active, 'Scope': scope}])

    def test_subscription_candidate_matching_requires_canonical_opportunity_key(self):
        with self.assertRaisesRegex(ValueError, 'OpportunityKey'):
            subscribers({'OpportunityKey': ' g1 '}, [])

    def test_active_subscription_with_stale_target_fails_closed(self):
        grant = {'OpportunityKey': 'g1', 'CategoryKeys': ['health']}
        stale_rules = [
            {'UserKey': 'u1', 'Active': True, 'Scope': 'opportunity', 'TargetKey': 'deleted-grant'},
            {'UserKey': 'u1', 'Active': True, 'Scope': 'category', 'TargetKey': 'stale-category'},
            {'UserKey': 'u1', 'Active': True, 'Scope': 'funder', 'TargetKey': 'unknown-funder'},
        ]
        for rule in stale_rules:
            with self.subTest(scope=rule['Scope']), self.assertRaisesRegex(ValueError, 'candidate set'):
                subscribers(grant, [rule])

    def test_delivery_event_key_distinguishes_zero_missing_and_delimited_fields(self):
        base = ('u', 'g', 'deadline', 'r1')
        self.assertNotEqual(delivery_event_key(*base, 0, 'email'),
                            delivery_event_key(*base, None, 'email'))
        self.assertNotEqual(
            delivery_event_key('u|g', 'x', 'deadline', 'r1', 10, 'email'),
            delivery_event_key('u', 'g|x', 'deadline', 'r1', 10, 'email'),
        )

    def test_delivery_event_key_rejects_malformed_identity_fields(self):
        valid = ('u', 'g', 'deadline', 'r1', 10, 'email')
        for index, value in ((0, ''), (1, None), (2, ' deadline'), (3, 1), (5, 'email ')):
            candidate = list(valid)
            candidate[index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                delivery_event_key(*candidate)
        for offset in (True, 1.0, '10'):
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, 'offset_days'):
                delivery_event_key('u', 'g', 'deadline', 'r1', offset, 'email')

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
