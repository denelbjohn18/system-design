import importlib.util
import copy
import datetime as dt
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
store=module('state_test',ROOT/'scripts/state.py')
hook=module('hook_test',ROOT/'hooks/session_start.py')

class StateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'study';self.root.mkdir()
  self.data=store.initialize(self.root,{'onboarding_complete':False})
  self.cid=next(iter(self.data['concepts']));self.t='2026-10-06T10:00:00+00:00'
 def tearDown(self):self.tmp.cleanup()
 def evidence(self,independent=False):
  return {'learner_quote':'The browser asks the server.','probe':'What if it cannot reply?',
          'hint_used':not independent,'fresh_scenario':independent,
          'rubric':{x:2 for x in store.objectives()['concepts'][self.cid]['dimensions']}}
 def event(self,**kw):
  d={'hook_event_name':'sessionStart','workspace_roots':[str(self.root)]};d.update(kw);return d
 def test_schema_and_views(self):
  self.assertEqual(store.load(self.root)['revision'],0)
  self.assertEqual(len(self.data['concepts']),len(store.objectives()['concepts']))
 def test_cas_and_backup(self):
  d=copy.deepcopy(self.data);d['mode']='paused';store.commit(self.root,d,0)
  self.assertTrue((self.root/'.system-design/backups/revision-00000000.json').is_file())
  with self.assertRaises(store.StateError):store.commit(self.root,d,0)
 def test_lock(self):
  (self.root/'.system-design/.write-lock').mkdir()
  with self.assertRaises(store.StateError):store.commit(self.root,self.data,0)
 def test_wrong_root(self):
  with self.assertRaises(store.StateError):store.validate(self.data,self.root.parent)
 def test_schema_bad(self):
  d=copy.deepcopy(self.data);d['schema_version']=2
  with self.assertRaises(store.StateError):store.validate(d,self.root)
 def test_coverage_bad(self):
  d=copy.deepcopy(self.data);del d['concepts'][self.cid]
  with self.assertRaises(store.StateError):store.validate(d,self.root)
 def test_no_directories(self):
  f=self.root/'.system-design/curriculum.md';f.unlink();f.mkdir()
  with self.assertRaises(store.StateError):store.load(self.root)
  self.assertIn('could not be restored',hook.restore(self.event())['additional_context'])
 def test_symlink(self):
  f=self.root/'.system-design/progress.md';f.unlink();f.symlink_to(self.root/'absent')
  with self.assertRaises(store.StateError):store.load(self.root)
 def test_bad_json_visible(self):
  (self.root/'.system-design/state.json').write_text('{')
  self.assertIn('Cannot parse',hook.restore(self.event())['additional_context'])
 def test_no_parent_state(self):
  child=self.root/'unrelated';child.mkdir()
  self.assertIsNone(hook.restore(self.event(workspace_roots=[str(child)])))
 def test_paused_no_restore(self):
  d=copy.deepcopy(self.data);d['mode']='paused';store.commit(self.root,d,0)
  self.assertIsNone(hook.restore(self.event()))
 def test_conflicting_profile(self):
  f=self.root/'.system-design/profile.md'
  for text in ['Learning mode: active\nLearning mode: paused\n','Learning mode: paused\nLearning mode: active\n','bad profile']:
   f.write_text(text)
   self.assertIn('conflicting or stale',hook.restore(self.event())['additional_context'])
 def test_active_no_notes(self):
  out=hook.restore(self.event());self.assertIn('additional_context',out)
  self.assertNotIn('onboarding_complete',out['additional_context'])
 def test_multiroot_background(self):
  self.assertIsNone(hook.restore(self.event(workspace_roots=[str(self.root),str(self.root.parent)])))
  self.assertIsNone(hook.restore(self.event(is_background_agent=True)))
 def test_size_bound(self):
  (self.root/'.system-design/profile.md').write_text('x'*(store.MAX_BYTES+1))
  with self.assertRaises(store.StateError):store.load(self.root)
 def test_assisted_due(self):
  store.record(self.data,self.cid,'assisted',self.evidence(),self.t)
  i=self.data['concepts'][self.cid];self.assertEqual(i['due_at'],'2026-10-07T10:00:00+00:00');self.assertEqual(i['status'],'assisted')
 def test_intro_rubric(self):
  self.assertEqual(store.objectives()['concepts'][self.cid]['dimensions'],['correctness','application'])
  store.record(self.data,self.cid,'independent',self.evidence(True),self.t)
  self.assertEqual(self.data['concepts'][self.cid]['status'],'provisional')
 def test_independent_hint_refused(self):
  e=self.evidence(True);e['hint_used']=True
  with self.assertRaises(store.StateError):store.record(self.data,self.cid,'independent',e,self.t)
 def test_midnight_not_retained(self):
  store.record(self.data,self.cid,'independent',self.evidence(True),'2026-10-06T23:59:00+00:00')
  due=self.data['concepts'][self.cid]['due_at']
  store.record(self.data,self.cid,'independent',self.evidence(True),'2026-10-07T00:01:00+00:00')
  self.assertEqual(self.data['concepts'][self.cid]['status'],'provisional');self.assertEqual(self.data['concepts'][self.cid]['due_at'],due)
 def test_retention_and_saturation(self):
  now=dt.datetime(2026,10,6,10,tzinfo=dt.timezone.utc)
  for _ in range(8):
   store.record(self.data,self.cid,'independent',self.evidence(True),now.isoformat());now+=dt.timedelta(days=31)
  self.assertEqual(self.data['concepts'][self.cid]['interval_index'],4)
  self.assertEqual(self.data['concepts'][self.cid]['status'],'retained')
 def test_early_recall_not_advance(self):
  store.record(self.data,self.cid,'independent',self.evidence(True),self.t)
  store.record(self.data,self.cid,'independent',self.evidence(True),'2026-10-07T10:00:00+00:00')
  due=self.data['concepts'][self.cid]['due_at']
  store.record(self.data,self.cid,'independent',self.evidence(True),'2026-10-08T10:00:00+00:00')
  self.assertEqual(self.data['concepts'][self.cid]['interval_index'],1)
  self.assertEqual(self.data['concepts'][self.cid]['due_at'],due)
 def test_repair_missing_view(self):
  (self.root/'.system-design/progress.md').unlink()
  data=store.load(self.root,check_views=False);store.commit(self.root,data,0)
  self.assertEqual(store.load(self.root)['revision'],1)
 def test_wrong_rubric_refused(self):
  evidence=self.evidence(True);evidence['rubric']={'mechanism':2}
  with self.assertRaises(store.StateError):store.record(self.data,self.cid,'independent',evidence,self.t)
 def test_lock_cleanup_on_conflict(self):
  with self.assertRaises(store.StateError):store.commit(self.root,self.data,99)
  self.assertFalse((self.root/'.system-design/.write-lock').exists())
 def test_failure_resets(self):
  store.record(self.data,self.cid,'independent',self.evidence(True),self.t)
  store.record(self.data,self.cid,'miss',self.evidence(),'2026-10-07T10:00:00+00:00')
  self.assertIsNone(self.data['concepts'][self.cid]['last_independent_at'])
 def test_next_provisional_advances(self):
  store.record(self.data,self.cid,'independent',self.evidence(True),self.t)
  self.assertNotEqual(store.selection(self.data,self.t)['next_concept'],self.cid)
 def test_due_budget(self):
  for cid in list(self.data['concepts'])[:5]:store.record(self.data,cid,'assisted',self.evidence(),self.t)
  result=store.selection(self.data,'2026-10-08T10:00:00+00:00')
  self.assertEqual(result['due_count'],5);self.assertEqual(len(result['review_ids']),3)
 def test_defer_not_reselected(self):
  store.record(self.data,self.cid,'defer',self.evidence(),self.t)
  self.assertNotEqual(store.selection(self.data,self.t)['next_concept'],self.cid)
 def test_overview_required_refused(self):
  with self.assertRaises(store.StateError):store.record(self.data,self.cid,'overview',self.evidence(),self.t)
 def test_backwards_time_refused(self):
  store.record(self.data,self.cid,'assisted',self.evidence(),self.t)
  with self.assertRaises(store.StateError):store.record(self.data,self.cid,'assisted',self.evidence(),'2026-10-05T10:00:00+00:00')
 def test_interrupted_canonical_write(self):
  d=copy.deepcopy(self.data);d['mode']='paused';real=store.atomic
  def fail(path,text):
   if path.name=='state.json':raise OSError('simulated failure')
   return real(path,text)
  with patch.object(store,'atomic',side_effect=fail):
   with self.assertRaises(OSError):store.commit(self.root,d,0)
  self.assertEqual(store.load(self.root)['mode'],'active')
  self.assertFalse((self.root/'.system-design/.write-lock').exists())
  store.commit(self.root,store.load(self.root),0)
  self.assertIn('Learning mode: active',(self.root/'.system-design/profile.md').read_text())
 def test_legacy_not_overwritten(self):
  other=self.root/'legacy';other.mkdir();s=other/'.system-design';s.mkdir();(s/'profile.md').write_text('old')
  with self.assertRaises(store.StateError):store.initialize(other,{})
  self.assertEqual((s/'profile.md').read_text(),'old')

if __name__=='__main__':unittest.main()

class PromptContractTests(unittest.TestCase):
 def test_beginner_contract(self):
  learn=(ROOT/'skills/learn/SKILL.md').read_text()
  self.assertIn('No experience requirements or topic-confidence checklist',learn)
  self.assertIn('Intro objectives 01-04',learn)
  self.assertIn('After three total attempts',learn)
 def test_state_and_progress_contract(self):
  learn=(ROOT/'skills/learn/SKILL.md').read_text()
  self.assertIn('never search parent folders',learn)
  self.assertIn('Do not directly edit JSON',learn)
  self.assertIn('Provisional items awaiting delayed recall do not block',learn)
  self.assertIn('Read back canonical state',learn)
 def test_review_contract(self):
  review=(ROOT/'skills/review/SKILL.md').read_text()
  self.assertIn('maximum three',review)
  self.assertIn('Miss/assisted attempts receive repair',review)
  self.assertIn('paused workspace stays paused',review)
 def test_required_overview_boundaries(self):
  ids=store.objectives()['concepts']
  self.assertTrue(all(v['required'] for v in ids.values() if int(v['unit'])<14))
  self.assertTrue(all(not v['required'] for v in ids.values() if 14<=int(v['unit'])<=16))
