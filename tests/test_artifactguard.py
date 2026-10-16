import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from dea_artifactguard import *

class TestArtifactGuard(unittest.TestCase):
    def test_01_out_paths(self): self.assertEqual({p.name for p in coordinate_paths('out')},{'T0-X','T0-Y','T1-X','T1-Y','T2-X','T2-Y'})
    def test_02_in_paths(self): self.assertIn('score',next(p for p in coordinate_paths('in') if p.name=='T0-X').required)
    def test_03_t0x_no_score_out(self): self.assertIn('T0-X',analyze_release({'target_x','slack_x'},'out').active_exact_coordinate_paths)
    def test_04_legacy_miss(self): self.assertEqual(analyze_release({'target_x','slack_x'},'out').legacy_findings,())
    def test_05_full_paths(self): self.assertEqual(len(full_record_paths('out')),4)
    def test_06_balanced_sanitize(self):
        r={'score','target_x','target_y','slack_x','slack_y','lambda'};s=sanitize_release(r,'out',{'peer_x','peer_y'},{x:1 for x in r},{'score'},'coordinate_exact')
        self.assertTrue(s.feasible);self.assertEqual(set(s.suppressed),{'slack_x','slack_y'})
    def test_07_lambda_expensive(self):
        r={'score','target_x','target_y','slack_x','slack_y','lambda'};c={'score':5,'target_x':2,'target_y':2,'slack_x':1,'slack_y':1,'lambda':9}
        s=sanitize_release(r,'out',{'peer_x','peer_y'},c,{'score'},'coordinate_exact');self.assertEqual(set(s.suppressed),{'slack_x','slack_y'})
    def test_08_slack_expensive(self):
        r={'score','target_x','target_y','slack_x','slack_y','lambda'};c={'score':5,'target_x':2,'target_y':2,'slack_x':8,'slack_y':8,'lambda':1}
        s=sanitize_release(r,'out',{'peer_x','peer_y'},c,{'score'},'coordinate_exact');self.assertEqual(set(s.suppressed),{'lambda','target_x','target_y'})
    def test_09_public_lite(self): self.assertEqual(set(public_lite({'score','lambda','slack_x','target_x'})['retained']),{'score'})
    def test_10_infer_dear(self): self.assertEqual(infer_release_schema(['x_eff.csv','x_lambda.csv','x_sx.csv','x_sy.csv','x_tx.csv','x_ty.csv']),{'score','lambda','slack_x','slack_y','target_x','target_y'})
    def test_11_infer_benchmarking(self): self.assertEqual(infer_release_schema(['x_eff.csv','x_lambda.csv','x_sx.csv','x_sy.csv']),{'score','lambda','slack_x','slack_y'})
    def test_12_validation(self):
        with self.assertRaises(ValueError): coordinate_paths('sideways')
        with self.assertRaises(ValueError): analyze_release({'unknown'},'out')

if __name__=='__main__': unittest.main(verbosity=2)
