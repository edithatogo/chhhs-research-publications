"""Persistent dry-run funding delivery ledger. No provider or send operation."""
import json
import sqlite3
from scripts.grants_planning import delivery_event_key, subscribers


def _cancelled(opportunity):
    """Respect canonical source status as well as explicit cancellation flags."""
    status = opportunity.get('Status')
    if status is not None and not isinstance(status, str):
        raise ValueError('Opportunity status must be text')
    return (opportunity.get('Cancelled') is True
            or (status or '').strip().casefold() in {'cancelled', 'canceled', 'withdrawn'})


def matching_users(opportunity, rules):
    targets = {'opportunity': {opportunity['OpportunityKey']},
               'category': set(opportunity.get('CategoryKeys') or []),
               'funder': {opportunity.get('FunderKey')}}
    relevant = []
    for rule in rules:
        if not isinstance(rule, dict) or type(rule.get('Active')) is not bool:
            raise ValueError('Valid preference objects required')
        if not rule['Active']: continue
        if rule.get('Scope') not in targets or any(not isinstance(rule.get(k),str) or not rule[k] or rule[k] != rule[k].strip() for k in ('UserKey','TargetKey')):
            raise ValueError('Valid active preference identity required')
        if rule['TargetKey'] in targets[rule['Scope']]: relevant.append(rule)
    return subscribers(opportunity, relevant)


class DryRunLedger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS delivery_event (
          event_key TEXT PRIMARY KEY, identity_json TEXT NOT NULL,
          user_key TEXT NOT NULL, opportunity_key TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS delivery_attempt (
          event_key TEXT NOT NULL, attempt INTEGER NOT NULL, status TEXT NOT NULL,
          provider_id TEXT, PRIMARY KEY(event_key, attempt));
        ''')
    def close(self): self.db.close()
    def plan(self, opportunity, rules, *, event_type, revision, offset_days=None, channel='email'):
        if event_type not in {'opportunity_changed','deadline_changed','deadline_cancelled','reminder'}:
            raise ValueError('Supported funding event required')
        if opportunity.get('ReviewStatus') != 'Reviewed': return []
        if event_type == 'reminder' and (opportunity.get('DeadlinePrecision') != 'day' or _cancelled(opportunity)): return []
        keys = []
        with self.db:
            for user in matching_users(opportunity,rules):
                key = delivery_event_key(user,opportunity['OpportunityKey'],event_type,revision,offset_days,channel)
                identity = json.dumps([user,opportunity['OpportunityKey'],event_type,revision,offset_days,channel],ensure_ascii=False)
                prior = self.db.execute('SELECT identity_json FROM delivery_event WHERE event_key=?',(key,)).fetchone()
                if prior and prior['identity_json'] != identity: raise ValueError('Event identity collision')
                self.db.execute('INSERT OR IGNORE INTO delivery_event VALUES (?,?,?,?,?)',(key,identity,user,opportunity['OpportunityKey'],'pending'))
                keys.append(key)
        return keys
    def begin(self, key, opportunity, current_rules, *, access_allowed, current_revision):
        if type(access_allowed) is not bool: raise ValueError('Explicit access decision required')
        with self.db:
            # Serialize reservations across independent processes/connections.
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM delivery_event WHERE event_key=?',(key,)).fetchone()
            if row is None: raise ValueError('Known event required')
            if row['status'] in {'pending_attempt','unknown','succeeded'}: return None
            identity = json.loads(row['identity_json'])
            if not isinstance(current_revision,str) or not current_revision or current_revision != current_revision.strip():
                raise ValueError('Current event revision required')
            eligible = (access_allowed and current_revision == identity[3]
                and (not _cancelled(opportunity) or identity[2] == 'deadline_cancelled')
                and opportunity.get('OpportunityKey') == row['opportunity_key']
                and opportunity.get('ReviewStatus') == 'Reviewed'
                and row['user_key'] in matching_users(opportunity,current_rules)
                and (identity[2] != 'reminder' or (opportunity.get('DeadlinePrecision') == 'day' and not _cancelled(opportunity))))
            if not eligible:
                self.db.execute('UPDATE delivery_event SET status=? WHERE event_key=?',('blocked',key)); return None
            attempt = self.db.execute('SELECT COALESCE(MAX(attempt),0)+1 FROM delivery_attempt WHERE event_key=?',(key,)).fetchone()[0]
            self.db.execute('INSERT INTO delivery_attempt VALUES (?,?,?,NULL)',(key,attempt,'pending_attempt'))
            self.db.execute('UPDATE delivery_event SET status=? WHERE event_key=?',('pending_attempt',key))
            return {'EventKey':key,'Attempt':attempt,'DryRun':True,'WouldSend':True,'DeliveryEnabled':False}
    def outcome(self, key, attempt, status, *, provider_id=None):
        if status not in {'succeeded','failed','unknown'}: raise ValueError('Supported simulated outcome required')
        if provider_id is not None and (not isinstance(provider_id,str) or not provider_id.startswith('SIMULATED:') or len(provider_id) == len('SIMULATED:')):
            raise ValueError('Only simulated provider identities allowed')
        if status == 'succeeded' and provider_id is None: raise ValueError('Simulated provider readback identity required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM delivery_attempt WHERE event_key=? AND attempt=?',(key,attempt)).fetchone()
            if row is None or row['status'] != 'pending_attempt': raise ValueError('Exact pending attempt required')
            self.db.execute('UPDATE delivery_attempt SET status=?,provider_id=? WHERE event_key=? AND attempt=?',(status,provider_id,key,attempt))
            self.db.execute('UPDATE delivery_event SET status=? WHERE event_key=?',(status,key))
    def resolve(self, key, attempt, *, provider_id):
        if not isinstance(provider_id,str) or not provider_id.startswith('SIMULATED:') or len(provider_id) == len('SIMULATED:'):
            raise ValueError('Exact simulated provider identity required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM delivery_attempt WHERE event_key=? AND attempt=?',(key,attempt)).fetchone()
            if row is None or row['status'] not in {'unknown','pending_attempt'} or (row['provider_id'] is not None and row['provider_id'] != provider_id):
                raise ValueError('Exact ambiguous attempt/provider match required')
            self.db.execute('UPDATE delivery_attempt SET status=? WHERE event_key=? AND attempt=?',('succeeded',key,attempt))
            self.db.execute('UPDATE delivery_event SET status=? WHERE event_key=?',('succeeded',key))
    def inspect(self, key):
        event = self.db.execute('SELECT * FROM delivery_event WHERE event_key=?',(key,)).fetchone()
        return {'DryRun':True,'DeliveryEnabled':False,'event':dict(event) if event else None,
                'attempts':[dict(r) for r in self.db.execute('SELECT * FROM delivery_attempt WHERE event_key=? ORDER BY attempt',(key,))]}
