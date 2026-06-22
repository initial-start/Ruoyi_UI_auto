"""登录模块测试 — 数据驱动。

测试数据来源: data/login_data.yaml
  - success 场景: 登录 → 断言弹窗 → 确认 → 验证跳转
  - failure 场景: 登录 → 断言错误提示
"""

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from data.testdata_loader import parametrize_from_yaml
from pages.login_page import LoginPage

# — 从 YAML 加载所有登录用例数据 —
cases, ids = parametrize_from_yaml("login_data.yaml", "login_cases")


@allure.feature("登录模块")
class TestLogin:

    @allure.story("登录数据驱动测试")
    @pytest.mark.login
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_login(self, page: Page, config: ConfigManager, case: dict) -> None:
        """数据驱动的登录测试。

        根据 case.scenario 分发:
          - success → 验证登录成功 + 弹窗断言
          - failure → 验证登录失败 + 错误提示断言
        """
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)

        scenario = case["scenario"]

        # —————————————— 执行登录 ——————————————
        login_page.fill_username(case["username"]) \
                   .fill_password(case["password"]) \
                   .click_login()

        login_page.page.wait_for_load_state("networkidle")

        # —————————————— 场景分发 ——————————————
        if scenario == "success":
            self._verify_success(login_page, case)
        elif scenario == "failure":
            self._verify_failure(login_page, case)

    # ================================================================
    # 验证方法
    # ================================================================

    @allure.step("验证登录成功 + 弹窗断言")
    def _verify_success(self, login_page: LoginPage, case: dict) -> None:
        """验证成功登录流程。

        步骤:
          1. 等待弹窗出现
          2. 断言弹窗标题和内容
          3. 点击确认/取消/关闭
          4. 验证跳转到主页
        """
        popup_data = case.get("popup", {})
        popup = login_page.wait_for_popup()

        # 断言弹窗标题
        title = popup_data.get("title")
        if title:
            popup.assert_title(title)

        # 断言弹窗内容包含关键词
        content_contains = popup_data.get("content_contains")
        if content_contains:
            popup.assert_contains(content_contains)

        # 操作弹窗
        action = popup_data.get("action", "confirm")
        if action == "confirm":
            popup.confirm()
        elif action == "cancel":
            popup.cancel()
        elif action == "close":
            popup.close()

        # 确认弹窗后应跳转到主页
        login_page.assert_login_success()

    @allure.step("验证登录失败 + 错误提示断言")
    def _verify_failure(self, login_page: LoginPage, case: dict) -> None:
        """验证失败登录流程。

        步骤:
          1. 断言仍在登录页（登录未成功跳转）
          2. 如有 assert_error_contains → 验证错误消息关键词
          3. 如有 assert_no_redirect → 只验证未跳转（不检查消息内容）
        """
        # 确保仍在登录页
        login_page.assert_on_login_page()

        # 获取错误消息并附加到报告
        error_msg = login_page.get_error_message()
        allure.attach(
            error_msg or "(无可见错误消息 — 可能为前端表单校验)",
            name="实际错误提示",
            attachment_type=allure.attachment_type.TEXT,
        )

        # 如果 YAML 中指定了预期错误关键词，则断言
        expected = case.get("assert_error_contains", "")
        if expected:
            assert expected in error_msg, \
                f"期望错误包含 '{expected}'，实际错误: '{error_msg}'"
