import tempfile,sys,unittest,zipfile,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import build_release
class PortableReleaseTests(unittest.TestCase):
 def test_fresh_zip_only_has_universal_logic_and_rebuilds(self):
  with tempfile.TemporaryDirectory() as d:
   zipfile_path=Path(d)/"out.zip"
   res=build_release.build(zipfile_path,"cosmic-materials-assistant-p0")
   self.assertEqual(res["version"],"2.0.3")
   with zipfile.ZipFile(zipfile_path) as z:
    names=z.namelist()
    self.assertIn("scripts/v2_cli.py",names)
    self.assertIn("scripts/v2_review.py",names)
    self.assertIn("scripts/v2_auth.py",names)
    self.assertIn("LICENSE",names)
    for path in ("AGENTS.md","README.md","docs/AGENT_INSTALL.md","docs/USAGE.md",
                 "docs/ARCHITECTURE.md","scripts/install_agent.py","tests/test_v2_install.py"):
     self.assertIn(path,names)
    self.assertIn("tests/test_v2_security.py",names)
    self.assertNotIn("scripts/finalize_shandong_cosmic.py",names)
    self.assertNotIn("P3_SHANDONG_REMEDIATION.md",names)
    self.assertIn("name: cosmic-materials-assistant-p0",z.read("SKILL.md").decode())
    self.assertNotIn("/Users/",z.read("SKILL.md").decode())
    z.extractall(Path(d)/"clean")
   result=subprocess.run([sys.executable,"-B","scripts/build_release.py","--out","rebuild.zip"],cwd=Path(d)/"clean",capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
 def test_package_inventory_complete(self):
  self.assertTrue(all((build_release.ROOT/f).is_file() for f in build_release.FILES))
