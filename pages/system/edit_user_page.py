"""修改用户页面对象。

URL: /system/user/edit/{userId} | 标题: 修改用户

与新增页结构相同，差异：
  - loginName 字段 readonly=true（不可修改）
  - 表单预填原始数据
"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage

INPUT_LOGIN_NAME = "input[name='loginName']"
INPUT_USER_NAME = "input[name='userName']"
INPUT_PHONE = "input[name='phonenumber']"
INPUT_EMAIL = "input[name='email']"
BTN_SUBMIT = "button.btn-primary"


class EditUserPage(BasePage):
    """修改用户页面。"""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def wait_loaded(self) -> "EditUserPage":
        self.wait_for_visible(INPUT_USER_NAME)
        return self

    def assert_login_name_readonly(self) -> "EditUserPage":
        """断言登录账户输入框只读。"""
        ro = self.locator(INPUT_LOGIN_NAME).get_attribute("readonly")
        assert ro is not None and ro != "false", \
            f"登录账户应为只读，实际 readonly={ro}"
        return self

    def fill_user_name(self, value: str) -> "EditUserPage":
        self.fill(INPUT_USER_NAME, value)
        return self

    def fill_phone(self, value: str) -> "EditUserPage":
        self.fill(INPUT_PHONE, value)
        return self

    def fill_email(self, value: str) -> "EditUserPage":
        self.fill(INPUT_EMAIL, value)
        return self

    def click_submit(self) -> "EditUserPage":
        self.locator(BTN_SUBMIT).first.evaluate("el => el.click()")
        self.page.wait_for_timeout(1500)
        return self
