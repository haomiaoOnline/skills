import subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from install_agent import install

class AgentInstallTests(unittest.TestCase):
    def test_clean_install_from_manifest_only_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"agent"/"skills"/"cosmic-materials-assistant-p0"
            response=install(target,skip_deps=True)
            self.assertEqual(response["status"],"installed")
            self.assertTrue((target/"SKILL.md").is_file())
            self.assertTrue((target/"AGENTS.md").is_file())
            self.assertTrue((target/"docs/AGENT_INSTALL.md").is_file())
            self.assertFalse((target/"P3_SHANDONG_REMEDIATION.md").exists())
            p=subprocess.run([sys.executable,"-B","-m","unittest","discover","-s","tests",
                              "-p","test_v2_core.py"],cwd=target,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr[-1300:])
            with self.assertRaises(FileExistsError):
                install(target,skip_deps=True)
    def test_missing_source_or_permission_does_not_destroy_destination(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"existing"
            target.mkdir()
            sentinel=target/"private.txt"
            sentinel.write_text("must preserve",encoding="utf8")
            with self.assertRaises(FileExistsError):
                install(target,skip_deps=True)
            self.assertEqual(sentinel.read_text(),"must preserve")
