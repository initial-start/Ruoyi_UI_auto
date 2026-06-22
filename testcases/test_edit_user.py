"""修改用户测试 — 数据驱动。

流程：新增 → 搜索 → 复选框状态断言 → 修改 → 验证
  - 单个复选框勾选 → 修改按钮可用
  - 多个复选框勾选 → 修改按钮不可用
  - 编辑页 loginName 只读断言
"""

import time

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from data.testdata_loader import parametrize_from_yaml
from pages.system.user_management_page import UserManagementPage
from pages.system.add_user_page import AddUserPage
from pages.system.edit_user_page import EditUserPage
from testcases.conftest import dismiss_popup

cases, ids = parametrize_from_yaml("edit_user_data.yaml", "edit_user_cases")


@allure.feature("用户管理")
class TestEditUser:

    @allure.story("修改用户")
    @pytest.mark.user_management
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_edit_user(
        self, logged_in_page: Page, config: ConfigManager, case: dict
    ) -> None:
        """修改用户：新增 → checkbox断言 → 编辑页只读断言 → 修改 → 验证。"""
        page = logged_in_page
        uid = f"{int(time.time() * 1000) % 1000000:06d}"
        init = case["init"]
        uname = f"{init['loginName']}_{uid}"
        phone = f"13800{uid[-6:]}"


        # ================================================
        # Step 2: 新增一个用户
        # ================================================
        with allure.step(f"新增用户: {uname}"):
            page.goto(f"{config.base_url}/system/user/add", wait_until="domcontentloaded")
            add_page = AddUserPage(page).wait_loaded()

            add_page.fill_user_name(uname) \
                    .fill_login_name(uname) \
                    .fill_password(init["password"]) \
                    .fill_phone(phone) \
                    .select_dept(init["deptName"]) \
                    .check_role(init["roleName"]) \
                    .click_submit()

            page.wait_for_timeout(2000)
            dismiss_popup(page)

        # ================================================
        # Step 3: 搜索用户 → checkbox 状态断言
        # ================================================
        with allure.step(f"搜索用户 + checkbox断言: {uname}"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            um = UserManagementPage(page).wait_loaded()
            um.fill_login_name(uname).click_search()

            data = um.get_table_data()
            assert data and len(data) > 0, f"应搜索到 {uname}"
            user_id = data[0].get("userId")

            # 断言1: 不勾选时修改按钮 disabled
            cls = page.locator("a.btn-primary.single").first.get_attribute("class") or ""
            assert "disabled" in cls, "未勾选时修改按钮应为disabled"

            # 勾选1行 → 修改按钮可用
            page.locator("tbody input[name='btSelectItem']").first.click()
            page.wait_for_timeout(300)
            cls = page.locator("a.btn-primary.single").first.get_attribute("class") or ""
            assert "disabled" not in cls, "勾选1行后修改按钮应可用"

            allure.attach(
                f"✓ 勾选1行: 修改按钮已启用 (class={cls})",
                name="单个复选框断言",
                attachment_type=allure.attachment_type.TEXT,
            )

            # 勾选2行 → 修改按钮 disabled（如果有≥2行数据）
            checkboxes = page.locator("tbody input[name='btSelectItem']").all()
            if len(checkboxes) >= 2:
                checkboxes[1].click()
                page.wait_for_timeout(300)
                cls = page.locator("a.btn-primary.single").first.get_attribute("class") or ""
                assert "disabled" in cls, "勾选2行后修改按钮应为disabled"

                allure.attach(
                    "✓ 勾选2行: 修改按钮已禁用",
                    name="多个复选框断言",
                    attachment_type=allure.attachment_type.TEXT,
                )

                # 取消第2个勾选
                checkboxes[1].click()
                page.wait_for_timeout(200)

        # ================================================
        # Step 4: 点击修改 → 编辑页断言
        # ================================================
        with allure.step("进入修改页面"):
            page.locator("a.btn-primary.single").first.evaluate("el => el.click()")
            page.wait_for_timeout(3000)

            # 如果没跳转，用直接 URL
            if "edit" not in page.url:
                page.goto(f"{config.base_url}/system/user/edit/{user_id}",
                          wait_until="domcontentloaded")
                page.wait_for_timeout(1500)

            assert "edit" in page.url, f"应在编辑页，实际URL: {page.url}"

            edit_page = EditUserPage(page).wait_loaded()

            # 断言 loginName 只读
            edit_page.assert_login_name_readonly()
            allure.attach(
                "loginName 字段为 readonly，不可修改",
                name="登录账户只读断言",
                attachment_type=allure.attachment_type.TEXT,
            )

        # ================================================
        # Step 5: 修改字段并提交
        # ================================================
        edit_data = case["edit"]
        with allure.step(f"修改字段: {edit_data}"):
            if "userName" in edit_data:
                edit_page.fill_user_name(edit_data["userName"])

            edit_page.click_submit()
            page.wait_for_timeout(2000)
            dismiss_popup(page)

        # ================================================
        # Step 6: 验证修改结果
        # ================================================
        expected = case["assert"]
        with allure.step(f"验证修改: {expected}"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            um = UserManagementPage(page).wait_loaded()
            um.fill_login_name(uname).click_search()

            data = um.get_table_data()
            assert data and len(data) > 0, f"应搜索到 {uname}"
            row = data[0]

            allure.attach(str(row), name="修改后用户数据", attachment_type=allure.attachment_type.TEXT)

            for field, value in expected.items():
                if field == "loginName":
                    assert row["loginName"] == uname, \
                        f"登录名={row['loginName']} ≠ {uname}"
                elif field == "userName":
                    assert row["userName"] == value, \
                        f"用户名={row['userName']} ≠ {value}"

            # DB 校验
            from utils.db_utils import Database, query_user_by_login_name
            with Database(config.database) as db:
                db_row = query_user_by_login_name(db, uname)
                assert db_row, f"DB中应存在 login_name='{uname}' 的用户"
                assert db_row["user_name"] == expected.get("userName", uname)
                allure.attach(str(db_row), name="DB修改后数据", attachment_type=allure.attachment_type.TEXT)

    # ================================================================
    # 辅助
    # ================================================================

