"""多环境配置单例加载器。

通过环境变量 TEST_ENV 切换环境，默认为 'test'。
用法：
    from config.config_manager import ConfigManager
    config = ConfigManager()
    print(config.base_url)
    print(config.credentials["username"])
"""

import os
from pathlib import Path
from typing import Any

import yaml


class ConfigManager:
    """配置管理器单例 — 进程级别只加载一次 YAML 配置。

    通过 __new__ 实现线程安全的懒加载单例。
    配置数据在首次实例化时从 YAML 文件加载并缓存。
    """

    _instance: "ConfigManager | None" = None
    _config: dict[str, Any] | None = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is not None:
            return  # 已加载，跳过重复初始化

        env = os.getenv("TEST_ENV", "test")
        config_dir = Path(__file__).resolve().parent / "environments"
        config_file = config_dir / f"{env}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"找不到环境配置文件: {config_file}\n"
                f"请设置 TEST_ENV 环境变量为 dev/test/prod 之一"
            )

        with open(config_file, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    # —— 便捷属性 ————————————————————————————————

    @property
    def base_url(self) -> str:
        """被测系统基础 URL。"""
        return self._config["base_url"]

    @property
    def browser_config(self) -> dict[str, Any]:
        """浏览器启动配置 (headless, slow_mo, viewport, locale)。"""
        return self._config.get("browser", {})

    @property
    def timeout(self) -> int:
        """全局操作超时（毫秒）。"""
        return self._config.get("timeout", 30_000)

    @property
    def credentials(self) -> dict[str, str]:
        """登录凭据 {username, password}。"""
        return self._config.get("credentials", {})

    @property
    def database(self) -> dict[str, Any]:
        """数据库连接配置 {host, port, user, password, database}。"""
        return self._config.get("database", {})

    # —— 通用访问 ————————————————————————————————

    def get(self, key: str, default: Any = None) -> Any:
        """获取任意配置项。"""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        return key in self._config
