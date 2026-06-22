"""断言工具 — 封装 RuoYi 常见弹窗/提示的断言操作。

基于实际页面 DOM 结构识别：
  - layui 对话框：安全提示、错误警告等模态弹窗
  - Element UI 消息条：操作成功/失败的轻量提示
"""

from __future__ import annotations

import logging
import allure
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


# ================================================================
# layui 弹窗相关选择器
# ================================================================

# layui 对话框（模态弹窗）
LAYER_DIALOG = ".layui-layer-dialog"
LAYER_TITLE = ".layui-layer-title"
LAYER_CONTENT = ".layui-layer-content"
LAYER_BTN_CONFIRM = ".layui-layer-btn0"  # 确认按钮
LAYER_BTN_CANCEL = ".layui-layer-btn1"   # 取消按钮
LAYER_CLOSE = ".layui-layer-close"       # 右上角 X

# Element UI 消息条
EL_MESSAGE = ".el-message"
EL_MESSAGE_SUCCESS = ".el-message--success .el-message__content"
EL_MESSAGE_ERROR = ".el-message--error .el-message__content"
EL_MESSAGE_WARNING = ".el-message--warning .el-message__content"


class PopupAssert:
    """弹窗断言器 — 用于验证和操作 RuoYi 的 layui 弹窗。

    用法：
        popup = PopupAssert(page)
        popup.assert_title("安全提示") \
             .assert_contains("初始密码") \
             .confirm()
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self._dialog_selector = LAYER_DIALOG

    # ————————————————————————————————————————
    # 等待
    # ————————————————————————————————————————

    @allure.step("等待弹窗出现")
    def wait_for_popup(self, timeout: int = 5000) -> "PopupAssert":
        """等待 layui 弹窗出现在页面上。"""
        self.page.wait_for_selector(LAYER_DIALOG, state="visible", timeout=timeout)
        return self

    @allure.step("等待弹窗关闭")
    def wait_for_close(self, timeout: int = 5000) -> "PopupAssert":
        """等待 layui 弹窗从页面上消失。"""
        self.page.wait_for_selector(LAYER_DIALOG, state="hidden", timeout=timeout)
        return self

    # ————————————————————————————————————————
    # 标题断言
    # ————————————————————————————————————————

    @allure.step("断言弹窗标题: {expected}")
    def assert_title(self, expected: str) -> "PopupAssert":
        """断言弹窗标题等于指定文本。

        Args:
            expected: 期望的标题文本
        """
        title = self.page.locator(LAYER_TITLE).first
        expect(title).to_contain_text(expected)
        logger.info(f"弹窗标题断言通过: {expected}")
        return self

    # ————————————————————————————————————————
    # 内容断言
    # ————————————————————————————————————————

    @allure.step("断言弹窗包含: {expected}")
    def assert_contains(self, expected: str) -> "PopupAssert":
        """断言弹窗内容包含指定文本（关键词匹配）。

        Args:
            expected: 期望包含的关键词
        """
        content = self.page.locator(LAYER_CONTENT).first
        expect(content).to_contain_text(expected)
        logger.info(f"弹窗内容断言通过: 包含 '{expected}'")
        return self

    @allure.step("断言弹窗不包含: {expected}")
    def assert_not_contains(self, expected: str) -> "PopupAssert":
        """断言弹窗内容不包含指定文本。

        Args:
            expected: 不应出现的关键词
        """
        content = self.page.locator(LAYER_CONTENT).first
        expect(content).not_to_contain_text(expected)
        return self

    @allure.step("断言弹窗精确文本: {expected}")
    def assert_text_equals(self, expected: str) -> "PopupAssert":
        """断言弹窗内容精确匹配指定文本。

        Args:
            expected: 期望的完整文本
        """
        content = self.page.locator(LAYER_CONTENT).first
        expect(content).to_have_text(expected)
        logger.info(f"弹窗文本精确断言通过: {expected}")
        return self

    @allure.step("断言弹窗内容匹配: {pattern}")
    def assert_text_matches(self, pattern: str) -> "PopupAssert":
        """断言弹窗内容匹配正则表达式。

        Args:
            pattern: 正则表达式模式
        """
        content = self.page.locator(LAYER_CONTENT).first
        expect(content).to_have_text(pattern)
        return self

    # ————————————————————————————————————————
    # 操作
    # ————————————————————————————————————————

    @allure.step("点击弹窗确认按钮")
    def confirm(self) -> "PopupAssert":
        """点击弹窗的确认按钮（关闭弹窗）。"""
        btn = self.page.locator(LAYER_BTN_CONFIRM).first
        btn.click()
        self.page.wait_for_timeout(500)  # 过渡动画
        return self

    @allure.step("点击弹窗取消按钮")
    def cancel(self) -> "PopupAssert":
        """点击弹窗的取消按钮。"""
        btn = self.page.locator(LAYER_BTN_CANCEL).first
        btn.click()
        return self

    @allure.step("点击弹窗关闭按钮(X)")
    def close(self) -> "PopupAssert":
        """点击弹窗右上角的关闭按钮。"""
        btn = self.page.locator(LAYER_CLOSE).first
        btn.click()
        return self

    # ————————————————————————————————————————
    # 信息获取
    # ————————————————————————————————————————

    def get_title(self) -> str:
        """获取弹窗标题文本。"""
        return self.page.locator(LAYER_TITLE).first.inner_text().strip()

    def get_content(self) -> str:
        """获取弹窗正文内容（不含图标文本）。"""
        return self.page.locator(LAYER_CONTENT).first.inner_text().strip()

    def is_visible(self) -> bool:
        """弹窗当前是否可见。"""
        return self.page.locator(LAYER_DIALOG).is_visible()


# ================================================================
# Element UI 消息条断言（非模态提示）
# ================================================================


class MessageAssert:
    """Element UI 消息条断言器 — 轻量级操作结果提示。

    用法：
        msg = MessageAssert(page)
        msg.assert_success_contains("操作成功")
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    @allure.step("断言成功消息包含: {expected}")
    def assert_success_contains(self, expected: str) -> "MessageAssert":
        """断言出现成功消息条并包含指定文本。"""
        el = self.page.locator(EL_MESSAGE_SUCCESS).first
        expect(el).to_contain_text(expected)
        return self

    @allure.step("断言错误消息包含: {expected}")
    def assert_error_contains(self, expected: str) -> "MessageAssert":
        """断言出现错误消息条并包含指定文本。"""
        el = self.page.locator(EL_MESSAGE_ERROR).first
        expect(el).to_contain_text(expected)
        return self

    @allure.step("断言警告消息包含: {expected}")
    def assert_warning_contains(self, expected: str) -> "MessageAssert":
        """断言出现警告消息条并包含指定文本。"""
        el = self.page.locator(EL_MESSAGE_WARNING).first
        expect(el).to_contain_text(expected)
        return self

    def get_message_text(self) -> str:
        """获取消息条文本（通用，取第一个出现的）。"""
        el = self.page.locator(EL_MESSAGE).first
        return el.inner_text().strip() if el.count() > 0 else ""


# ================================================================
# 组合断言工具（便捷入口）
# ================================================================


def assert_popup(page: Page) -> PopupAssert:
    """获取弹窗断言器（layui 对话框）。"""
    return PopupAssert(page)


def assert_message(page: Page) -> MessageAssert:
    """获取消息条断言器（Element UI）。"""
    return MessageAssert(page)
