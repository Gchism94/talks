"""Known arithmetic and evidence-boundary controls for allocation sizing."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('size_access',Path(__file__).with_name('size_access.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class SizingControls(unittest.TestCase):
 def test_known_hours_filters_and_instance_conversion(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);(base/'runs.json').write_text(json.dumps([dict(workload='ds',warmup=True,status='passed',platform='campus-aws',wall_seconds=999999,configured_threads=2),dict(workload='ds',warmup=False,status='failed',wall_seconds=999999),dict(workload='ds',warmup=False,status='passed',platform='campus-aws',wall_seconds=3600,configured_threads=2,peak_process_rss_mib=100)]))
   task=dict(id='test',resource='cpu',workload='ds',results_file='runs.json',participants_or_groups=40,jobs_each=2,repetitions_per_job=1,allowance_fraction=.25,provider_conversion=dict(provider='FIXTURE only',unit='test instance-SU',verified_date='fixture',units_per_instance_hour=2))
   result=module.size({'workloads':[task]},base);row=result['workloads'][0]
   # 40 × 2 one-hour jobs × 1.25 = 100 instance-hours, 200 configured core-hours.
   self.assertEqual(row['component_residency_hours'],100);self.assertEqual(row['configured_core_hour_envelope'],200);self.assertEqual(row['provider_units'],200);self.assertFalse(result['eligible_for_submission'])
 def test_cpu_control_is_never_gpu_sizing(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);(base/'runs.json').write_text(json.dumps([dict(workload='mlis',warmup=False,status='passed',device='cpu',sizing_eligible=False,wall_seconds=1)]))
   task=dict(id='test',resource='gpu',workload='mlis',results_file='runs.json',participants_or_groups=1,jobs_each=1,repetitions_per_job=1,allowance_fraction=0)
   with self.assertRaises(ValueError):module.size({'workloads':[task]},base)
   result=module.size({'workloads':[task]},base,True);self.assertFalse(result['measurement_qualified']);self.assertFalse(result['eligible_for_submission']);self.assertIsNone(result['workloads'][0]['full_physical_gpu_hours'])
 def test_visible_gpu_hours_are_not_full_physical_hours(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);(base/'runs.json').write_text(json.dumps([dict(workload='ds',warmup=False,status='passed',device='cuda:0',platform='free-colab',sizing_eligible=True,wall_seconds=1800,peak_torch_reserved_bytes=67108864)]))
   task=dict(id='gpu',resource='gpu',workload='ds',results_file='runs.json',participants_or_groups=8,jobs_each=3,repetitions_per_job=2,allowance_fraction=.25,provider_conversion=dict(provider='FIXTURE',unit='fractional instance-SU',verified_date='fixture',units_per_instance_hour=16))
   row=module.size({'workloads':[task]},base)['workloads'][0]
   self.assertEqual(row['visible_device_hours'],30);self.assertEqual(row['provider_units'],480);self.assertIsNone(row['full_physical_gpu_hours'])
if __name__=='__main__':unittest.main()
