"""通用 CRUD 数据表格组件（模板，待集成）。

封装 RuoYi 系统中常用的数据表格操作：
  - 搜索区域 + 查询/重置按钮
  - 表格主体（分页、行操作）

注意：当前仅作为模板参考。user_management_page.py 已内联实现相同功能。
后续添加角色/菜单/部门等模块时，应将此类作为基类复用，消除重复。

  - 新增/编辑对话框
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

# RuoYi 表格区域选择器
SEARCH_FORM = ".search-form, .el-form, form.search"
TABLE = ".table, .el-table, table.table"
TABLE_BODY = f"{TABLE} tbody, {TABLE} .el-table__body"
TABLE_ROWS = f"{TABLE_BODY} tr, {TABLE_BODY} .el-table__row"
SEARCH_BTN = "button:has-text('搜索'), button:has-text('查询')"
RESET_BTN = "button:has-text('重置'), button:has-text('清空')"
ADD_BTN = "button:has-text('新增'), button:has-text('添加')"
PAGINATION = ".pagination, .el-pagination"
DIALOG = ".el-dialog, .modal, .modal-dialog"
DIALOG_TITLE = f"{DIALOG} .el-dialog__title, {DIALOG} .modal-title"
DIALOG_CONFIRM = f"{DIALOG} button:has-text('确定'), {DIALOG} button:has-text('保存')"
DIALOG_CANCEL = f"{DIALOG} button:has-text('取消'), {DIALOG} button:has-text('关闭')"


class DataTable(BasePage):
    """通用数据表格组件。

    封装 RuoYi 中常见的搜索 + 表格 + 对话框 CRUD 流程。

    用法：
        table = DataTable(page)
        table.search(username="admin")
        table.click_add()
        # ... 填写对话框表单 ...
        table.confirm_dialog()
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ————————————————————————————————————————
    # 搜索
    # ————————————————————————————————————————

    @allure.step("搜索: {kwargs}")
    def search(self, **field_values: str) -> "DataTable":
        """填充搜索表单并点击查询。

        Args:
            **field_values: 字段名=值，如 status="0", userName="admin"

        字段名对应 RuoYi 搜索表单中 input/select 的 name 或 placeholder。
        """
        for name, value in field_values.items():
            # 尝试通过 name 属性或 placeholder 定位输入框
            loc = self.page.locator(
                f"input[name='{name}'], "
                f"input[placeholder*='{name}'], "
                f"select[name='{name}']"
            ).first

            if loc.count() == 0:
                continue

            tag = loc.evaluate("el => el.tagName").lower()
            if tag == "select":
                loc.select_option(value)
            else:
                loc.clear()
                loc.fill(value)

        self.click(SEARCH_BTN)
        self.page.wait_for_load_state("networkidle")
        self.wait_for_load()
        return self

    @allure.step("重置搜索条件")
    def reset_search(self) -> "DataTable":
        """点击重置按钮清空搜索条件。"""
        self.click(RESET_BTN)
        return self

    # ————————————————————————————————————————
    # 表格操作
    # ————————————————————————————————————————

    @allure.step("点击新增按钮")
    def click_add(self) -> "DataTable":
        """点击新增按钮。"""
        self.click(ADD_BTN)
        self.wait_for_dialog()
        return self

    @allure.step("编辑第 {row_index} 行")
    def click_edit(self, row_index: int) -> "DataTable":
        """点击指定行的编辑按钮。

        Args:
            row_index: 行索引（从 0 开始）
        """
        edit_btn = self.page.locator(TABLE_ROWS).nth(row_index)\
            .locator("button:has-text('编辑'), a:has-text('修改')").first
        edit_btn.click()
        self.wait_for_dialog()
        return self

    @allure.step("删除第 {row_index} 行")
    def click_delete(self, row_index: int) -> "DataTable":
        """点击指定行的删除按钮（弹出确认框）。"""
        del_btn = self.page.locator(TABLE_ROWS).nth(row_index)\
            .locator("button:has-text('删除'), a:has-text('删除')").first
        del_btn.click()
        return self

    def get_row_count(self) -> int:
        """获取表格数据行数。"""
        return self.page.locator(TABLE_ROWS).count()

    @allure.step("获取表格全部文本")
    def get_table_text(self) -> str:
        """获取表格主体区域的纯文本内容。"""
        return self.locator(TABLE_BODY).inner_text()

    def get_cell_text(self, row_index: int, column_index: int) -> str:
        """获取指定单元格的文本。

        Args:
            row_index: 行索引（从 0 开始）
            column_index: 列索引（从 0 开始）
        """
        row = self.page.locator(TABLE_ROWS).nth(row_index)
        cells = row.locator("td").all()
        if column_index < len(cells):
            return cells[column_index].inner_text()
        return ""

    # ————————————————————————————————————————
    # 对话框
    # ————————————————————————————————————————

    def wait_for_dialog(self) -> "DataTable":
        """等待对话框展开。"""
        self.wait_for_visible(DIALOG)
        return self

    @allure.step("填写对话框字段: {name} = {value}")
    def fill_dialog_field(self, name: str, value: str) -> "DataTable":
        """在新增/编辑对话框中填写字段。

        Args:
            name: 字段 label 文本（如 "用户名称"）
            value: 要填入的值
        """
        # RuoYi 对话框通常使用 form-item 布局
        field = self.page.locator(
            f".el-form-item:has-text('{name}') input, "
            f".form-group:has-text('{name}') input, "
            f"label:has-text('{name}') + div input"
        ).first
        field.clear()
        field.fill(value)
        return self

    @allure.step("确认对话框")
    def confirm_dialog(self) -> "DataTable":
        """点击对话框确定按钮。"""
        self.click(DIALOG_CONFIRM)
        self.wait_for_hidden(DIALOG)
        self.page.wait_for_load_state("networkidle")
        return self

    def cancel_dialog(self) -> "DataTable":
        """点击对话框取消按钮。"""
        self.click(DIALOG_CANCEL)
        return self

    # ————————————————————————————————————————
    # 等待 & 校验
    # ————————————————————————————————————————

    def wait_for_load(self) -> "DataTable":
        """等待表格数据加载完成。"""
        self.wait_for_visible(TABLE_BODY)
        return self

    def assert_has_data(self) -> "DataTable":
        """断言表格至少有一行数据。"""
        count = self.get_row_count()
        assert count > 0, "表格应至少有一行数据"
        return self

    def assert_empty(self) -> "DataTable":
        """断言表格无数据。"""
        count = self.get_row_count()
        assert count == 0, f"表格应为空，但实际有 {count} 行"
        return self

    def assert_contains_text(self, text: str) -> "DataTable":
        """断言表格包含指定文本。"""
        table_text = self.get_table_text()
        assert text in table_text, \
            f"表格应包含 '{text}'，实际文本:\n{table_text[:500]}"
        return self
