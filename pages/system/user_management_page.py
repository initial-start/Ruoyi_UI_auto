"""用户管理页面对象。

基于 http://localhost/system/user 实际 DOM 结构封装。

页面结构：
  - 搜索区域：登录名称 / 手机号码 / 用户状态 / 创建时间范围
  - 工具栏：新增 / 修改 / 删除 / 导入 / 导出 / 刷新 / 切换视图
  - 表格：bootstrap-table，动态渲染，含复选框 + 行操作按钮
  - 新增/编辑弹窗：layui 对话框

用法：
    page.goto("http://localhost/system/user")
    user_page = UserManagementPage(page)
    user_page.wait_loaded() \
             .search_by_login_name("admin") \
             .click_add()
"""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from pages.base_page import BasePage

# ================================================================
# 搜索区域选择器
# ================================================================
INPUT_LOGIN_NAME = "input[name='loginName']"
INPUT_PHONE = "input[name='phonenumber']"
SELECT_STATUS = "select[name='status']"
INPUT_START_TIME = "input[name='params[beginTime]']"
INPUT_END_TIME = "input[name='params[endTime]']"

# ================================================================
# 工具栏按钮选择器（都是 <a> 标签 + onclick）
# ================================================================
BTN_ADD = "a.btn-success"                                     # onclick="$.operate.addTab()"
BTN_EDIT = "a.btn-primary.single"                             # onclick="$.operate.editTab()"
BTN_DELETE = "a.btn-danger.multiple"                          # onclick="$.operate.removeAll()"
BTN_IMPORT = "a.btn-info"                                     # onclick="$.table.importExcel()"
BTN_EXPORT = "a.btn-warning"                                  # onclick="$.table.exportExcel()"
BTN_SEARCH = "a[onclick*='$.table.search']"                  # 搜索按钮
BTN_RESET = "a[onclick*='resetPre']"                          # 重置按钮
BTN_REFRESH = "button[name='refresh']"                        # 刷新按钮

# ================================================================
# 表格选择器（bootstrap-table）
# ================================================================
TABLE = "table#bootstrap-table, table[data-unique-id]"
TABLE_BODY = f"{TABLE} tbody"
TABLE_ROWS = f"{TABLE_BODY} tr"
TABLE_CHECKBOX = "input[name='btSelectItem']"
TABLE_SELECT_ALL = "input[name='btSelectAll']"

# ================================================================
# 弹窗选择器（layui dialog）
# ================================================================
DIALOG = ".layui-layer-dialog:visible"
DIALOG_TITLE = ".layui-layer-title"
DIALOG_CONFIRM = ".layui-layer-btn0"
DIALOG_CANCEL = ".layui-layer-btn1"
DIALOG_CLOSE = ".layui-layer-close"

# ================================================================
# 分页
# ================================================================
PAGINATION_INFO = ".pagination-info, .pagination-detail"


