import sys,csv,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import v2_mcp
class MCPContractTests(unittest.TestCase):
 def test_schema_has_semantic_fields_only(self):
  spec=v2_mcp.schema()
  self.assertEqual(spec["single_deliverable"],".xlsx")
  self.assertIn("subprocess",spec["semantic_fields"])
  self.assertIn("data_group",spec["semantic_fields"])
 def test_inspect_does_not_create_files_and_generate_one(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);src=root/"client.csv";out=root/"workload.xlsx"
   with src.open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f);w.writerow(["一级模块","二级模块","三级模块","子过程描述","数据移动类型"])
    w.writerow(["管理","功能","模块","发送请求","E"])
   with patch.dict("os.environ",{"COSMIC_MCP_ROOT":str(root)}):
    preview=v2_mcp.inspect(str(src))
    self.assertFalse(preview["ready"])
    self.assertFalse(out.exists())
    result=v2_mcp.generate(str(src),str(out))
   self.assertEqual(result["file_count"],1)
   self.assertTrue(out.exists())
   self.assertEqual(len(list(root.glob("*.xlsx"))),1)
 def test_mcp_never_reads_or_writes_outside_authorized_root(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);allowed=r/"allowed";allowed.mkdir()
   outside=r/"outside.csv";outside.write_text("一级模块,子过程\\n机密,读取\\n",encoding="utf8")
   with patch.dict("os.environ",{"COSMIC_MCP_ROOT":str(allowed)}):
    with self.assertRaises(PermissionError):v2_mcp.inspect(outside)
    with self.assertRaises(PermissionError):v2_mcp.generate(outside,allowed/"result.xlsx")
    valid=allowed/"client.csv";valid.write_text("一级模块,子过程\\n公开,测试\\n",encoding="utf8")
    with self.assertRaises(PermissionError):v2_mcp.generate(valid,r/"outside.xlsx")
