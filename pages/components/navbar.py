"""顶部导航栏组件。

RuoYi 顶部导航栏包含：
  - 系统 Logo / 标题
  - 折叠/展开侧边栏按钮
  - 用户头像 & 下拉菜单（个人中心、退出登录等）
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

# RuoYi 导航栏选择器
NAVBAR = ".navbar, .main-header, .navbar-header"
NAV_TOGGLE_BTN = ".navbar-toggle, .sidebar-toggle, .hamburger"
USER_DROPDOWN = ".user-menu, .navbar-right .dropdown, .navbar-user"
LOGOUT_BTN = "text=退出登录, a:has-text('退出')"
USER_NAME = ".user-menu span, .navbar-right .username"


class Navbar(BasePage):
    """顶部导航栏。"""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("折叠/展开侧边栏")
    def toggle_sidebar(self) -> "Navbar":
        """点击侧边栏折叠/展开按钮。"""
        self.click(NAV_TOGGLE_BTN)
        return self

    @allure.step("获取当前登录用户名")
    def get_username(self) -> str:
        """获取导航栏上显示的用户名。"""
        return self.get_text(USER_NAME).strip()

    @allure.step("退出登录")
    def logout(self) -> "Navbar":
        """展开用户菜单，点击退出登录。"""
        self.click(USER_DROPDOWN)
        self.click(LOGOUT_BTN)
        return self

    def assert_loaded(self) -> "Navbar":
        """断言导航栏已加载。"""
        self.assert_visible(NAVBAR)
        return self
