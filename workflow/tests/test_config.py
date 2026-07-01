"""EngineConfig 单元测试。"""

from __future__ import annotations

import dataclasses

import pytest

from agent_engine import EngineConfig


class TestEngineConfig:
    """EngineConfig 配置校验测试。"""

    def test_default_values(self) -> None:
        """默认值应满足 PRD 中规定的 25/10。"""
        config = EngineConfig()
        assert config.recursion_limit == 25
        assert config.max_concurrency == 10
        assert config.raise_on_cycle is True

    def test_custom_values(self) -> None:
        """可自定义配置值。"""
        config = EngineConfig(
            recursion_limit=50, max_concurrency=20, raise_on_cycle=False
        )
        assert config.recursion_limit == 50
        assert config.max_concurrency == 20
        assert config.raise_on_cycle is False

    def test_recursion_limit_must_be_positive(self) -> None:
        """recursion_limit 必须为正整数。"""
        with pytest.raises(ValueError, match="recursion_limit 必须为正整数"):
            EngineConfig(recursion_limit=0)
        with pytest.raises(ValueError, match="recursion_limit 必须为正整数"):
            EngineConfig(recursion_limit=-1)

    def test_max_concurrency_must_be_positive(self) -> None:
        """max_concurrency 必须为正整数。"""
        with pytest.raises(ValueError, match="max_concurrency 必须为正整数"):
            EngineConfig(max_concurrency=0)
        with pytest.raises(ValueError, match="max_concurrency 必须为正整数"):
            EngineConfig(max_concurrency=-3)

    def test_config_is_immutable(self) -> None:
        """EngineConfig 是 frozen dataclass，不允许修改。"""
        config = EngineConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.recursion_limit = 100  # type: ignore[misc]
