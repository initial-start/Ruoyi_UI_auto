"""导入测试 — 数据驱动。

流程：
  import → 点击导入 → 选择文件 → 点击导入 → 断言结果
  validate → 选择非法格式文件 → 断言前端校验提示
"""

import os

import allure
import pytest
from playwright.sync_api import Page

from config.config_manager import ConfigManager
from data.testdata_loader import parametrize_from_yaml
from testcases.conftest import dismiss_popup

cases, ids = parametrize_from_yaml("import_data.yaml", "import_cases")


@allure.feature("用户管理")
class TestImportExport:

    @allure.story("导入Excel")
    @pytest.mark.user_management
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_import_excel(
        self, logged_in_page: Page, config: ConfigManager, case: dict
    ) -> None:
        """导入：点击导入 → 选择文件 → 断言结果。"""
        page = logged_in_page
        file_path = case["file_path"]
        scenario = case.get("scenario", "import")

        # ================================================
        # Step 1: 导航到用户管理页
        # ================================================
        with allure.step("进入用户管理页"):
            page.goto(f"{config.base_url}/system/user", wait_until="networkidle")
            page.wait_for_timeout(3000)

        # ================================================
        # Step 2: 点击导入 → 弹窗 → 选择文件
        # ================================================
        with allure.step(f"打开导入弹窗，选择文件: {file_path}"):
            page.locator("a.btn-info").first.evaluate("el => el.click()")
            page.wait_for_timeout(1500)

            title = page.locator(".layui-layer-title").first.inner_text().strip()
            assert "导入" in title, f"弹窗标题应含'导入'，实际: {title}"

            assert os.path.exists(file_path), f"文件不存在: {file_path}"
            page.locator("#file").first.set_input_files(file_path)
            page.wait_for_timeout(500)

        # ================================================
        # Step 3: 根据场景处理
        # ================================================
        # 正常导入 — 点击导入按钮提交
        if scenario == "import":
            with allure.step("点击导入提交"):
                page.locator(".layui-layer-btn0").first.evaluate("el => el.click()")
                page.wait_for_timeout(3000)

        # 非法格式 — 前端直接校验，不需要点导入
        if scenario == "validate":
            page.wait_for_timeout(1000)

        # ================================================
        # Step 4: 断言结果
        # ================================================
        expected = case["assert_result_contains"]
        with allure.step(f"断言结果包含: '{expected}'"):
            popup_text = page.locator(".layui-layer-dialog:visible").first.inner_text() \
                if page.locator(".layui-layer-dialog:visible").count() > 0 \
                else page.locator(".layui-layer:visible, [class*=message]:visible, [class*=tip]:visible").first.inner_text()

            allure.attach(popup_text, name="导入结果", attachment_type=allure.attachment_type.TEXT)
            assert expected in popup_text, \
                f"结果应包含 '{expected}'，实际: {popup_text}"

            dismiss_popup(page)

            # DB 校验 — 仅成功导入时查库
            if scenario == "import" and "成功" in popup_text:
                from utils.db_utils import Database
                with Database(config.database) as db:
                    count = db.count("sys_user", "create_by = %s", ("admin",))
                    allure.attach(f"DB中由admin创建的用户数: {count}", name="DB导入校验", attachment_type=allure.attachment_type.TEXT)
                    assert count > 0, "导入后DB中应有新增用户"

    # ================================================================
    # 辅助
    # ================================================================

