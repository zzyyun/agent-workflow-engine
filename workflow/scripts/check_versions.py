"""验证项目所有关键依赖的实际安装版本。"""
from importlib.metadata import version

# 已安装包的精确版本
packages = [
    "langgraph",
    "langchain-core",
    "pydantic",
    "typing-extensions",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "ruff",
]

print(f"{'包名':<22} {'已安装版本':<15} {'锁定目标':<15} 状态")
print("-" * 70)

# 从 requirements*.txt 读锁定目标
locked: dict[str, str] = {}
for fname in ("requirements.txt", "requirements-dev.txt"):
    with open(fname, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "==" in line and not line.startswith("#"):
                name, ver = line.split("==", 1)
                locked[name.strip().lower()] = ver.strip()

for pkg in packages:
    installed = version(pkg)
    target = locked.get(pkg.lower(), "未锁定")
    status = "✅" if target == "未锁定" or installed == target else "❌"
    print(f"{pkg:<22} {installed:<15} {target:<15} {status}")
