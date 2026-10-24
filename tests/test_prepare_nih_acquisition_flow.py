import unittest

from scripts.prepare_nih_acquisition_flow import prepare


class NihAcquisitionFlowTests(unittest.TestCase):
    def setUp(self):
        self.flow = prepare("https://example.sharepoint.com/personal/owner")

    def test_source_is_exact_and_four_response_reads_are_serial(self):
        actions = self.flow["actions"]
        scope = actions["Scope"]["inputs"]
        self.assertEqual([x["role"] for x in scope["requests"]],
                         ["search-current", "detail-current", "search-replay", "detail-replay"])
        self.assertEqual(scope["requests"][0]["request"]["oppNum"], "PA-25-301")
        self.assertEqual(scope["requests"][1]["request"], {"opportunityId": 357812})
        loop = actions["Acquisition"]["actions"]["For_each_response"]
        self.assertEqual(loop["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        self.assertEqual(self.flow["triggers"]["Recurrence"]["runtimeConfiguration"]["concurrency"]["runs"], 1)

    def test_archive_readback_precedes_admission_and_manifest(self):
        pipeline = self.flow["actions"]["Acquisition"]["actions"]
        loop = pipeline["For_each_response"]["actions"]
        self.assertEqual(loop["Guard_source"]["runAfter"], {"Verify_response": ["Succeeded"]})
        self.assertEqual(loop["Record_response"]["runAfter"], {"Guard_source": ["Succeeded"]})
        self.assertIn("$content", loop["Verify_response"]["inputs"])
        self.assertEqual(pipeline["Acquisition_manifest"]["runAfter"], {"Qualification_guard": ["Succeeded"]})
        self.assertIn("workflow()?['run']?['name']", self.flow["actions"]["Run_folder"]["inputs"])

    def test_no_downstream_or_delivery_claim_and_no_credentials(self):
        manifest = self.flow["actions"]["Acquisition"]["actions"]["Acquisition_manifest"]["inputs"]
        for flag in ["accepted", "register_updated", "model_refreshed", "end_to_end_qualified"]:
            self.assertIs(manifest[flag], False)
        text = str(self.flow)
        for operation in ["PatchItem", "PostItem", "RefreshDataset", "SendEmail", "Authorization", "Bearer"]:
            self.assertNotIn(operation, text)

    def test_failure_receipt_does_not_suppress_failure(self):
        failure = self.flow["actions"]["Observe_failure"]
        self.assertEqual(failure["runAfter"], {"Acquisition": ["Failed", "TimedOut"]})
        self.assertIs(failure["actions"]["Failure_receipt"]["inputs"]["notification_delivered"], False)
        terminal = failure["actions"]["Terminate_failure"]
        self.assertEqual(terminal["inputs"]["runStatus"], "Failed")
        self.assertEqual(set(terminal["runAfter"]["Verify_failure"]), {"Succeeded", "Failed", "TimedOut", "Skipped"})

    def test_fault_is_explicit_and_blocks_complete_manifest(self):
        flow = prepare("https://example.sharepoint.com/personal/owner", minutes=1, fault=True)
        pipeline = flow["actions"]["Acquisition"]["actions"]
        self.assertIn("if(false", pipeline["Qualification_guard"]["inputs"])
        self.assertIn("if(true", self.flow["actions"]["Acquisition"]["actions"]["Qualification_guard"]["inputs"])

    def test_all_folder_archives_are_binary_verified_before_manifest(self):
        pipeline = self.flow["actions"]["Acquisition"]["actions"]
        loop = pipeline["For_each_attachment_folder"]
        self.assertIn("synopsisAttachmentFolders", loop["foreach"])
        self.assertIn("equals(body('Read_attachment')?['$content'],body('Fetch_attachment')?['$content'])",
                      loop["actions"]["Verify_attachment"]["inputs"])
        self.assertEqual(pipeline["Qualification_guard"]["runAfter"], {"For_each_attachment_folder": ["Succeeded"]})
        self.assertEqual(loop["actions"]["Record_attachment"]["runAfter"], {"Verify_attachment": ["Succeeded"]})

    def test_bad_bindings_and_intervals_rejected(self):
        for site in ["http://example.sharepoint.com", "https://evil.example", "https://example.sharepoint.com/path?x=y"]:
            with self.assertRaises(ValueError):
                prepare(site)
        for interval in [0, 61, True]:
            with self.assertRaises(ValueError):
                prepare("https://example.sharepoint.com", minutes=interval)
        with self.assertRaises(ValueError):
            prepare("https://example.sharepoint.com", "/Documents/../other")


if __name__ == "__main__":
    unittest.main()
