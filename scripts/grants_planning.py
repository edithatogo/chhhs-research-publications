"""Local reference logic for institutional dates and subscription matching.

No tenant writes, calendar invitations or notifications. Holiday coverage and
institutional lead times must be supplied by a versioned institutional policy.
"""
from datetime import date, timedelta
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
