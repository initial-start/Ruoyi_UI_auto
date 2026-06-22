"""新增用户测试 — 数据驱动。"""

import time

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from data.testdata_loader import parametrize_from_yaml
from pages.system.user_management_page import UserManagementPage
from pages.system.add_user_page import AddUserPage
from testcases.conftest import dismiss_popup

cases, ids = parametrize_from_yaml("add_user_data.yaml", "add_user_cases")


@allure.feature("用户管理")
class TestAddUser:

    @allure.story("新增用户")
    @pytest.mark.user_management
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_add_user(self, logged_in_page: Page, config: ConfigManager, case: dict) -> None:
        page = logged_in_page
        uid = str(int(time.time()))[-6:]
        uname = f"{case.get('loginName', '')}_{uid}"
        phone = f"13800{uid}"

        with allure.step(f"新增用户: {case['description']}"):
            page.goto(f"{config.base_url}/system/user/add", wait_until="domcontentloaded")
            add_page = AddUserPage(page).wait_loaded()
            self._fill_form(add_page, case, uname, phone)
            add_page.click_submit()
            page.wait_for_timeout(2000)

        scenario = case.get("scenario", "add")
        if scenario == "add":
            self._verify_add_success(page, config, case, uname, phone)
        elif scenario == "validate":
            self._verify_required_field(page, case)

    def _verify_add_success(self, page, config, case, uname, phone):
        dismiss_popup(page)
        with allure.step(f"验证: {uname}"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            um = UserManagementPage(page).wait_loaded()
            um.fill_login_name(uname).click_search()
            data = um.get_table_data()
            assert data and len(data) > 0, f"搜索 {uname} 应有结果"
            row = data[0]
            expected = case.get("assert", {})
            allure.attach(str(row), name="用户数据", attachment_type=allure.attachment_type.TEXT)
            assert row["loginName"] == uname
            assert row["userName"] == uname
            assert row["phonenumber"] == phone
            dept = row.get("dept", {}) or {}
            assert dept.get("deptName") == case["deptName"]
            assert row.get("createTime"), "创建时间为空"

            from utils.db_utils import Database, query_user_by_login_name
            with Database(config.database) as db:
                db_row = query_user_by_login_name(db, uname)
                assert db_row
                assert db_row["user_name"] == uname

    def _verify_required_field(self, page, case):
        field_label = case["assert_field"]
        with allure.step(f"必填校验: {field_label}"):
            assert "add" in page.url, "空字段提交不应跳转"
            name = {"用户名称": "userName", "登录账号": "loginName", "登录密码": "password"}.get(field_label, "")
            has_error = page.evaluate(
                """(name) => {
                    var el = document.querySelector(\"input[name='\" + name + \"']\");
                    if (el) {
                        if (el.validationMessage) return el.validationMessage;
                        var parent = el.closest('.form-group, .has-error');
                        if (parent && parent.classList.contains('has-error')) return 'has-error';
                        if (el.required) return 'required-attr';
                    }
                    return '';
                }""",
                name,
            )
            assert has_error, f"字段'{field_label}'应有必填校验提示"

    def _fill_form(self, add_page, case, uname, phone):
        with allure.step("填写表单"):
            if case.get("userName"): add_page.fill_user_name(uname)
            if case.get("loginName"): add_page.fill_login_name(uname)
            if case.get("password"): add_page.fill_password(case["password"])
            if case.get("phonenumber"): add_page.fill_phone(phone)
            if case.get("email"): add_page.fill_email(case["email"])
            if case.get("sex"): add_page.select_sex(case["sex"])
            if case.get("remark"): add_page.fill_remark(case["remark"])
            if case.get("deptName"): add_page.select_dept(case["deptName"])
            if case.get("roleName"): add_page.check_role(case["roleName"])
