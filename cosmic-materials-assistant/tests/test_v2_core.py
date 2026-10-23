import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import v2_core as v
def make():
 out=[]
 for j in range(10):
  mod="模块"+str(j//2)
  typ=["新增"]*2+["复用"]*7+["利旧"]
  out.append(dict(row_id=str(j+2),level1="系统",level2="域",level3=mod,
     functional_process="过程"+mod,trigger="用户触发"+mod, functional_user="用户",
     subprocess=("接收" if j%2==0 else "返回")+mod+"第"+str(j),
     movement="E" if j%2==0 else "X",data_group="业务对象"+str(j),
     attributes="字段"+str(j), development_type=typ[j],development_basis="设计记录第"+str(j),
     source_locator="FUR#"+str(j), evidence_text="需求动作"+str(j),cfp="1",
     review_status="approved", reviewer="项目审核员", reviewed_at="2026-10-21",
     boundary_basis="边界设计说明第"+str(j)+"节",
     movement_basis="验收用例描述外部输入或输出第"+str(j)+"条"))
 return out
def schematic_validate(rows):
    """Legacy rules test without external reviewer file/key fixtures."""
    return v.validate(rows,strict_evidence=False)

class UniversalContract(unittest.TestCase):
 def test_core_no_excel_coordinates(self):
  self.assertNotIn("I",v.FIELDS)
  self.assertEqual(set(v.FIELDS),{"subprocess","data_group","attributes"})
 def test_ratio_and_weights(self):
  rows=make()
  result=schematic_validate(rows)
  self.assertTrue(result["passed"],result["issues"])
  self.assertEqual(result["ratio_target"],{"新增":2,"复用":7,"利旧":1})
  self.assertEqual(result["weighted_workload_basis"],"4.31")
 def test_cross_process_duplicate_never_exempt(self):
  rows=make(); rows[2]["data_group"]=rows[0]["data_group"]
  x=schematic_validate(rows)
  self.assertIn("GLOBAL_DUPLICATE_DATA_GROUP",{e["code"] for e in x["issues"]})
 def test_same_subprocess_no_exception_even_other_module(self):
  rows=make();rows[5]["subprocess"]=rows[1]["subprocess"]
  self.assertIn("GLOBAL_DUPLICATE_SUBPROCESS",{e["code"] for e in schematic_validate(rows)["issues"]})
 def test_same_attrs_no_exception(self):
  rows=make();rows[6]["attributes"]=rows[0]["attributes"]
  self.assertIn("GLOBAL_DUPLICATE_ATTRIBUTES",{e["code"] for e in schematic_validate(rows)["issues"]})
 def test_module_multiple_processes_blocks(self):
  rows=make();rows[1]["functional_process"]="假设新过程"
  self.assertIn("MODULE_MULTIPLE_PROCESSES",{e["code"] for e in schematic_validate(rows)["issues"]})
 def test_max_8_movements(self):
  rows=make(); extras=[]
  for k in range(9):
   x=dict(rows[0]);x["row_id"]=str(100+k);x["subprocess"]="独立动作"+str(k);x["data_group"]="另对象"+str(k);x["attributes"]="其他字段"+str(k);x["movement"]="X"
   extras.append(x)
  self.assertIn("PROCESS_OVER_8",{e["code"] for e in schematic_validate(rows+extras)["issues"]})
 def test_missing_source_not_approved(self):
  rows=make();rows[0]["evidence_text"]=""
  x=schematic_validate(rows);self.assertFalse(x["passed"]);self.assertEqual(x["approved_cfp"],0)
 def test_reviewed_cfpoint_needs_real_approval(self):
  rows=make();rows[0]["review_status"]="pending"
  x=schematic_validate(rows)
  self.assertFalse(x["passed"])
  self.assertEqual(x["approved_cfp"],0)
  self.assertIn("HUMAN_REVIEW_MISSING",{e["code"] for e in x["issues"]})
 def test_missing_boundary_basis_blocks(self):
  rows=make();rows[0]["boundary_basis"]=""
  self.assertIn("BOUNDARY_BASIS_MISSING",{e["code"] for e in schematic_validate(rows)["issues"]})
 def test_evidenced_process_context_does_not_fake_new_process_or_approval(self):
  rows=make(); rows[2]["data_group"]=rows[0]["data_group"]
  rows[2]["evidence_text"]+=" 过程"+rows[2]["level3"]
  revised=v.qualify_with_evidenced_process(rows)
  self.assertNotEqual(revised[2]["data_group"],rows[2]["data_group"])
  self.assertEqual(revised[2]["functional_process"],rows[2]["functional_process"])
  self.assertEqual(revised[2]["cfp"],"")
  self.assertEqual(revised[2]["review_status"],"pending")
  issues={x["code"] for x in schematic_validate(revised)["issues"]}
  self.assertNotIn("GLOBAL_DUPLICATE_DATA_GROUP",issues)
  self.assertIn("HUMAN_REVIEW_MISSING",issues)
 def test_unicode_fullwidth_duplicates_are_rejected(self):
  self.assertEqual(v.norm("ＡＢＣ（订单）"),v.norm("abc订单"))
  rows=make();rows[2]["data_group"]=rows[0]["data_group"].replace("业务","業務")
  self.assertNotEqual(v.norm(rows[2]["data_group"]),v.norm(rows[0]["data_group"]))
 def test_unauthenticated_context_does_not_modify(self):
  rows=make(); rows[2]["attributes"]=rows[0]["attributes"]
  revised=v.qualify_with_evidenced_process(rows)
  self.assertEqual(revised[2]["attributes"],rows[2]["attributes"])
 def test_source_row_excluded(self):
  rows=make();rows[0]["status"]="未建设"
  x=schematic_validate(rows);self.assertEqual(x["active_rows"],9)
if __name__=="__main__":unittest.main()
