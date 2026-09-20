"""Local reference logic for institutional dates and subscription matching.

No tenant writes, calendar invitations or notifications. Holiday coverage and
institutional lead times must be supplied by a versioned institutional policy.
"""
from datetime import date, timedelta
import hashlib
import re


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
    targets = {'opportunity': {opportunity['OpportunityKey']},
               'category': set(opportunity.get('CategoryKeys', [])),
               'funder': {opportunity.get('FunderKey')}}
    return sorted({rule['UserKey'] for rule in subscriptions
                   if rule.get('Active') is True and rule.get('UserKey')
                   and rule.get('TargetKey')
                   and rule.get('TargetKey') in targets.get(rule.get('Scope'), set())})


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
    return True


def delivery_event_key(user_key, opportunity_key, event_type, revision, offset_days, channel):
    """Stable idempotency key for a future delivery ledger; no delivery occurs here."""
    basis = '|'.join(str(value or '') for value in (
        user_key, opportunity_key, event_type, revision, offset_days, channel))
    return 'EVENT:' + hashlib.sha256(basis.encode('utf-8')).hexdigest()[:24]
