"""Pytest 公共配置与 fixture。"""

from __future__ import annotations

import os
import sys

# 将 src 加入路径，方便 ``import agent_engine``
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
