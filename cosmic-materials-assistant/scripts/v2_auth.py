"""Cryptographically bind independently reviewed rows to source files and data.

An HMAC only proves possession of a reviewer-held key; human credentials and
business evidence semantics remain external acceptance gates.
"""
import hashlib,hmac,json
from datetime import date
from pathlib import Path

SIGNATURE_FIELDS=(
 "row_id","level1","level2","level3","functional_process","functional_process_id",
 "functional_user","trigger","subprocess","movement","data_group","attributes","cfp",
 "development_type","development_basis","evidence_text","source_locator",
 "source_file","source_sha256","status","review_status","reviewer","reviewed_at",
 "boundary_basis","movement_basis","fur_id"
)
def sha_file(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b""):
   h.update(chunk)
 return h.hexdigest()

def source_path(row,base_dir):
 value=str(row.get("source_file","")).strip()
 if not value:raise ValueError("Missing primary source_file")
 root=Path(base_dir).expanduser().resolve(strict=True)
 if not root.is_dir():raise ValueError("Source root must be a real directory")
 source=Path(value).expanduser()
 if not source.is_absolute():source=root/source
 source=source.resolve(strict=True)
 if root not in source.parents:
  raise ValueError("Evidence source is outside approved source root")
 if not source.is_file():raise ValueError("Evidence source is not a file")
 return source

def source_valid(row,base_dir):
 try:
  source=source_path(row,base_dir)
  return hmac.compare_digest(sha_file(source),str(row.get("source_sha256","")))
 except (OSError,ValueError):return False

def review_date_valid(row):
 try:
  return date.fromisoformat(str(row.get("reviewed_at","")))<=date.today()
 except ValueError:return False

def row_payload(row):
 return json.dumps({k:str(row.get(k,"") or "").strip() for k in SIGNATURE_FIELDS},
                   ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def signature(row,key):
 if not isinstance(key,bytes) or len(key)<32:
  raise ValueError("Reviewer HMAC key must contain >=32 bytes")
 return hmac.new(key,b"cosmic-v2.0.1-row\0"+row_payload(row),hashlib.sha256).hexdigest()

def valid_signature(row,key):
 sig=str(row.get("approval_signature","")).strip()
 if key is None or len(sig)!=64:return False
 try:return hmac.compare_digest(signature(row,key),sig)
 except ValueError:return False

def read_key(path):
 p=Path(path)
 k=p.read_bytes().strip()
 if len(k)<32:raise ValueError("Reviewer key must have >=32 bytes")
 return k
