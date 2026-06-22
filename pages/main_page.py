"""主页/仪表盘页面对象。

登录成功后的主页面，包含：
  - 顶部导航栏 (Navbar)
  - 左侧菜单栏 (Sidebar)
  - 主内容区域（仪表盘、标签页等）

用法：
    main = MainPage(page)
    main.wait_loaded()
    main.sidebar.navigate_to("系统管理", "用户管理")
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components.navbar import Navbar
from pages.components.sidebar import Sidebar

# RuoYi 主页内容区域选择器
MAIN_CONTENT = ".main-content, .content-wrapper, .app-main"
WELCOME_SECTION = ".welcome, .dashboard, .home-main"
TAB_BAR = ".tags-view, .tabs-view"
PAGE_IFRAME = "iframe"


class MainPage(BasePage):
    """RuoYi 主页（登录后仪表盘）。"""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.navbar = Navbar(page)
        self.sidebar = Sidebar(page)

    # ————————————————————————————————————————
    # 等待 & 断言
    # ————————————————————————————————————————

    @allure.step("等待主页加载完成")
    def wait_loaded(self) -> "MainPage":
        """等待主页核心元素加载完成。"""
        self.navbar.assert_loaded()
        self.wait_for_visible(MAIN_CONTENT)
        return self

    def assert_loaded(self) -> "MainPage":
        """断言主页已成功加载。"""
        self.navbar.assert_loaded()
        self.assert_visible(MAIN_CONTENT)
        return self

    # ————————————————————————————————————————
    # 导航
    # ————————————————————————————————————————

    @allure.step("导航到: {' → '.join(menu_items)}")
    def navigate_to(self, *menu_items: str) -> "MainPage":
        """通过侧边栏导航到指定功能页面。

        Args:
            menu_items: 菜单路径，如 ("系统管理", "用户管理")
        """
        self.sidebar.navigate_to(*menu_items)
        return self

    @allure.step("切换到标签页: {tab_title}")
    def switch_tab(self, tab_title: str) -> "MainPage":
        """切换到已打开的标签页。"""
        tab = self.page.locator(f".tags-view-item:has-text('{tab_title}')").first
        tab.click()
        return self

    @allure.step("关闭标签页: {tab_title}")
    def close_tab(self, tab_title: str) -> "MainPage":
        """关闭指定标签页。"""
        tab = self.page.locator(
            f".tags-view-item:has-text('{tab_title}') .el-icon-close"
        ).first
        tab.click()
        return self

    # ————————————————————————————————————————
    # 用户操作
    # ————————————————————————————————————————

    @allure.step("退出登录")
    def logout(self) -> "MainPage":
        """通过导航栏退出登录。"""
        self.navbar.logout()
        return self

    def get_username(self) -> str:
        """获取当前登录用户名。"""
        return self.navbar.get_username()
