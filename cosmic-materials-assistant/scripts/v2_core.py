#!/usr/bin/env python3
"""COSMIC v2.0 semantic validation (independent from Excel letters and clients).

Default universal *delivery contract*, not claims about COSMIC official rules:
globally unique subprocess/data_group/attributes, project ratio 2:7:1,
1:1 L3->logical process, <=8 movements per process, reuse weight .33.
"""
from __future__ import annotations
import re
import unicodedata
from datetime import date
import v2_auth
from collections import Counter,defaultdict
from decimal import Decimal
from difflib import SequenceMatcher

METHOD="COSMIC V5"
POLICY_VERSION="universal-contract-2.0"
MOVEMENTS={"E","X","R","W"}
TARGET_RATIO={"新增":Decimal("0.2"),"复用":Decimal("0.7"),"利旧":Decimal("0.1")}
WEIGHTS={"新增":Decimal("1"),"复用":Decimal("0.33"),"利旧":Decimal("0")}
FIELDS={"subprocess":"子过程","data_group":"数据组","attributes":"数据属性"}
REQUIRED=("level1","level2","level3","functional_process","trigger","functional_user","subprocess","movement","data_group","attributes")


def norm(s):
    normalized=unicodedata.normalize("NFKC",str(s or "")).casefold()
    return "".join(c for c in normalized if c.isalnum() or '\u4e00'<=c<='\u9fff')


def apportion(n,ratio=TARGET_RATIO):
    raw={k:Decimal(n)*v for k,v in ratio.items()}
    q={k:int(v) for k,v in raw.items()}
    for k in sorted(raw,key=lambda k:(-(raw[k]-q[k]),list(raw).index(k)))[:n-sum(q.values())]:
        q[k]+=1
    return q


def record(value):
    """Canonical semantic model; NEVER pass spreadsheet coordinate references."""
    allowed=set(REQUIRED)|{"row_id","source_locator","evidence_text","cfp","development_type","development_basis","status","functional_process_id","fur_id","review_status","reviewer","reviewed_at","boundary_basis","movement_basis","source_file","source_sha256","approval_signature"}
    unknown=set(value)-allowed
    if unknown:raise ValueError("Unknown semantic fields: "+str(sorted(unknown)))
    return {key:str(value.get(key,"") or "").strip() for key in allowed}