class UserManagementPage(BasePage):
    """RuoYi 用户管理页面。

    用法：
        user_page = UserManagementPage(page)
        user_page.wait_loaded()
        user_page.search_by_login_name("admin")
        user_page.click_add()
        # ... 填写弹窗表单 ...
        user_page.confirm_dialog()
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ================================================================
    # 等待加载
    # ================================================================

    def wait_loaded(self, timeout: int = 15000) -> "UserManagementPage":
        """等待 bootstrap-table 渲染完成。"""
        try:
            self.page.wait_for_selector(f"{TABLE_BODY} tr", timeout=timeout)
        except PlaywrightTimeout:
            pass  # 可能表格为空（0条数据）
        return self

    # ================================================================
    # 搜索操作
    # ================================================================

    def fill_login_name(self, value: str) -> "UserManagementPage":
        """填写登录名称搜索条件。"""
        self.locator(INPUT_LOGIN_NAME).fill(value)
        return self

    def fill_phone(self, value: str) -> "UserManagementPage":
        """填写手机号码搜索条件。"""
        self.locator(INPUT_PHONE).fill(value)
        return self

    def select_status(self, value: str) -> "UserManagementPage":
        """选择用户状态。

        Args:
            value: '所有' / '正常'('0') / '停用'('1')
        """
        self.locator(SELECT_STATUS).select_option(value)
        return self

    def fill_start_time(self, value: str) -> "UserManagementPage":
        """填写创建时间-开始。格式: 2026-06-01"""
        self.locator(INPUT_START_TIME).fill(value)
        return self

    def fill_end_time(self, value: str) -> "UserManagementPage":
        """填写创建时间-结束。格式: 2026-06-30"""
        self.locator(INPUT_END_TIME).fill(value)
        return self

    def click_search(self) -> "UserManagementPage":
        """点击搜索按钮，等待表格刷新。"""
        self._click_btn(BTN_SEARCH)
        self.page.wait_for_timeout(800)
        self.wait_loaded()
        return self

    def click_reset(self) -> "UserManagementPage":
        """点击重置按钮，清空所有搜索条件并自动查询。"""
        self._click_btn(BTN_RESET)
        self.page.wait_for_timeout(800)
        self.wait_loaded()
        return self

    # ================================================================
    # 搜索快捷方法
    # ================================================================

    def search_by_login_name(self, name: str) -> "UserManagementPage":
        """按登录名称搜索。"""
        return self.fill_login_name(name).click_search()

    def search_by_phone(self, phone: str) -> "UserManagementPage":
        """按手机号码搜索。"""
        return self.fill_phone(phone).click_search()

    def search_by_status(self, status: str) -> "UserManagementPage":
        """按用户状态搜索。"""
        return self.select_status(status).click_search()

    # ================================================================
    # 工具栏操作
    # ================================================================

    def click_add(self) -> "UserManagementPage":
        """点击新增按钮，等待弹窗出现。"""
        self._click_btn(BTN_ADD)
        self.page.wait_for_selector(DIALOG, timeout=5000)
        return self

    def click_edit(self) -> "UserManagementPage":
        """点击修改按钮（需先选中行）。"""
        self._click_btn(BTN_EDIT)
        self.page.wait_for_selector(DIALOG, timeout=5000)
        return self

    def click_delete_toolbar(self) -> "UserManagementPage":
        """点击工具栏删除按钮（需先选中行）。"""
        self._click_btn(BTN_DELETE)
        return self

    def click_import(self) -> "UserManagementPage":
        """点击导入按钮。"""
        self._click_btn(BTN_IMPORT)
        return self

    def click_export(self) -> "UserManagementPage":
        """点击导出按钮。"""
        self._click_btn(BTN_EXPORT)
        return self

    def click_refresh(self) -> "UserManagementPage":
        """点击刷新按钮。"""
        self._click_btn(BTN_REFRESH)
        self.wait_loaded()
        return self

    # ================================================================
    # 行选择操作
    # ================================================================

    def select_row(self, index: int = 0) -> "UserManagementPage":
        """勾选指定行的 checkbox。

        Args:
            index: 行索引，0=第一行
        """
        cb = self.page.locator(TABLE_CHECKBOX).nth(index)
        cb.evaluate("el => { el.checked = true; el.dispatchEvent(new Event('change')); }")
        self.page.wait_for_timeout(300)
        return self

    def select_all(self) -> "UserManagementPage":
        """勾选全选 checkbox。"""
        cb = self.page.locator(TABLE_SELECT_ALL).first
        cb.evaluate("el => { el.checked = true; el.dispatchEvent(new Event('change')); }")
        return self

    # ================================================================
    # 行操作
    # ================================================================

    def click_row_edit(self, index: int = 0) -> "UserManagementPage":
        """点击指定行的编辑按钮。"""
        row = self.page.locator(TABLE_ROWS).nth(index)
        edit_btn = row.locator("a:has-text('编辑')").first
        edit_btn.evaluate("el => el.click()")
        return self

    def click_row_delete(self, index: int = 0) -> "UserManagementPage":
        """点击指定行的删除按钮。"""
        row = self.page.locator(TABLE_ROWS).nth(index)
        del_btn = row.locator("a:has-text('删除')").first
        del_btn.evaluate("el => el.click()")
        return self

    # ================================================================
    # 弹窗操作（layui dialog）
    # ================================================================

    def get_dialog_title(self) -> str:
        """获取弹窗标题。"""
        return self.page.locator(DIALOG_TITLE).first.inner_text().strip()

    def fill_dialog_field(self, label: str, value: str) -> "UserManagementPage":
        """在弹窗中根据 label 文本找到输入框并填充。

        遍历弹窗中所有 label，匹配后通过 for 属性或父级查找 input。
        """
        dialog = self.page.locator(DIALOG).first

        # 方案1: label for 匹配
        labels = dialog.locator("label, .control-label").all()
        for lbl in labels:
            try:
                if label in lbl.inner_text():
                    fid = lbl.get_attribute("for")
                    if fid:
                        inp = dialog.locator(f"#{fid}").first
                        if inp.count() > 0:
                            inp.fill(value)
                            return self
                    # 父级内找
                    inp = lbl.locator("..").locator("input, select").first
                    if inp.count() > 0:
                        inp.fill(value)
                        return self
            except:
                continue

        # 方案2: name 映射兜底
        name_map = {
            "用户名称": "userName", "用户昵称": "userName",
            "手机号码": "phonenumber", "登录账户": "loginName",
            "登录名称": "loginName", "登录密码": "password",
            "密码": "password", "邮箱": "email", "备注": "remark",
        }
        name = name_map.get(label, "")
        if name:
            inp = dialog.locator(f"input[name='{name}']").first
            if inp.count() > 0:
                inp.fill(value)
        return self

    def fill_dialog_by_name(self, name: str, value: str) -> "UserManagementPage":
        """在弹窗中通过 name 属性直接填充。"""
        self.page.locator(DIALOG).first.locator(f"input[name='{name}'], select[name='{name}']").first.fill(value)
        return self

    def confirm_dialog(self) -> "UserManagementPage":
        """点击弹窗确定按钮。"""
        btn = self.page.locator(DIALOG_CONFIRM).first
        btn.evaluate("el => el.click()")
        self.page.wait_for_timeout(1000)
        return self

    def cancel_dialog(self) -> "UserManagementPage":
        """点击弹窗取消按钮。"""
        self.page.locator(DIALOG_CANCEL).first.evaluate("el => el.click()")
        return self

    def close_dialog(self) -> "UserManagementPage":
        """点击弹窗右上角 X 关闭。"""
        self.page.locator(DIALOG_CLOSE).first.evaluate("el => el.click()")
        return self

    def wait_for_dialog(self, timeout: int = 5000) -> "UserManagementPage":
        """等待弹窗出现。"""
        self.page.wait_for_selector(DIALOG, timeout=timeout)
        return self

    def wait_for_dialog_close(self, timeout: int = 5000) -> "UserManagementPage":
        """等待弹窗关闭。"""
        self.page.wait_for_selector(DIALOG, state="hidden", timeout=timeout)
        return self

    # ================================================================
    # 表格信息获取
    # ================================================================

    def get_row_count(self) -> int:
        """获取当前表格行数。"""
        return self.page.locator(TABLE_ROWS).count()

    def get_table_data(self) -> list[dict]:
        """通过 JS 获取 bootstrap-table 当前数据。"""
        return self.page.evaluate("() => jQuery('table').bootstrapTable('getData')") or []

    def get_cell_text(self, row_index: int, column_index: int) -> str:
        """获取单元格文本。"""
        row = self.page.locator(TABLE_ROWS).nth(row_index)
        cells = row.locator("td").all()
        if column_index < len(cells):
            return cells[column_index].inner_text().strip()
        return ""

    def get_pagination_info(self) -> str:
        """获取分页信息文本。"""
        return self.page.locator(PAGINATION_INFO).first.inner_text().strip()

    # ================================================================
    # 断言
    # ================================================================

    def assert_loaded(self) -> "UserManagementPage":
        """断言页面已加载。"""
        self.assert_visible(f"{TABLE}, .fixed-table-container")
        return self

    def assert_contains_text(self, text: str) -> "UserManagementPage":
        """断言表格中包含指定文本。"""
        body = self.page.locator(TABLE_BODY).first.inner_text()
        assert text in body, f"表格中应包含 '{text}'，实际: {body[:200]}"
        return self

    def assert_not_contains(self, text: str) -> "UserManagementPage":
        """断言表格中不包含指定文本。"""
        body = self.page.locator(TABLE_BODY).first.inner_text()
        assert text not in body, f"表格中不应包含 '{text}'"
        return self

    def assert_row_count(self, expected: int) -> "UserManagementPage":
        """断言表格行数。"""
        actual = self.get_row_count()
        assert actual == expected, f"表格应有 {expected} 行，实际: {actual}"
        return self

    def assert_dialog_visible(self) -> "UserManagementPage":
        """断言弹窗可见。"""
        self.assert_visible(DIALOG)
        return self

    # ================================================================
    # 内部辅助
    # ================================================================

    def _click_btn(self, selector: str) -> None:
        """JS click 绕过遮罩 + 中文编码问题。"""
        el = self.page.locator(selector).first
        el.evaluate("el => el.click()")
