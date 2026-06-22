"""日志系统 — 双通道输出（控制台 + 按日期滚动的文件）。

用法：
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("测试开始")
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import LOG_DIR, LOG_FORMAT, LOG_DATE_FORMAT

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志文件路径（按日期命名）
LOG_FILE = LOG_DIR / f"test_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logger() -> None:
    """初始化全局日志配置。

    应在 conftest.py 的 session 级 fixture 中调用一次。
    配置后，所有通过 get_logger() 获取的 logger 都会：
      - DEBUG 及以上 → 写入文件
      - INFO 及以上 → 输出到控制台
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()  # 防止重复添加

    fmt = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # — 文件处理器 (DEBUG) —
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    # — 控制台处理器 (INFO) —
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    """获取命名 logger。

    如果根 logger 尚未配置，自动调用 setup_logger()。
    """
    if not logging.getLogger().handlers:
        setup_logger()
    return logging.getLogger(name)