def validate(records, approval_key=None, source_base=".", strict_evidence=True):
    """Return stable machine-readable issues and summary. No automatic approval."""
    rows=[record(x) for x in records]
    issues=[]
    seen={field:{} for field in FIELDS}
    grouped=defaultdict(list); modules=defaultdict(set)
    active=[]
    def flag(code,index,field,message,related=None,source="universal_delivery"):
        issues.append({"code":code,"row_id":rows[index].get("row_id") or str(index+2),
                       "field":field,"message":message,"related_row":related,"basis":source})
    for i,r in enumerate(rows):
        if r["status"] in ("未建设","excluded","unbuilt"):continue
        active.append((i,r))
        for field in REQUIRED:
            if not norm(r[field]):flag("MISSING_FIELD",i,field,"缺少真实有效字段内容")
        if r["movement"] and r["movement"] not in MOVEMENTS:
            flag("INVALID_MOVEMENT",i,"movement","数据移动仅允许E/X/R/W",source="COSMIC_V5")
        if r["cfp"] and r["cfp"] not in ("1","1.0"):
            flag("CFP_MUST_BE_ONE",i,"cfp","正式数据移动为1标准CFP",source="COSMIC_V5")
        if r["cfp"] and not r["evidence_text"]:
            flag("CFP_SOURCE_MISSING",i,"evidence_text","未见需求来源证据")
        if r["movement"] in MOVEMENTS and r["cfp"] not in ("1","1.0"):
            flag("CFP_UNCONFIRMED",i,"cfp","标准CFP必须在有依据的真实移动上确认为1；候选不得自动计点")
        if r["review_status"] not in ("approved","已审批") or not r["reviewer"] or not r["reviewed_at"]:
            flag("HUMAN_REVIEW_MISSING",i,"review_status","必须有人工确认状态、审核人和审核日期；程序不能自称已批准")
        if not r["boundary_basis"]:
            flag("BOUNDARY_BASIS_MISSING",i,"boundary_basis","缺少被度量软件块边界证据")
        if not r["movement_basis"]:
            flag("MOVEMENT_BASIS_MISSING",i,"movement_basis","缺少E/X/R/W与外部功能用户/持久存储的真实依据")
        module=tuple(r[k] for k in ("level1","level2","level3"))
        ident=r["functional_process_id"] or r["functional_process"]
        modules[module].add(ident)
        grouped[(module,ident)].append((i,r))
        for fld,label in FIELDS.items():
            value=norm(r[fld])
            if not value:continue
            prior=seen[fld].get(value)
            if prior is not None:
                flag("GLOBAL_DUPLICATE_"+fld.upper(),i,fld,
                    label+"与前行全表重复；仅可据真实功能过程及FUR加真实限定描述",
                    related=rows[prior].get("row_id") or str(prior+2))
            else:seen[fld][value]=i
        if r["development_type"] not in WEIGHTS:
            flag("DEVELOPMENT_TYPE_MISSING",i,"development_type","必须依据真实开发事实标记新增/复用/利旧")
        elif not r["development_basis"]:
            flag("DEVELOPMENT_EVIDENCE_MISSING",i,"development_basis","开发类型未提供实际依据")
        if not r["source_locator"]:
            flag("SOURCE_LOCATOR_MISSING",i,"source_locator","原始需求定位缺失")
        if not r["evidence_text"]:
            flag("SOURCE_TEXT_MISSING",i,"evidence_text","原始FUR文本证据缺失")
        if strict_evidence:
            if not v2_auth.source_valid(r,source_base):
                flag("UNVERIFIABLE_SOURCE",i,"source_file","原始来源文件或SHA256无效，不得确认CFP")
            if not v2_auth.review_date_valid(r):
                flag("INVALID_REVIEW_DATE",i,"reviewed_at","审核日期必须是有效且不晚于今天的ISO日期")
            if not v2_auth.valid_signature(r,approval_key):
                flag("UNVERIFIED_APPROVAL_SIGNATURE",i,"approval_signature",
                     "审批必须用审核人独立密钥签名，修改数据或来源后旧签名立即失效")
    for module,ids in modules.items():
        if len(ids)>1:
            first=next((i for i,r in active if tuple(r[k] for k in ("level1","level2","level3"))==module),None)
            if first is not None:
                flag("MODULE_MULTIPLE_PROCESSES",first,"functional_process",
                     "同一三级模块存在多个独立逻辑过程；不许为了去重凭空增设过程")
    for (module,ident),group in grouped.items():
        if not ident:continue
        if len(group)>8:
            flag("PROCESS_OVER_8",group[8][0],"functional_process",
                 "每逻辑过程最多8条数据移动，需真实拆分与边界证据")
        first=group[0]
        if first[1]["movement"]!="E":
            flag("PROCESS_FIRST_NOT_E",first[0],"movement","首条须真实触发E",source="COSMIC_V5_AND_DELIVERY")
        if not any(r["movement"]=="E" for _,r in group):
            flag("PROCESS_NO_E",first[0],"movement","缺少真实触发E",source="COSMIC_V5")
        if len(group)<2:
            flag("PROCESS_FEWER_THAN_TWO",first[0],"movement","有效过程少于两条移动",source="COSMIC_V5")
        if sum(r["movement"]=="E" for _,r in group)>1:
            flag("PROCESS_MULTIPLE_E",first[0],"movement","项目规则只允许一个真实触发E")
    counts=Counter(r["development_type"] for _,r in active if r["development_type"] in WEIGHTS)
    target=apportion(len(active))
    verified=bool(active) and all(r["development_type"] in WEIGHTS and r["development_basis"] for _,r in active)
    if verified and any(counts[k]!=target[k] for k in TARGET_RATIO):
        flag("DEVELOPMENT_RATIO_MISMATCH",active[0][0],"development_type",
             "实际开发类型比例不等于2:7:1；不能为了凑比例改写真实分类")
    if active and not verified:
        flag("DEVELOPMENT_RATIO_UNVERIFIED",active[0][0],"development_type",
             "存在未证实类别；不得将2:7:1预分配当真实建设事实")
    weighted=sum((WEIGHTS.get(r["development_type"],Decimal("0")) for _,r in active),Decimal("0"))
    issues.sort(key=lambda x:(int(x["row_id"]) if str(x["row_id"]).isdigit() else 10**10,x["field"],x["code"]))
    return {"schema":"cosmic-v2-delivery-1","method":METHOD,"policy":POLICY_VERSION,
            "passed":bool(active) and not issues,
            "active_rows":len(active),"candidate_cfp":sum(r["movement"] in MOVEMENTS for _,r in active),
            "approved_cfp":sum(r["movement"] in MOVEMENTS and r["cfp"] in ("1","1.0") and bool(r["evidence_text"]) and r["review_status"] in ("approved","已审批") for _,r in active) if not issues else 0,
            "ratio_target":target,"ratio_actual":dict(counts),"ratio_verified":verified,
            "weighted_workload_basis":str(weighted),"issues":issues,
            "disclaimer":"2:7:1/0.33/全表唯一/最多8条属于用户要求的通用交付合同，不宣称COSMIC V5官方规定"}

def qualify_with_evidenced_process(records):
    """Optional candidate-only renaming; NEVER invent a new functional process.

    Different real functional processes may qualify otherwise duplicated display
    text only when the FUR excerpt itself names that process. Reject approval
    of changed rows pending fresh independent review.
    """
    copied=[dict(r) for r in records]
    originals=[record(r) for r in records]
    for field in FIELDS:
        used=set()
        first={}
        for ix,r in enumerate(copied):
            if originals[ix]["status"] in ("未建设","excluded","unbuilt"):
                continue
            old=str(r.get(field,"") or "")
            token=norm(old)
            if not token:continue
            if token not in used:
                used.add(token)
                first[token]=ix
                continue
            previous=originals[first[token]]
            current=originals[ix]
            process=current["functional_process"]
            if (not process or process==previous["functional_process"]
                    or tuple(current[k] for k in ("level1","level2","level3"))==tuple(previous[k] for k in ("level1","level2","level3"))
                    or process not in current["evidence_text"]
                    or not current["source_locator"]):
                continue
            proposed=old+"【功能过程："+process+"】"
            unique=norm(proposed)
            if unique in used:
                continue
            r[field]=proposed
            r["review_status"]="pending"
            r["approval_signature"]=""
            r["cfp"]=""
            used.add(unique)
    return copied

def sample_profile():
    return {"policy":POLICY_VERSION,"semantic_fields":list(REQUIRED),
            "ratio":{k:str(v) for k,v in TARGET_RATIO.items()},
            "weights":{k:str(v) for k,v in WEIGHTS.items()},
            "global_unique":list(FIELDS),"max_movements":8}
