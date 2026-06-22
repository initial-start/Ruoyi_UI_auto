"""全局常量定义 — 项目根路径、默认超时、目录路径等。"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 目录路径
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"
REPORT_DIR = PROJECT_ROOT / "reports"
ALLURE_RESULTS_DIR = REPORT_DIR / "allure-results"

# 默认超时（毫秒）
DEFAULT_TIMEOUT: int = 30_000
DEFAULT_NAVIGATION_TIMEOUT: int = 60_000

# 默认环境
DEFAULT_ENV: str = "test"

# 日志配置
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
