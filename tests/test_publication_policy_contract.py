import copy
import unittest
from scripts.publication_policy_contract import load_policy, validate_policy


class PolicyContractTests(unittest.TestCase):
    def test_default_is_automatic_and_retains_uncertainty(self):
        policy=load_policy()
        self.assertFalse(policy['manual_record_approval'])
        self.assertEqual(policy['ambiguous_identity'],'preserve-separate-source-records')
        self.assertEqual(policy['corrections_and_retractions'],'retain-and-label')

    def test_changed_or_incomplete_policy_is_not_silently_adopted(self):
        for field,value in [('manual_record_approval',0),('inclusion','review-first'),('version','')]:
            policy=copy.deepcopy(load_policy());policy[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_policy(policy)
        policy=load_policy();policy['unexpected']=True
        with self.assertRaises(ValueError):validate_policy(policy)
