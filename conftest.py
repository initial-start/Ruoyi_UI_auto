"""项目根 conftest.py — 全局 pytest fixtures 和钩子。

提供：
  1. 日志系统初始化（session 级别，自动执行）
  2. 配置加载 fixture（session 级别单例）
  3. 浏览器启动参数注入（headless / slow_mo）
  4. 浏览器上下文定制（viewport / locale）
  5. Page 默认超时注入
  6. 测试失败自动截图并附加到 Allure
"""

from datetime import datetime

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from utils.logger import setup_logger


# ——————————————————————————————————————————
# Session 级 Fixtures
# ——————————————————————————————————————————


@pytest.fixture(scope="session", autouse=True)
def _setup_logging() -> None:
    """自动初始化日志系统（session 级别，所有测试之前执行一次）。"""
    setup_logger()


@pytest.fixture(scope="session")
def config() -> ConfigManager:
    """加载对应环境的配置（session 级别单例）。

    通过环境变量 TEST_ENV 控制，默认为 'test'。
    用法：
        def test_something(config):
            url = config.base_url
            user = config.credentials["username"]
    """
    return ConfigManager()


# ——————————————————————————————————————————
# pytest-playwright 扩展 Fixtures
# ——————————————————————————————————————————


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict, config: ConfigManager) -> dict:
    """注入浏览器启动参数 — executable_path / headless / slow_mo 从配置读取。"""
    browser_cfg = config.browser_config
    args = {
        **browser_type_launch_args,
        "headless": browser_cfg.get("headless", True),
        "slow_mo": browser_cfg.get("slow_mo", 0),
    }
    exe = browser_cfg.get("executable_path")
    if exe:
        args["executable_path"] = exe
    return args


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args: dict, config: ConfigManager) -> dict:
    """定制浏览器 context 创建参数 — viewport、locale。"""
    browser_cfg = config.browser_config
    return {
        **browser_context_args,
        "viewport": browser_cfg.get("viewport", {"width": 1920, "height": 1080}),
        "locale": browser_cfg.get("locale", "zh-CN"),
    }


@pytest.fixture(scope="function")
def page(page: Page, config: ConfigManager) -> Page:
    """注入默认超时到 Page。

    每个测试函数创建新的 page，确保测试隔离。
    """
    page.set_default_timeout(config.timeout)
    return page


# ——————————————————————————————————————————
# 失败截图钩子
# ——————————————————————————————————————————


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并附加到 Allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    # 仅在测试执行阶段 (call) 且失败时触发
    if report.when != "call" or not report.failed:
        return

    page: Page | None = item.funcargs.get("page")
    if page is None:
        return

    # 生成文件名: test_file__test_name__timestamp
    test_name = item.nodeid.replace("/", "_").replace("\\", "_").replace("::", "__")
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{test_name}__{timestamp}"

    from utils.allure_utils import save_screenshot_to_file

    path = save_screenshot_to_file(page, filename)

    # 附加到 Allure 报告
    allure.attach.file(
        str(path),
        name=f"失败截图 — {item.name}",
        attachment_type=allure.attachment_type.PNG,
    )
