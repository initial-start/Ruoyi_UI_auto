"""删除用户测试 — 数据驱动。

流程：新增用户 → 搜索 → 删除 → 搜索断言无结果
"""

import time

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from data.testdata_loader import parametrize_from_yaml
from testcases.conftest import dismiss_popup
from pages.system.user_management_page import UserManagementPage
from pages.system.add_user_page import AddUserPage

cases, ids = parametrize_from_yaml("delete_user_data.yaml", "delete_user_cases")


@allure.feature("用户管理")
class TestDeleteUser:

    @allure.story("删除用户")
    @pytest.mark.user_management
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_delete_user(
        self, logged_in_page: Page, config: ConfigManager, case: dict
    ) -> None:
        """删除用户：新增 → 搜索 → 删除 → 搜索断言不存在。"""
        page = logged_in_page
        uid = f"{int(time.time() * 1000) % 1000000:06d}"
        uname = f"{case['loginName']}_{uid}"
        phone = f"13800{uid}"

        # ================================================
        # Step 1: 新增一个用户（作为删除目标）
        # ================================================
        with allure.step(f"新增用户: {uname}"):
            page.goto(f"{config.base_url}/system/user/add", wait_until="domcontentloaded")
            add_page = AddUserPage(page).wait_loaded()

            add_page.fill_user_name(uname) \
                    .fill_login_name(uname) \
                    .fill_password(case["password"]) \
                    .fill_phone(phone)

            if case.get("email"):
                add_page.fill_email(case["email"])

            add_page.select_dept(case["deptName"]) \
                    .check_role(case["roleName"]) \
                    .click_submit()

            page.wait_for_timeout(2000)
            dismiss_popup(page)

        # ================================================
        # Step 3: 搜索确认用户存在
        # ================================================
        with allure.step(f"搜索用户: {uname}"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            um = UserManagementPage(page).wait_loaded()
            um.fill_login_name(uname).click_search()

            data = um.get_table_data()
            assert data and len(data) > 0, f"删除前应能搜索到 {uname}"
            allure.attach(str(data[0]), name="删除前用户数据", attachment_type=allure.attachment_type.TEXT)

        # ================================================
        # Step 4: 点击行内删除 → 断言弹窗 → 确认
        # ================================================
        with allure.step(f"删除用户: {uname}"):
            # 1. 点击行内删除按钮
            row = page.locator("tbody tr").first
            del_btn = row.locator("a:has-text('删除')").first
            del_btn.evaluate("el => el.click()")
            page.wait_for_timeout(800)

            # 2. 断言删除确认弹窗内容
            dialog = page.locator(".layui-layer-dialog:visible").first
            dialog_text = dialog.inner_text()
            allure.attach(dialog_text, name="删除确认弹窗", attachment_type=allure.attachment_type.TEXT)
            assert "确定删除该条用户信息吗" in dialog_text, \
                f"删除确认弹窗内容不符: {dialog_text}"

            # 3. 点击确定
            page.locator(".layui-layer-dialog:visible .layui-layer-btn0").first.evaluate("el => el.click()")
            page.wait_for_timeout(2000)

            # 4. 处理操作成功弹窗
            dismiss_popup(page)

        # ================================================
        # Step 5: 再次搜索，断言不存在
        # ================================================
        with allure.step(f"验证已删除: {uname}"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            um = UserManagementPage(page).wait_loaded()
            um.fill_login_name(uname).click_search()

            data = um.get_table_data()
            assert not data or len(data) == 0, \
                f"删除后不应搜索到 {uname}，实际: {len(data)} 条"

            # DB 校验 — del_flag 应为 '2'(已删除)
            from utils.db_utils import Database
            with Database(config.database) as db:
                deleted = db.query_one(
                    "SELECT login_name, del_flag FROM sys_user WHERE login_name = %s",
                    (uname,),
                )
                assert deleted and deleted["del_flag"] == "2", \
                    f"DB中 del_flag 应为'2'(已删除)，实际: {deleted}"
                allure.attach(str(deleted), name="DB删除状态", attachment_type=allure.attachment_type.TEXT)

            allure.attach(
                f"用户 {uname} 已成功删除，搜索结果为 0 条",
                name="删除验证通过",
                attachment_type=allure.attachment_type.TEXT,
            )

    # ================================================================
    # 辅助
    # ================================================================

