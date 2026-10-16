import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestNativeRecords(unittest.TestCase):
    def test_benchmarking(self):
        d=json.loads((ROOT/'native_results/benchmarking_charnes_verification.json').read_text())
        self.assertEqual(d['verdict'],'PASS');self.assertEqual(d['T1']['exact_n'],43);self.assertEqual(d['T1']['eligible_n'],43);self.assertIsNone(d['T0'])
    def test_dear(self):
        d=json.loads((ROOT/'native_results/dear_fixture_verification.json').read_text())
        self.assertEqual(d['verdict'],'PASS');self.assertEqual(d['T1']['exact_n'],2);self.assertEqual(d['T0']['exact_n'],2)
if __name__=='__main__':unittest.main(verbosity=2)
