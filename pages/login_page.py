"""RuoYi 登录页对象。

基于 http://localhost/login 实际页面结构识别：
  - 用户名输入框:   input[name='username']  placeholder="用户名"
  - 密码输入框:     input[name='password']  placeholder="密码"
  - 记住我复选框:   input[name='rememberme']
  - 登录按钮:       button.btn.btn-success.btn-block  text="登录"
  - 图形验证码:     img (非文本输入，需要 OCR 或开发关闭)
  - 登录后弹窗:     layui 对话框 (安全提示/密码修改提醒等)
  - 错误提示:       Bootstrap alert / layui 弹窗
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.assert_utils import PopupAssert

# — 基于实际页面识别的选择器 —
USERNAME_INPUT = "input[name='username']"
PASSWORD_INPUT = "input[name='password']"
REMEMBER_CHECKBOX = "input[name='rememberme']"
LOGIN_BUTTON = "button.btn.btn-success.btn-block"

# — 错误提示（按优先级尝试） —
ERROR_SELECTORS = [
    ".alert.alert-danger",           # Bootstrap 警告框（RuoYi 默认）
    ".layui-layer-content",           # layui 弹窗
    ".el-message--error .el-message__content",  # Element UI 错误消息
    ".el-message__content",           # Element UI 通用消息
    ".error-msg",                     # 通用错误容器
]


class LoginPage(BasePage):
    """RuoYi 系统登录页面。

    用法：
        login_page = LoginPage(page)
        main_page = login_page.navigate(url).login("admin", "admin123")
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ————————————————————————————————————————
    # 导航 & 等待
    # ————————————————————————————————————————

    @allure.step("打开登录页: {url}")
    def navigate(self, url: str) -> "LoginPage":
        """导航到登录页并等待登录表单加载完成。"""
        super().navigate(url)
        self.wait_for_login_form()
        return self

    def wait_for_login_form(self) -> "LoginPage":
        """等待登录表单渲染完成。"""
        self.wait_for_visible(USERNAME_INPUT)
        self.wait_for_visible(PASSWORD_INPUT)
        self.wait_for_visible(LOGIN_BUTTON)
        return self

    # ————————————————————————————————————————
    # 表单操作
    # ————————————————————————————————————————

    @allure.step("输入用户名: {username}")
    def fill_username(self, username: str) -> "LoginPage":
        """填写用户名。"""
        self.fill(USERNAME_INPUT, username)
        return self

    @allure.step("输入密码")
    def fill_password(self, password: str) -> "LoginPage":
        """填写密码。"""
        self.fill(PASSWORD_INPUT, password)
        return self

    # 注意：此 RuoYi 实例使用图形验证码（img 标签），非文本输入。
    # 自动化测试前需要在 RuoYi 后台关闭验证码，或接入 OCR 识别。
    # 关闭方式：application.yml → captchaType: false 或 math

    @allure.step("勾选'记住我'")
    def check_remember_me(self) -> "LoginPage":
        """勾选'记住我'复选框。"""
        if self.locator(REMEMBER_CHECKBOX).count() > 0:
            self.check(REMEMBER_CHECKBOX)
        return self

    # ————————————————————————————————————————
    # 动作
    # ————————————————————————————————————————

    @allure.step("点击登录按钮")
    def click_login(self) -> "LoginPage":
        """点击登录按钮。"""
        self.click(LOGIN_BUTTON)
        return self

    @allure.step("执行登录: {username} / ****")
    def login(self, username: str, password: str) -> "LoginPage":
        """执行登录流程（不处理弹出框，适用于错误用例）。

        Args:
            username: 用户名
            password: 密码
        """
        self.fill_username(username)\
            .fill_password(password)\
            .click_login()
        self.page.wait_for_load_state("networkidle")
        return self

    # ————————————————————————————————————————
    # 登录后弹窗处理
    # ————————————————————————————————————————

    @allure.step("等待登录后弹窗")
    def wait_for_popup(self, timeout: int = 5000) -> PopupAssert:
        """等待登录后出现的 layui 弹窗，返回断言器。

        登录成功后 RuoYi 可能弹出安全提示等弹窗，
        通过返回的 PopupAssert 可以断言内容并操作。

        Returns:
            PopupAssert 实例，支持链式断言和操作

        Usage:
            login_page.login("admin", "admin123")
            popup = login_page.wait_for_popup()
            popup.assert_title("安全提示") \
                 .assert_contains("初始密码") \
                 .confirm()
        """
        popup = PopupAssert(self.page)
        popup.wait_for_popup(timeout)
        return popup

    @allure.step("登录并处理安全弹窗: {username}")
    def login_and_handle_popup(
        self, username: str, password: str, popup_confirm: bool = True
    ) -> "LoginPage":
        """执行登录并自动处理登录后的弹窗。

        完整流程：填写凭据 → 点击登录 → 等待弹窗 → 断言 → 确认 → 等待跳转。

        Args:
            username: 用户名
            password: 密码
            popup_confirm: 是否自动点击弹窗确认按钮（默认 True）

        Returns:
            self
        """
        self.fill_username(username)\
            .fill_password(password)\
            .click_login()

        # 等待弹窗出现
        popup = PopupAssert(self.page)
        popup.wait_for_popup()

        # 记录弹窗内容到 Allure
        title = popup.get_title()
        content = popup.get_content()
        allure.attach(
            f"弹窗标题: {title}\n弹窗内容: {content}",
            name="登录弹窗信息",
            attachment_type=allure.attachment_type.TEXT,
        )

        if popup_confirm:
            popup.confirm()
            # 确认后等待跳转到主页
            self.page.wait_for_load_state("networkidle")

        return self

    # ————————————————————————————————————————
    # 验证
    # ————————————————————————————————————————

    @allure.step("获取错误消息")
    def get_error_message(self) -> str:
        """获取登录失败的提示信息。

        按优先级尝试多种错误提示容器，
        匹配到第一个可见且有文本的元素即返回。

        Returns:
            错误提示文本，如果没有找到则返回空字符串
        """
        for selector in ERROR_SELECTORS:
            loc = self.locator(selector)
            if loc.count() > 0 and loc.first.is_visible():
                text = loc.first.inner_text().strip()
                if text:
                    return text
        return ""

    @allure.step("断言登录成功 — 已跳转到主页")
    def assert_login_success(self) -> "LoginPage":
        """断言登录成功：URL 不再包含 login。"""
        # 等待离开登录页
        self.page.wait_for_url("**/index**", timeout=10_000)
        return self

    @allure.step("断言登录失败 — 提示: {expected_error}")
    def assert_login_error(self, expected_error: str) -> "LoginPage":
        """断言登录失败并验证错误提示。

        Args:
            expected_error: 期望的错误提示关键词
        """
        error_msg = self.get_error_message()
        assert expected_error in error_msg, \
            f"期望错误包含 '{expected_error}'，实际错误: '{error_msg}'"
        return self

    @allure.step("断言仍在登录页")
    def assert_on_login_page(self) -> "LoginPage":
        """断言当前仍在登录页面。"""
        self.assert_visible(LOGIN_BUTTON)
        return self
