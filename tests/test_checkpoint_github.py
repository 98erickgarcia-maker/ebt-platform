"""Test real Git snapshots against a local bare remote, never GitHub/cloud data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('checkpoint', Path(__file__).resolve().parents[1] / 'scripts/checkpoint_github.py')
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / 'repo'
        self.remote = self.home / 'remote.git'
        self.root.mkdir()
        subprocess.run(['git','init','--bare',str(self.remote)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.g('init','-b','main')
        self.g('config','user.name','Synthetic QA')
        self.g('config','user.email','qa@example.test')
        self.write('README.md','baseline\n')
        self.write('.gitignore','tmp/\n')
        self.g('add','README.md','.gitignore')
        self.g('commit','-m','baseline')
        self.g('remote','add','origin',str(self.remote))
        self.g('push','origin','main')
        self.g('fetch','origin')
        self.config_path = self.root / cp.DEFAULT_CONFIG
        self.write('source.txt','reviewed content\n')
        config = {'remote':'origin','repository_url':str(self.remote),'branch':'codex/qa-checkpoints',
                  'initial_base_ref':'refs/remotes/origin/main','files':[
                      {'path':'source.txt','reviewed_sha256':cp.digest(cp.canonical_bytes('source.txt',(self.root/'source.txt').read_bytes()))}]}
        cp.atomic_json(self.config_path,config)

    def g(self,*args,**kwargs):
        return cp.git(self.root,*args,**kwargs)

    def write(self,path,text):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

    def run_checkpoint(self,**kwargs):
        return cp.checkpoint(self.root,self.config_path,**kwargs)

    def test_push_readback_and_checkout_preserved(self):
        head=self.g('rev-parse','HEAD');index=(self.root/'.git/index').read_bytes()
        self.write('README.md','existing unstaged change\n')
        self.write('staged.txt','existing staged change\n');self.g('add','staged.txt')
        index=(self.root/'.git/index').read_bytes()
        result=self.run_checkpoint(push=True)
        self.assertTrue(result['remote_verified'])
        self.assertEqual(result['commit'],cp.remote_head(self.root,'origin','codex/qa-checkpoints'))
        self.assertEqual(self.g('rev-parse','HEAD'),head)
        self.assertEqual((self.root/'.git/index').read_bytes(),index)
        self.assertEqual(self.g('show',result['commit']+':source.txt'),'reviewed content')
        self.assertEqual(self.g('show',result['commit']+':README.md'),'baseline')
        self.assertEqual((self.root/'README.md').read_text(),'existing unstaged change\n')

    def test_unchanged_is_idempotent(self):
        a=self.run_checkpoint(push=True);b=self.run_checkpoint(push=True)
        self.assertEqual(a['commit'],b['commit'])

    def test_changed_bytes_require_review(self):
        self.run_checkpoint(push=True)
        self.write('source.txt','new reviewed candidate\n')
        with self.assertRaisesRegex(cp.CheckpointError,'Revisão necessária'):
            self.run_checkpoint(push=True)
        result=self.run_checkpoint(approve=True,push=True)
        self.assertTrue(result['remote_verified'])
        self.assertEqual(self.g('show',result['commit']+':source.txt'),'new reviewed candidate')

    def test_push_failure_keeps_local_for_retry(self):
        real_git=cp.git
        def fail_push(root,*args,**kwargs):
            if 'push' in args:raise cp.CheckpointError('synthetic transport failure')
            return real_git(root,*args,**kwargs)
        with patch.object(cp,'git',side_effect=fail_push),self.assertRaisesRegex(cp.CheckpointError,'transport'):
            self.run_checkpoint(push=True)
        local=self.g('rev-parse','refs/heads/codex/qa-checkpoints')
        self.assertIsNone(cp.remote_head(self.root,'origin','codex/qa-checkpoints'))
        result2=self.run_checkpoint(push=True)
        self.assertEqual(local,result2['commit'])

    def test_file_changed_during_snapshot_stops_upload(self):
        real_git=cp.git
        def concurrent_edit(root,*args,**kwargs):
            if args[0]=='commit-tree':self.write('source.txt','concurrent unreviewed edit\n')
            return real_git(root,*args,**kwargs)
        with patch.object(cp,'git',side_effect=concurrent_edit),self.assertRaisesRegex(cp.CheckpointError,'mudaram durante'):
            self.run_checkpoint(push=True)
        self.assertIsNone(cp.remote_head(self.root,'origin','codex/qa-checkpoints'))
        self.assertIsNotNone(self.g('rev-parse','--verify','refs/heads/codex/qa-checkpoints',optional=True))

    def test_remote_divergence_is_never_overwritten(self):
        first=self.run_checkpoint(push=True)
        divergent=self.g('commit-tree',first['tree'],'-p',first['commit'],data=b'concurrent remote commit\n')
        self.g('update-ref','refs/heads/codex/concurrent',divergent)
        self.g('push','origin','refs/heads/codex/concurrent:refs/heads/codex/qa-checkpoints')
        self.write('source.txt','changed\n')
        with self.assertRaisesRegex(cp.CheckpointError,'remota mudou'):
            self.run_checkpoint(approve=True,push=True)
        self.assertEqual(cp.remote_head(self.root,'origin','codex/qa-checkpoints'),divergent)

    def test_secrets_block_even_with_approval_and_do_not_echo_value(self):
        value='ghp_'+'a'*36
        self.write('source.txt','token='+value)
        with self.assertRaises(cp.CheckpointError) as failure:
            self.run_checkpoint(approve=True,push=True)
        self.assertNotIn(value,str(failure.exception))
        self.assertIn('github_token',str(failure.exception))

    def test_unlisted_private_files_never_enter_commit(self):
        self.write('.env','private data\n');self.write('customer.csv','private data\n')
        result=self.run_checkpoint(push=True)
        listing=self.g('ls-tree','-r','--name-only',result['commit'])
        self.assertNotIn('.env',listing);self.assertNotIn('customer.csv',listing)

    def test_missing_file_preserves_prior_remote(self):
        result=self.run_checkpoint(push=True)
        (self.root/'source.txt').unlink()
        with self.assertRaisesRegex(cp.CheckpointError,'ausente'):
            self.run_checkpoint(push=True)
        self.assertEqual(cp.remote_head(self.root,'origin','codex/qa-checkpoints'),result['commit'])

    def test_dry_run_has_no_git_or_config_mutation(self):
        before=self.config_path.read_bytes();head=self.g('rev-parse','HEAD')
        result=self.run_checkpoint(approve=True,dry_run=True)
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(before,self.config_path.read_bytes());self.assertEqual(head,self.g('rev-parse','HEAD'))
        self.assertIsNone(self.g('rev-parse','--verify','refs/heads/codex/qa-checkpoints',optional=True))

    def test_binary_requires_exact_pinned_hash(self):
        data=b'\x00binary'
        with self.assertRaises(cp.CheckpointError):cp.scan('logo.webp',data)
        self.assertEqual(cp.scan('logo.webp',data,cp.digest(data)),[])
        with self.assertRaises(cp.CheckpointError):cp.scan('logo.webp',data+b'x',cp.digest(data))

    def test_windows_and_linux_line_endings_share_review_hash(self):
        first=self.run_checkpoint(push=True)
        (self.root/'source.txt').write_bytes(b'reviewed content\r\n')
        second=self.run_checkpoint(push=True)
        self.assertEqual(first['commit'],second['commit'])

    def test_private_paths_and_traversal_refused(self):
        for path in ('../secret.txt','C:/secret.txt','tmp/a.txt','.env','src/.env.local','entregas/archive.md','a.pfx'):
            with self.subTest(path=path),self.assertRaises(cp.CheckpointError):cp.safe_path(path)
        cp.safe_path('docs/execucao/entregas/P01-01.md')

    def test_synthetic_credentials_and_html_not_false_positive(self):
        self.assertEqual(cp.scan('fixture.py',b'password="qa!synthetic-only"'),[])
        self.assertEqual(cp.scan('App.tsx',b'autoComplete={activation ? "new-password" : "current-password"}'),[])

    def test_lock_prevents_duplicate_run(self):
        with cp.lock(self.root):
            with self.assertRaises(cp.CheckpointError):
                with cp.lock(self.root):pass


if __name__=='__main__':unittest.main()
