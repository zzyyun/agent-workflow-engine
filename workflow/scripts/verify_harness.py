"""验证 harness-tasks.json 格式。"""
import json
from pathlib import Path

# 脚本位于 workflow/scripts/，harness 文件位于 workflow/
harness_dir = Path(__file__).resolve().parent.parent
tasks_file = harness_dir / "harness-tasks.json"

data = json.loads(tasks_file.read_text(encoding="utf-8"))

print(f"Schema version : {data['version']}")
print(f"Session config : {data['session_config']}")
print(f"Task count     : {len(data['tasks'])}")
print()
for t in data["tasks"]:
    status = t["status"]
    tid = t["id"]
    title = t["title"]
    deps = t["depends_on"]
    prio = t["priority"]
    val = t.get("validation", {}).get("command", "(none)")
    print(f"[{status:8}] {tid} (P={prio}) depends_on={deps}")
    print(f"           {title}")
    print(f"           validation: {val[:60]}...")
    print()
