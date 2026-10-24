import json
from pathlib import Path
import tempfile
import unittest
from scripts.lane_resume import read_checkpoint, REQUIRED


class LaneResumeTests(unittest.TestCase):
    def test_owner_selection_and_missing_lane_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'private/ops/execution-lanes'
            folder.mkdir(parents=True)
            data = dict.fromkeys(REQUIRED, 'none')
            data.update(schema_version=1, owner='E01', failures=[], completion=[])
            (folder / 'e01.json').write_text(json.dumps(data))
            self.assertEqual(read_checkpoint(root, 'e01')['owner'], 'E01')
            with self.assertRaises(FileNotFoundError):
                read_checkpoint(root, 'grants')
            for lane in ('../e01', '/tmp/e01', 'E01'):
                with self.assertRaises(ValueError):
                    read_checkpoint(root, lane)
            data['failures'] = [{'operation': 'save', 'observed': 'draft conflict'}]
            (folder / 'e01.json').write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                read_checkpoint(root, 'e01')

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / 'private/ops/execution-lanes').mkdir(parents=True)
            (root / 'private/ops/execution-lanes/e01.json').symlink_to(Path(outside) / 'state.json')
            with self.assertRaises(ValueError):
                read_checkpoint(root, 'e01')
