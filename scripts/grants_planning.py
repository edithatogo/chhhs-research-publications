"""Local reference logic for institutional dates and subscription matching.

No tenant writes, calendar invitations or notifications. Holiday coverage and
institutional lead times must be supplied by a versioned institutional policy.
"""
from datetime import date, datetime, timedelta
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from copy import deepcopy
from urllib.parse import urlsplit

from scripts.grants_registry import parse_offset_instant


def institutional_deadline(external_date, lead_days, *, business_days=True, holidays=None):
    """Return a proposed date; partial/unknown source dates remain unknown."""
    if type(lead_days) is not int or not 0 <= lead_days <= 3660:
        raise ValueError('Lead days must be an integer from zero to 3660')
    if type(business_days) is not bool:
        raise ValueError('Business day policy must be boolean')
    if not isinstance(external_date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', external_date):
        return None
    try:
        target = date.fromisoformat(external_date)
    except ValueError:
        return None
    if business_days and holidays is None:
        raise ValueError('Business day calculation requires an explicit holiday calendar')
    if holidays is None:
        holidays = ()
    excluded = _holiday_dates(holidays)
    remaining = lead_days
    while remaining:
        try:
            target -= timedelta(days=1)
        except OverflowError:
            # A representational boundary cannot produce a defensible date.
            # Keep the batch moving by treating this projection as unknown.
            return None
        if not business_days or (target.weekday() < 5 and target not in excluded):
            remaining -= 1
    return target.isoformat()


def subscribers(opportunity, subscriptions):
    """Return unique candidate user keys from structurally valid inputs only.

    This is a matching preview, not authorization to send. Active preferences
    must be re-read and access/consent checked at the delivery boundary.
    """
    if not isinstance(opportunity, Mapping):
        raise ValueError('opportunity must be an object')
    opportunity_key = opportunity.get('OpportunityKey')
    if (not isinstance(opportunity_key, str) or not opportunity_key
            or opportunity_key != opportunity_key.strip()):
        raise ValueError('OpportunityKey must be nonblank text without outer whitespace')
    raw_categories = opportunity.get('CategoryKeys', [])
    if raw_categories is None:
        raw_categories = []
    if not isinstance(raw_categories, (list, tuple)):
        raise ValueError('CategoryKeys must be a list or tuple of nonblank text keys')
    categories = set()
    for category in raw_categories:
        if (not isinstance(category, str) or not category
                or category != category.strip()):
            raise ValueError('CategoryKeys must contain nonblank text keys without outer whitespace')
        categories.add(category)
    funder_key = opportunity.get('FunderKey')
    if funder_key is not None and (
            not isinstance(funder_key, str) or not funder_key
            or funder_key != funder_key.strip()):
        raise ValueError('FunderKey must be null or nonblank text without outer whitespace')

    targets = {
        'opportunity': {opportunity_key},
        'category': categories,
        'funder': {funder_key} if funder_key is not None else set(),
    }
    if (isinstance(subscriptions, (str, bytes, Mapping))
            or not isinstance(subscriptions, Iterable)):
        raise ValueError('subscriptions must be a collection of preference objects')
    candidates = set()
    for index, rule in enumerate(subscriptions, 1):
        if not isinstance(rule, Mapping):
            raise ValueError(f'subscription {index} must be an object')
        active = rule.get('Active')
        if type(active) is not bool:
            raise ValueError(f'subscription {index} Active must be boolean')
        if not active:
            continue
        user_key = rule.get('UserKey')
        scope = rule.get('Scope')
        target_key = rule.get('TargetKey')
        if (not isinstance(user_key, str) or not user_key
                or user_key != user_key.strip()):
            raise ValueError(f'subscription {index} UserKey must be nonblank text without outer whitespace')
        if not isinstance(scope, str) or scope not in targets:
            raise ValueError(f'subscription {index} Scope is unsupported')
        if (not isinstance(target_key, str) or not target_key
                or target_key != target_key.strip()):
            raise ValueError(f'subscription {index} TargetKey must be nonblank text without outer whitespace')
        # A key that cannot exist in the canonical candidate vocabulary usually
        # signals stale or mistyped configuration. Fail closed instead of
        # silently presenting an apparently healthy empty match.
        if target_key not in targets[scope]:
            raise ValueError(f'subscription {index} TargetKey is not present in the opportunity candidate set')
        if target_key in targets[scope]:
            candidates.add(user_key)
    return sorted(candidates)


def validate_policy(policy):
    """Validate a versioned institutional date policy without approving it."""
    if not isinstance(policy, dict):
        return False
    # Reject misspelled or unsupported fields. Silently ignoring a typo such as
    # ``EffectiveUntil`` could make a bounded policy appear open-ended/current.
    allowed = {'PolicyKey', 'Version', 'OrganisationKey', 'AnchorKind', 'LeadDays',
               'CalendarOrBusinessDays', 'HolidayCalendarVersion', 'HolidayDates',
               'HolidayCoverage', 'EffectiveFrom', 'EffectiveTo'}
    if set(policy) - allowed:
        return False
    required = ('PolicyKey', 'Version', 'OrganisationKey', 'AnchorKind', 'LeadDays',
                'HolidayCalendarVersion', 'EffectiveFrom')
    text_fields = ('PolicyKey', 'Version', 'OrganisationKey', 'AnchorKind',
                   'HolidayCalendarVersion')
    if not all(isinstance(policy.get(key), str)
               and policy[key]
               and policy[key] == policy[key].strip()
               for key in text_fields):
        return False
    if policy.get('EffectiveFrom') in (None, ''):
        return False
    if type(policy['LeadDays']) is not int or not 0 <= policy['LeadDays'] <= 3660:
        return False
    if policy.get('CalendarOrBusinessDays') not in ('calendar', 'business'):
        return False
    if ('HolidayCoverage' in policy
            and not _holiday_coverage_is_valid(
                policy.get('HolidayCoverage'), policy['HolidayCalendarVersion'])):
        return False
    if policy.get('CalendarOrBusinessDays') == 'business':
        if ('HolidayDates' not in policy
                or not _holiday_coverage_is_valid(
                    policy.get('HolidayCoverage'), policy['HolidayCalendarVersion'])):
            return False
    if 'HolidayDates' in policy:
        try:
            holiday_dates = _holiday_dates(policy['HolidayDates'])
        except (TypeError, ValueError):
            return False
        if policy.get('CalendarOrBusinessDays') == 'business':
            coverage_start, coverage_end = _holiday_coverage_dates(policy['HolidayCoverage'])
            if any(day < coverage_start or day > coverage_end for day in holiday_dates):
                return False
    effective_from = _policy_date(policy['EffectiveFrom'])
    if effective_from is None:
        return False
    if 'EffectiveTo' in policy and policy['EffectiveTo'] is not None:
        effective_to = _policy_date(policy['EffectiveTo'])
        if effective_to is None or effective_to < effective_from:
            return False
    return True


def _holiday_coverage_is_valid(value, calendar_version):
    """Require traceable, verified coverage metadata for business calendars.

    A holiday list alone cannot show whether an empty or truncated list is
    complete. The versioned coverage record identifies the source capture and
    its claimed interval; authoritative source review remains an operational
    acceptance gate.
    """
    if not isinstance(value, Mapping):
        return False
    allowed = {'CalendarVersion', 'SourceID', 'SourceURL', 'ObservedAtUTC',
               'CoverageStart', 'CoverageEnd', 'CoverageVerified', 'EvidenceSHA256'}
    if set(value) - allowed:
        return False
    source_id = value.get('SourceID')
    source_url = value.get('SourceURL')
    observed = value.get('ObservedAtUTC')
    evidence_hash = value.get('EvidenceSHA256')
    if (value.get('CalendarVersion') != calendar_version
            or not isinstance(source_id, str) or not source_id or source_id != source_id.strip()
            or not isinstance(source_url, str) or source_url != source_url.strip()
            or value.get('CoverageVerified') is not True
            or not isinstance(evidence_hash, str)
            or not re.fullmatch(r'[0-9a-f]{64}', evidence_hash)):
        return False
    try:
        parsed_url = urlsplit(source_url)
        if (parsed_url.scheme != 'https' or not parsed_url.hostname
                or parsed_url.username is not None or parsed_url.password is not None):
            return False
        port = parsed_url.port  # Access validates malformed and out-of-range ports.
        if port == 0:
            return False
        if not isinstance(observed, str) or not re.fullmatch(
                r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', observed):
            return False
        datetime.strptime(observed, '%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, TypeError):
        return False
    start = _policy_date(value.get('CoverageStart'))
    end = _policy_date(value.get('CoverageEnd'))
    return start is not None and end is not None and start <= end


def _holiday_coverage_dates(value):
    return _policy_date(value['CoverageStart']), _policy_date(value['CoverageEnd'])


def _holiday_dates(values):
    """Parse a supplied holiday calendar without coercion or silent deduping."""
    if not isinstance(values, (list, tuple)):
        raise ValueError('HolidayDates must be a list or tuple of unique ISO dates')
    parsed = []
    for value in values:
        day = _policy_date(value)
        if day is None:
            raise ValueError('HolidayDates must contain real YYYY-MM-DD dates')
        parsed.append(day)
    if len(parsed) != len(set(parsed)):
        raise ValueError('HolidayDates must not contain duplicates')
    return set(parsed)


def _policy_date(value):
    """Parse a strict policy date, rejecting impossible dates and timestamps."""
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def institutional_policy_status(policy, as_of):
    """Return current, future, expired or invalid for a policy on an ISO date.

    Expired policies remain valid historical records, but callers can expose
    their status as a stale flag and avoid applying them to new calculations.
    EffectiveTo is inclusive.
    """
    today = _policy_date(as_of)
    if today is None or not validate_policy(policy):
        return 'invalid'
    start = _policy_date(policy['EffectiveFrom'])
    end = _policy_date(policy['EffectiveTo']) if policy.get('EffectiveTo') else None
    if today < start:
        return 'future'
    if end is not None and today > end:
        return 'expired'
    return 'current'


def reconcile_institutional_override_history(history, *, current_anchor,
                                               current_policy, as_of):
    """Return immutable override-history rows annotated against current inputs.

    This is a local consistency projection, not policy approval or persistence.
    Every revision must be present and contiguous per anchor/policy so that a
    partial version history cannot be mistaken for the complete audit trail.
    """
    if isinstance(history, (str, bytes, Mapping)) or not isinstance(history, Iterable):
        raise ValueError('override history must be a collection of records')
    rows = list(history)
    anchor = _validate_override_anchor(current_anchor)
    if current_policy is not None and not validate_policy(current_policy):
        raise ValueError('current institutional policy is invalid')
    as_of_date = _policy_date(as_of)
    if as_of_date is None:
        raise ValueError('as_of must be a real YYYY-MM-DD date')
    policy_status = (institutional_policy_status(current_policy, as_of_date.isoformat())
                     if current_policy is not None else 'missing')
    current_calculated = _current_institutional_date(anchor, current_policy, policy_status)

    required = {
        'OverrideKey', 'OverrideRevision', 'AnchorDeadlineKey', 'AnchorDate',
        'AnchorPrecision', 'PolicyKey', 'PolicyVersion', 'CalculatedDate',
        'OverrideDate', 'OverrideReason', 'ReviewStatus', 'RecordedAtUTC',
    }
    groups: dict[tuple[str, str, str], list[dict]] = {}
    seen_keys: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != required:
            raise ValueError('override record fields do not match the exact history contract')
        for field in ('OverrideKey', 'AnchorDeadlineKey', 'PolicyKey', 'PolicyVersion',
                      'OverrideReason', 'ReviewStatus'):
            value = row[field]
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f'{field} must be nonblank text without outer whitespace')
        revision = row['OverrideRevision']
        if type(revision) is not int or revision < 1:
            raise ValueError('OverrideRevision must be a positive integer')
        for field in ('AnchorDate', 'CalculatedDate', 'OverrideDate'):
            if _policy_date(row[field]) is None:
                raise ValueError(f'{field} must be a real YYYY-MM-DD date')
        try:
            recorded = parse_offset_instant(row['RecordedAtUTC'])
        except ValueError as exc:
            raise ValueError('RecordedAtUTC must be a timezone-aware RFC3339 instant') from exc
        if recorded.utcoffset() != timedelta(0):
            raise ValueError('RecordedAtUTC must use the UTC offset')
        if (not isinstance(row['AnchorPrecision'], str)
                or row['AnchorPrecision'] not in {'day', 'month', 'quarter', 'year', 'unknown'}):
            raise ValueError('AnchorPrecision is unsupported')
        basis = json.dumps([row['AnchorDeadlineKey'], row['PolicyKey'],
                            row['PolicyVersion'], revision],
                           ensure_ascii=False, separators=(',', ':'))
        expected_key = 'OVERRIDE:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24]
        if row['OverrideKey'] != expected_key:
            raise ValueError('OverrideKey does not match the typed history identity')
        if row['OverrideKey'] in seen_keys:
            raise ValueError('override history contains duplicate identities')
        seen_keys.add(row['OverrideKey'])
        groups.setdefault((row['AnchorDeadlineKey'], row['PolicyKey'], row['PolicyVersion']), []).append(
            {**dict(row), '_recorded': recorded}
        )

    assessed: list[dict] = []
    for (anchor_key, policy_key, _policy_version), entries in sorted(groups.items()):
        entries.sort(key=lambda entry: entry['OverrideRevision'])
        revisions = [entry['OverrideRevision'] for entry in entries]
        if revisions != list(range(1, len(revisions) + 1)):
            raise ValueError('override history must contain every contiguous revision from 1')
        if any(right['_recorded'] < left['_recorded']
               for left, right in zip(entries, entries[1:])):
            raise ValueError('override revision timestamps must be nondecreasing')
        latest_revision = revisions[-1]
        for entry in entries:
            row = {key: deepcopy(value) for key, value in entry.items() if key != '_recorded'}
            stale_reasons: list[str] = []
            if anchor is None:
                stale_reasons.append('current_anchor_missing')
            else:
                if anchor['DeadlineKey'] != anchor_key:
                    stale_reasons.append('source_anchor_changed')
                if anchor['LocalDate'] != row['AnchorDate']:
                    stale_reasons.append('source_anchor_date_changed')
                if anchor['Precision'] != row['AnchorPrecision']:
                    stale_reasons.append('source_anchor_precision_changed')
                if anchor['Cancelled']:
                    stale_reasons.append('source_anchor_cancelled')
            if current_policy is None:
                stale_reasons.append('current_policy_missing')
            else:
                if current_policy['PolicyKey'] != policy_key:
                    stale_reasons.append('policy_changed')
                if current_policy['Version'] != row['PolicyVersion']:
                    stale_reasons.append('policy_version_changed')
                if policy_status != 'current':
                    stale_reasons.append(f'policy_{policy_status}')
            if current_calculated != row['CalculatedDate']:
                stale_reasons.append('calculated_date_changed')
            row['SupersededByRevision'] = (
                latest_revision if row['OverrideRevision'] < latest_revision else None
            )
            row['Stale'] = bool(stale_reasons)
            row['StaleReasons'] = stale_reasons
            row['MatchesCurrentInputs'] = not stale_reasons
            row['ReviewStatusIsReviewed'] = row['ReviewStatus'].casefold() == 'reviewed'
            # The history records the proposed date; it never rewrites the
            # official anchor or asserts that the institution approved it.
            row['OfficialAnchorDateCurrent'] = anchor['LocalDate'] if anchor else None
            row['CurrentCalculatedDate'] = current_calculated
            row['CurrentPolicyStatus'] = policy_status
            assessed.append(row)
    return assessed


def _validate_override_anchor(value):
    if value is None:
        return None
    required = {'DeadlineKey', 'LocalDate', 'Precision', 'Cancelled'}
    if not isinstance(value, Mapping) or set(value) != required:
        raise ValueError('current anchor fields do not match the exact deadline contract')
    key = value['DeadlineKey']
    if not isinstance(key, str) or not key or key != key.strip():
        raise ValueError('current anchor DeadlineKey must be nonblank and unpadded')
    if (not isinstance(value['Precision'], str)
            or value['Precision'] not in {'day', 'month', 'quarter', 'year', 'unknown'}):
        raise ValueError('current anchor Precision is unsupported')
    if type(value['Cancelled']) is not bool:
        raise ValueError('current anchor Cancelled must be boolean')
    local_date = value['LocalDate']
    if local_date is not None and _policy_date(local_date) is None:
        raise ValueError('current anchor LocalDate must be null or a real YYYY-MM-DD date')
    return dict(value)


def _current_institutional_date(anchor, policy, policy_status):
    if (anchor is None or anchor['Cancelled'] or anchor['Precision'] != 'day'
            or anchor['LocalDate'] is None or policy is None or policy_status != 'current'):
        return None
    result = institutional_deadline(
        anchor['LocalDate'], policy['LeadDays'],
        business_days=policy['CalendarOrBusinessDays'] == 'business',
        holidays=policy.get('HolidayDates', ()),
    )
    if result is not None and policy['CalendarOrBusinessDays'] == 'business':
        coverage = policy['HolidayCoverage']
        if result < coverage['CoverageStart'] or anchor['LocalDate'] > coverage['CoverageEnd']:
            return None
    return result


def delivery_event_key(user_key, opportunity_key, event_type, revision, offset_days, channel):
    """Stable, unambiguous idempotency key; no delivery occurs here.

    Serialize the typed tuple as JSON rather than joining stringified values:
    zero-day offsets must differ from missing offsets, and delimiters inside
    identifiers must not make distinct events share a hash input.
    """
    text_values = {
        'user_key': user_key,
        'opportunity_key': opportunity_key,
        'event_type': event_type,
        'revision': revision,
        'channel': channel,
    }
    for field, value in text_values.items():
        if not isinstance(value, str) or not value or value != value.strip():
            raise ValueError(f'{field} must be nonblank text without outer whitespace')
    if offset_days is not None and type(offset_days) is not int:
        raise ValueError('offset_days must be an integer or None')
    basis = json.dumps(
        [user_key, opportunity_key, event_type, revision, offset_days, channel],
        ensure_ascii=False,
        separators=(',', ':'),
        allow_nan=False,
    )
    return 'EVENT:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24]
