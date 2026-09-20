import unittest
import copy
from pathlib import Path

from scripts.validate_publication_platform_contract import PACKAGE, _definition, validate
from scripts.build_sharepoint_upsert_package import load_target


class PublicationPlatformContractTests(unittest.TestCase):
    def require_private_package(self):
        if not PACKAGE.exists():
            self.skipTest("private live package is not present in source archive")

    def test_package_contract_is_valid_when_present(self):
        self.require_private_package()
        self.assertEqual(validate(_definition()), [])

    def test_record_loop_is_required(self):
        self.require_private_package()
        definition = copy.deepcopy(_definition())
        definition["actions"].pop("Apply_to_each_Publication")
        self.assertIn("registry writes must be inside an explicit record loop", validate(definition))

    def test_parallel_writes_are_rejected(self):
        self.require_private_package()
        definition = copy.deepcopy(_definition())
        definition["actions"]["Apply_to_each_Publication"]["runtimeConfiguration"]["concurrency"]["repetitions"] = 20
        self.assertIn("record loop must use single-write concurrency", validate(definition))

    def test_duplicate_source_keys_fail_closed(self):
        self.require_private_package()
        definition = copy.deepcopy(_definition())
        definition["actions"]["Apply_to_each_Publication"]["actions"].pop("Condition_Duplicate_SourceKey")
        self.assertIn("duplicate SourceKey results must fail closed", validate(definition))

    def test_record_actions_cannot_be_top_level(self):
        self.require_private_package()
        definition = copy.deepcopy(_definition())
        definition["actions"]["SharePoint_Get_items"] = copy.deepcopy(
            definition["actions"]["Apply_to_each_Publication"]["actions"]["SharePoint_Get_items"]
        )
        self.assertIn("record-scoped SharePoint actions must not be top-level", validate(definition))

    def test_placeholder_target_is_not_accepted_as_native_target(self):
        with self.assertRaises(ValueError):
            load_target(Path("config/sharepoint-publication-target.template.json"))

    def test_unknown_run_after_dependency_is_rejected(self):
        self.require_private_package()
        definition = copy.deepcopy(_definition())
        definition["actions"]["Apply_to_each_Publication"]["actions"]["SharePoint_Get_items"]["runAfter"] = {"Missing": ["Succeeded"]}
        self.assertTrue(any("unknown runAfter" in error for error in validate(definition)))


if __name__ == "__main__":
    unittest.main()
