"""Funding dry-run state and boundary checks, without messages or real people."""
import tempfile,unittest
from pathlib import Path
from scripts.grants_delivery_ledger import DryRunLedger
class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'ledger.sqlite';self.ledger=DryRunLedger(self.path);self.addCleanup(self.ledger.close)
        self.opportunity=dict(OpportunityKey='SYNTHETIC:O',CategoryKeys=['SYNTHETIC:C'],FunderKey='SYNTHETIC:F',ReviewStatus='Reviewed',DeadlinePrecision='day')
        self.rules=[dict(UserKey='SYNTHETIC:U',Scope=s,TargetKey=t,Active=True) for s,t in [('category','SYNTHETIC:C'),('funder','SYNTHETIC:F'),('opportunity','SYNTHETIC:O')]]
    def plan(self,**kwargs):return self.ledger.plan(self.opportunity,self.rules,event_type='deadline_changed',revision='v1',**kwargs)[0]
    def begin(self,key,**kwargs):return self.ledger.begin(key,self.opportunity,self.rules,access_allowed=True,current_revision='v1',**kwargs)
    def test_overlapping_follows_and_duplicate_trigger_one_event(self):
        key=self.plan();self.assertEqual(key,self.plan());self.assertEqual(len(self.ledger.inspect(key)['attempts']),0)
    def test_pending_attempt_survives_restart_without_reservation(self):
        key=self.plan();self.begin(key)
        other=DryRunLedger(self.path)
        try:self.assertIsNone(other.begin(key,self.opportunity,self.rules,access_allowed=True,current_revision='v1'))
        finally:other.close()
    def test_unsubscribe_between_match_and_boundary(self):
        key=self.plan()
        for rule in self.rules:rule['Active']=False
        self.assertIsNone(self.begin(key));self.assertEqual(self.ledger.inspect(key)['event']['status'],'blocked')
    def test_access_loss_blocks(self):
        key=self.plan();self.assertIsNone(self.ledger.begin(key,self.opportunity,self.rules,access_allowed=False,current_revision='v1'))
    def test_failed_attempt_retry_retains_history(self):
        key=self.plan();a=self.begin(key);self.ledger.outcome(key,a['Attempt'],'failed');b=self.begin(key)
        self.assertEqual(b['Attempt'],2);self.assertEqual(len(self.ledger.inspect(key)['attempts']),2)
    def test_ambiguous_provider_never_retried_and_exact_readback(self):
        key=self.plan();a=self.begin(key);self.ledger.outcome(key,a['Attempt'],'unknown',provider_id='SIMULATED:1')
        self.assertIsNone(self.begin(key))
        with self.assertRaises(ValueError):self.ledger.resolve(key,a['Attempt'],provider_id='SIMULATED:other')
        self.ledger.resolve(key,a['Attempt'],provider_id='SIMULATED:1');self.assertIsNone(self.begin(key))
    def test_changed_revision_and_cancellation_distinct_events(self):
        key=self.plan()
        newer=self.ledger.plan(self.opportunity,self.rules,event_type='deadline_changed',revision='v2')[0]
        cancelled=self.ledger.plan(self.opportunity,self.rules,event_type='deadline_cancelled',revision='v2')[0]
        self.assertEqual(len({key,newer,cancelled}),3)
    def test_approximate_date_no_precise_reminder(self):
        self.opportunity['DeadlinePrecision']='month'
        self.assertEqual(self.ledger.plan(self.opportunity,self.rules,event_type='reminder',revision='v1',offset_days=7),[])
    def test_real_provider_identity_rejected(self):
        key=self.plan();a=self.begin(key)
        with self.assertRaises(ValueError):self.ledger.outcome(key,a['Attempt'],'succeeded',provider_id='real-provider')
    def test_different_opportunity_preference_ignored(self):
        self.rules.append(dict(UserKey='SYNTHETIC:V',Scope='opportunity',TargetKey='SYNTHETIC:OTHER',Active=True))
        self.assertEqual(len(self.ledger.plan(self.opportunity,self.rules,event_type='deadline_changed',revision='v1')),1)

    def test_stale_revision_blocked_at_boundary(self):
        key=self.plan()
        self.assertIsNone(self.ledger.begin(key,self.opportunity,self.rules,access_allowed=True,current_revision='v2'))
    def test_cancellation_blocks_old_deadline_change(self):
        key=self.plan();self.opportunity['Cancelled']=True
        self.assertIsNone(self.begin(key))
    def test_canonical_status_cancellation_and_withdrawal_block_existing_events(self):
        for status in ('Cancelled', 'Canceled', 'Withdrawn'):
            with self.subTest(status=status):
                self.opportunity.pop('Status', None)
                key=self.ledger.plan(self.opportunity,self.rules,event_type='deadline_changed',revision=status)[0]
                self.opportunity['Status']=status
                self.assertIsNone(self.ledger.begin(key,self.opportunity,self.rules,access_allowed=True,current_revision=status))
                self.assertEqual(self.ledger.inspect(key)['event']['status'],'blocked')
                self.assertEqual(self.ledger.plan(self.opportunity,self.rules,event_type='reminder',revision=status,offset_days=7),[])
                cancelled=self.ledger.plan(self.opportunity,self.rules,event_type='deadline_cancelled',revision=status)[0]
                self.assertTrue(self.ledger.begin(cancelled,self.opportunity,self.rules,access_allowed=True,current_revision=status)['DryRun'])
    def test_interrupted_pending_attempt_can_reconcile_without_retry(self):
        key=self.plan();attempt=self.begin(key)
        self.ledger.resolve(key,attempt['Attempt'],provider_id='SIMULATED:recovered')
        self.assertIsNone(self.begin(key))
