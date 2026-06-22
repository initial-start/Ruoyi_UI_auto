"""测试层 conftest.py — 公共 fixtures，消除各测试文件的重复代码。

提供：
  - login_page:      未登录状态的 LoginPage（已导航到 /login）
  - logged_in_page:  已登录 + 已处理弹窗的 Page（可直接跳转业务页面）
  - dismiss_popup:   关闭 layui 弹窗的辅助方法
"""

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from pages.login_page import LoginPage


def dismiss_popup(page: Page) -> None:
    """关闭 layui 弹窗（安全提示 / 操作成功 / 确认框）。

    所有测试文件均可通过 testcases.conftest.dismiss_popup 调用。
    """
    popup = page.locator(".layui-layer-dialog:visible").first
    if popup.count() > 0:
        txt = popup.inner_text()
        allure.attach(txt, name="弹窗内容", attachment_type=allure.attachment_type.TEXT)
        if "成功" in txt or "安全提示" in txt or "提示" in txt:
            page.locator(".layui-layer-btn0").first.evaluate("el => el.click()")
            page.wait_for_timeout(500)


@pytest.fixture(scope="function")
def login_page(page: Page, config: ConfigManager) -> LoginPage:
    """未登录状态的 LoginPage，已导航到登录页。"""
    lp = LoginPage(page)
    lp.navigate(config.base_url)
    return lp


@pytest.fixture(scope="function")
def logged_in_page(page: Page, config: ConfigManager) -> Page:
    """执行完整登录流程，处理安全弹窗，返回已认证的 Page。

    用法：
        def test_xxx(self, logged_in_page, config):
            logged_in_page.goto(f"{config.base_url}/system/user")
    """
    page.goto(config.base_url + "/login", wait_until="domcontentloaded")
    page.fill("input[name='username']", config.credentials["username"])
    page.fill("input[name='password']", config.credentials["password"])
    page.locator("button.btn.btn-success.btn-block").click()
    page.wait_for_timeout(1500)
    dismiss_popup(page)
    return page
