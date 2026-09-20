"""Local reference logic for institutional dates and subscription matching.

No tenant writes, calendar invitations or notifications. Holiday coverage and
institutional lead times must be supplied by a versioned institutional policy.
"""
from datetime import date, timedelta
import hashlib
import re

SUBSCRIPTION_SCOPES = {'opportunity', 'category', 'funder'}


def institutional_deadline(external_date, lead_days, *, business_days=True, holidays=()):
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
    excluded = {date.fromisoformat(day) for day in holidays}
    remaining = lead_days
    while remaining:
        target -= timedelta(days=1)
        if not business_days or (target.weekday() < 5 and target not in excluded):
            remaining -= 1
    return target.isoformat()


def subscribers(opportunity, subscriptions):
    """Unique candidate user keys; identity/access/consent checked by delivery."""
    if not isinstance(opportunity, dict):
        raise ValueError('opportunity must be an object')
    opportunity_key = opportunity.get('OpportunityKey')
    if not isinstance(opportunity_key, str) or not opportunity_key.strip():
        raise ValueError('opportunity requires OpportunityKey for subscription matching')
    category_keys = opportunity.get('CategoryKeys', [])
    if not isinstance(category_keys, (list, tuple, set)) or any(
        not isinstance(key, str) or not key.strip() for key in category_keys
    ):
        raise ValueError('opportunity CategoryKeys must be a collection of non-empty keys')
    funder_key = opportunity.get('FunderKey', '')
    if funder_key and (not isinstance(funder_key, str) or not funder_key.strip()):
        raise ValueError('opportunity FunderKey must be a string when supplied')
    targets = {'opportunity': {opportunity_key.strip()},
               'category': {key.strip() for key in category_keys},
               'funder': {funder_key.strip()} if isinstance(funder_key, str) and funder_key.strip() else set()}
    matched = set()
    for rule in subscriptions:
        if not isinstance(rule, dict):
            raise ValueError('subscription rule must be an object')
        scope = rule.get('Scope')
        user_key = rule.get('UserKey')
        target_key = rule.get('TargetKey')
        if not all(isinstance(value, str) for value in (scope, user_key, target_key)):
            raise ValueError('subscription requires string scope, user key and target key')
        scope = scope.strip()
        user_key = user_key.strip()
        target_key = target_key.strip()
        if scope not in SUBSCRIPTION_SCOPES or not user_key or not target_key:
            raise ValueError('subscription requires a supported scope, user key and target key')
        if rule.get('Active') is not True and rule.get('Active') is not False:
            raise ValueError('subscription Active must be boolean')
        if rule.get('Active') is True and target_key in targets[scope]:
            matched.add(user_key)
    return sorted(matched)


def validate_policy(policy):
    """Validate a versioned institutional date policy without approving it."""
    required = ('PolicyKey', 'Version', 'OrganisationKey', 'AnchorKind', 'LeadDays',
                'HolidayCalendarVersion', 'EffectiveFrom')
    if not all(policy.get(key) not in (None, '') for key in required):
        return False
    if type(policy['LeadDays']) is not int or not 0 <= policy['LeadDays'] <= 3660:
        return False
    if policy.get('CalendarOrBusinessDays') not in ('calendar', 'business'):
        return False
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(policy['EffectiveFrom'])):
        return False
    if policy.get('EffectiveTo') and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(policy['EffectiveTo'])):
        return False
    try:
        effective_from = date.fromisoformat(str(policy['EffectiveFrom']))
        effective_to = date.fromisoformat(str(policy['EffectiveTo'])) if policy.get('EffectiveTo') else None
    except ValueError:
        return False
    if effective_to and effective_to < effective_from:
        return False
    holidays = policy.get('HolidayDates', ())
    if not isinstance(holidays, (list, tuple, set)):
        return False
    try:
        parsed_holidays = [date.fromisoformat(str(day)) for day in holidays]
    except ValueError:
        return False
    if len(parsed_holidays) != len(set(parsed_holidays)):
        return False
    return True


def delivery_event_key(user_key, opportunity_key, event_type, revision, offset_days, channel):
    """Stable idempotency key for a future delivery ledger; no delivery occurs here."""
    fields = (user_key, opportunity_key, event_type, revision, channel)
    if any(not isinstance(value, str) or not value.strip() for value in fields):
        raise ValueError('delivery event identity fields must be non-empty strings')
    if type(offset_days) is not int or not -3660 <= offset_days <= 3660:
        raise ValueError('delivery event offset_days must be an integer from -3660 to 3660')
    basis = '|'.join(value.strip() for value in fields[:4]) + f'|{offset_days}|' + fields[4].strip()
    return 'EVENT:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24]
