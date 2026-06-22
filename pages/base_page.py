"""BasePage — 所有页面对象的基类。

设计原则：
  - 零 time.sleep()：依赖 Playwright 自动等待 + 显式状态等待
  - 链式调用：所有交互方法返回 self
  - Allure 集成：关键操作自动记录到报告
  - 类型安全：完整类型标注

用法：
    class MyPage(BasePage):
        def do_something(self) -> "MyPage":
            self.click("button.submit")
            return self
"""

from __future__ import annotations

import logging
from typing import Any

import allure
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger(__name__)


class BasePage:
    """页面对象基类。

    封装 Playwright Page 的常用操作，提供：
      - 导航与等待
      - 元素交互（点击、输入、选择）
      - 断言辅助
      - 截图与脚本执行
    """

    def __init__(self, page: Page) -> None:
        """初始化页面对象。

        Args:
            page: Playwright Page 实例（通常由 pytest-playwright 的 page fixture 注入）
        """
        self.page = page

    # ————————————————————————————————————————
    # 导航 & 等待
    # ————————————————————————————————————————

    @allure.step("导航到: {url}")
    def navigate(self, url: str) -> "BasePage":
        """导航到指定 URL，等待 DOM 加载完成。"""
        self.page.goto(url, wait_until="domcontentloaded")
        logger.info(f"已导航到: {url}")
        return self

    def wait_for_url(self, pattern: str, timeout: int | None = None) -> "BasePage":
        """等待 URL 匹配指定模式。

        Args:
            pattern: URL 匹配模式（支持通配符 * 和正则）
            timeout: 超时 (ms)，默认使用全局配置
        """
        self.page.wait_for_url(pattern, timeout=timeout)
        return self

    def wait_for_load_state(self, state: str = "networkidle") -> "BasePage":
        """等待页面达到指定加载状态。

        Args:
            state: 'load' | 'domcontentloaded' | 'networkidle'
        """
        self.page.wait_for_load_state(state)
        return self

    def reload(self) -> "BasePage":
        """刷新页面并等待 DOM 就绪。"""
        self.page.reload(wait_until="domcontentloaded")
        return self

    # ————————————————————————————————————————
    # 元素查找
    # ————————————————————————————————————————

    def locator(self, selector: str) -> Locator:
        """获取元素定位器。

        支持 Playwright 选择器语法:
          - CSS: "button.primary", "#loginBtn"
          - 文本: "text=登录"
          - 组合: "button:has-text('搜索')"
          - XPath: "xpath=//button"  (不推荐，仅在 CSS 无法表达时使用)

        Returns:
            Playwright Locator 对象
        """
        return self.page.locator(selector)

    def get_by_role(self, role: str, **kwargs) -> Locator:
        """按 ARIA role 定位元素（推荐优先使用，稳定性最好）。"""
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        """按可见文本定位元素。"""
        return self.page.get_by_text(text, exact=exact)

    def get_by_label(self, label: str) -> Locator:
        """按 label 文本定位关联的表单控件。"""
        return self.page.get_by_label(label)

    def get_by_placeholder(self, placeholder: str) -> Locator:
        """按 placeholder 属性定位输入框。"""
        return self.page.get_by_placeholder(placeholder)

    # ————————————————————————————————————————
    # 元素交互
    # ————————————————————————————————————————

    @allure.step("点击: {selector}")
    def click(self, selector: str, timeout: int | None = None) -> "BasePage":
        """点击元素（自动等待可见且可点击）。"""
        self.locator(selector).click(timeout=timeout)
        logger.debug(f"点击元素: {selector}")
        return self

    @allure.step("双击: {selector}")
    def double_click(self, selector: str) -> "BasePage":
        """双击元素。"""
        self.locator(selector).dblclick()
        return self

    @allure.step("右键点击: {selector}")
    def right_click(self, selector: str) -> "BasePage":
        """右键点击元素。"""
        self.locator(selector).click(button="right")
        return self

    @allure.step("输入: {selector} ← {value}")
    def fill(self, selector: str, value: str) -> "BasePage":
        """填充输入框。

        Playwright fill() 内置三步操作：
          1. 聚焦元素
          2. 清空现有内容
          3. 输入新值并触发 input/change 事件

        无需额外调用 clear()。
        """
        self.locator(selector).fill(value)
        return self

    @allure.step("逐字输入: {selector} ← {value}")
    def type(self, selector: str, value: str, delay: int = 50) -> "BasePage":
        """逐字符输入（模拟键盘打字，触发 keydown/keyup 事件）。

        适用于有实时验证、自动补全等需要逐字触发的输入框。
        """
        self.locator(selector).type(value, delay=delay)
        return self

    @allure.step("选择下拉: {selector} = {value}")
    def select_option(self, selector: str, value: str | list[str]) -> "BasePage":
        """选择 <select> 下拉框选项。

        Args:
            selector: select 元素选择器
            value: option 的 value 属性值（字符串或字符串列表）
        """
        self.locator(selector).select_option(value)
        return self

    @allure.step("勾选复选框: {selector}")
    def check(self, selector: str) -> "BasePage":
        """勾选复选框。"""
        self.locator(selector).check()
        return self

    @allure.step("取消勾选: {selector}")
    def uncheck(self, selector: str) -> "BasePage":
        """取消勾选复选框。"""
        self.locator(selector).uncheck()
        return self

    @allure.step("按键盘: {key}")
    def press_key(self, key: str) -> "BasePage":
        """在当前焦点元素按键盘按键。

        Args:
            key: 按键名称，如 'Enter', 'Escape', 'Tab', 'ArrowDown'
        """
        self.page.keyboard.press(key)
        return self

    def hover(self, selector: str) -> "BasePage":
        """鼠标悬停。"""
        self.locator(selector).hover()
        return self

    def drag_to(self, source: str, target: str) -> "BasePage":
        """拖拽元素。"""
        self.locator(source).drag_to(self.locator(target))
        return self

    # ————————————————————————————————————————
    # 等待方法
    # ————————————————————————————————————————

    def wait_for_visible(self, selector: str, timeout: int | None = None) -> "BasePage":
        """等待元素可见。"""
        self.locator(selector).wait_for(state="visible", timeout=timeout)
        return self

    def wait_for_hidden(self, selector: str, timeout: int | None = None) -> "BasePage":
        """等待元素隐藏（适用于 loading 遮罩、toast 等）。"""
        self.locator(selector).wait_for(state="hidden", timeout=timeout)
        return self

    def wait_for_enabled(self, selector: str, timeout: int | None = None) -> "BasePage":
        """等待元素可用（非 disabled）。"""
        self.locator(selector).wait_for(state="attached", timeout=timeout)
        expect(self.locator(selector)).to_be_enabled(timeout=timeout)
        return self

    def wait_for_detached(self, selector: str, timeout: int | None = None) -> "BasePage":
        """等待元素从 DOM 中移除。"""
        self.locator(selector).wait_for(state="detached", timeout=timeout)
        return self

    def wait_for_timeout(self, milliseconds: int) -> "BasePage":
        """纯时间等待（仅用于 CSS 动画/过渡等无法用状态等待的场景）。

        ⚠️ 不推荐常规使用，优先使用 wait_for_visible/wait_for_hidden 等状态等待方法。
        """
        self.page.wait_for_timeout(milliseconds)
        return self

    # ————————————————————————————————————————
    # 断言
    # ————————————————————————————————————————

    @allure.step("断言可见: {selector}")
    def assert_visible(self, selector: str, message: str = "") -> "BasePage":
        """断言元素可见。"""
        expect(self.locator(selector)).to_be_visible()
        return self

    @allure.step("断言隐藏: {selector}")
    def assert_hidden(self, selector: str) -> "BasePage":
        """断言元素不可见或不存在。"""
        expect(self.locator(selector)).to_be_hidden()
        return self

    @allure.step("断言文本包含: {selector} 包含 '{text}'")
    def assert_text(self, selector: str, text: str) -> "BasePage":
        """断言元素文本包含指定内容。"""
        expect(self.locator(selector)).to_contain_text(text)
        return self

    @allure.step("断言文本精确: {selector} == '{text}'")
    def assert_exact_text(self, selector: str, text: str) -> "BasePage":
        """断言元素文本精确匹配。"""
        expect(self.locator(selector)).to_have_text(text)
        return self

    @allure.step("断言属性: {selector}[{name}] = {value}")
    def assert_attribute(self, selector: str, name: str, value: str) -> "BasePage":
        """断言元素的属性值。"""
        expect(self.locator(selector)).to_have_attribute(name, value)
        return self

    @allure.step("断言计数值: {selector} 数量 = {count}")
    def assert_count(self, selector: str, count: int) -> "BasePage":
        """断言匹配选择器的元素数量。"""
        expect(self.locator(selector)).to_have_count(count)
        return self

    @allure.step("断言已勾选: {selector}")
    def assert_checked(self, selector: str) -> "BasePage":
        """断言复选框已勾选。"""
        expect(self.locator(selector)).to_be_checked()
        return self

    # ————————————————————————————————————————
    # 信息获取
    # ————————————————————————————————————————

    def get_text(self, selector: str) -> str:
        """获取元素内部文本。"""
        return self.locator(selector).inner_text()

    def get_input_value(self, selector: str) -> str:
        """获取输入框当前值。"""
        return self.locator(selector).input_value()

    def get_attribute(self, selector: str, name: str) -> str | None:
        """获取元素属性值。"""
        return self.locator(selector).get_attribute(name)

    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见。"""
        return self.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用。"""
        return self.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        """检查复选框是否勾选。"""
        return self.locator(selector).is_checked()

    def count(self, selector: str) -> int:
        """返回匹配选择器的元素数量。"""
        return self.locator(selector).count()

    # ————————————————————————————————————————
    # 弹窗 & 对话框
    # ————————————————————————————————————————

    def accept_dialog(self) -> "BasePage":
        """接受浏览器原生弹窗 (alert/confirm)。"""
        self.page.on("dialog", lambda d: d.accept())
        return self

    def dismiss_dialog(self) -> "BasePage":
        """取消浏览器原生弹窗。"""
        self.page.on("dialog", lambda d: d.dismiss())
        return self

    # ————————————————————————————————————————
    # 截图 & 脚本
    # ————————————————————————————————————————

    def screenshot(self, name: str, full_page: bool = True) -> bytes:
        """截取页面截图，返回 PNG 字节数据。"""
        return self.page.screenshot(path=None, full_page=full_page)

    def execute_script(self, script: str, *args) -> Any:
        """执行 JavaScript 脚本。"""
        return self.page.evaluate(script, *args)

    def scroll_to(self, selector: str) -> "BasePage":
        """滚动到指定元素（JS 方式）。"""
        self.locator(selector).scroll_into_view_if_needed()
        return self

    # ————————————————————————————————————————
    # Iframe
    # ————————————————————————————————————————

    def switch_to_iframe(self, selector: str) -> "BasePage":
        """切换到 iframe 内操作（创建新的 BasePage 代理）。"""
        frame = self.page.frame_locator(selector)
        # 创建一个新的 BasePage 包装 frame
        proxy = object.__new__(BasePage)
        proxy.page = frame
        return proxy
