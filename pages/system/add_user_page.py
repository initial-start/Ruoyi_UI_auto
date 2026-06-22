"""新增用户页面对象。

URL: /system/user/add | 标题: 新增用户

基于 http://localhost/system/user/add 实际 DOM 结构封装。

表单字段：
  基本信息:
    - 用户名称: input[name='userName'] placeholder="请输入用户名称"
    - 归属部门: input[name='deptName'] placeholder="请选择归属部门" (zTree选择)
    - 手机号码: input[name='phonenumber'] placeholder="请输入手机号码"
    - 邮箱:     input[name='email'] placeholder="请输入邮箱"
    - 登录账号: input[name='loginName'] placeholder="请输入登录账号"
    - 登录密码: input[name='password'] placeholder="请输入登录密码"
    - 用户性别: select[name='sex'] (男/女/未知)
    - 用户状态: input[name='status'] (checkbox: 正常/停用)
    - 岗位:     select[name='post'] (多选)
    - 角色:     input[name='role'] (checkbox: 普通角色)
  其他信息:
    - 备注:     textarea[name='remark']

用法:
    page.goto("http://localhost/system/user/add")
    add_page = AddUserPage(page)
    add_page.fill_user_name("test1") \
            .fill_login_name("user1") \
            .fill_password("123456") \
            .fill_phone("1340000001") \
            .select_dept("软件测试开发部") \
            .check_role("普通角色") \
            .click_submit()
"""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage

# ================================================================
# 表单字段选择器
# ================================================================
INPUT_USER_NAME = "input[name='userName']"
INPUT_DEPT_NAME = "input[name='deptName']"
INPUT_DEPT_ID = "input[name='deptId']"
INPUT_PHONE = "input[name='phonenumber']"
INPUT_EMAIL = "input[name='email']"
INPUT_LOGIN_NAME = "input[name='loginName']"
INPUT_PASSWORD = "input[name='password']"
SELECT_SEX = "select[name='sex']"
INPUT_STATUS = "input[name='status']"
SELECT_POST = "select[name='post']"
INPUT_REMARK = "textarea[name='remark']"

# ================================================================
# 按钮
# ================================================================
BTN_SUBMIT = "button.btn-primary"          # 保 存 — onclick='submitHandler()'
BTN_CLOSE = "button.btn-danger"            # 关 闭 — onclick='closeItem()'


class AddUserPage(BasePage):
    """新增用户页面。

    用法:
        add_page = AddUserPage(page)
        add_page.fill_user_name("test1") \
                .fill_login_name("user1") \
                .fill_password("123456") \
                .click_submit()
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ================================================================
    # 等待
    # ================================================================

    def wait_loaded(self) -> "AddUserPage":
        """等待表单页面加载完成。"""
        self.wait_for_visible(INPUT_USER_NAME)
        return self

    # ================================================================
    # 基本信息 — 文本输入
    # ================================================================

    def fill_user_name(self, value: str) -> "AddUserPage":
        """填写用户名称。"""
        self.fill(INPUT_USER_NAME, value)
        return self

    def fill_login_name(self, value: str) -> "AddUserPage":
        """填写登录账号。"""
        self.fill(INPUT_LOGIN_NAME, value)
        return self

    def fill_password(self, value: str) -> "AddUserPage":
        """填写登录密码。"""
        self.fill(INPUT_PASSWORD, value)
        return self

    def fill_phone(self, value: str) -> "AddUserPage":
        """填写手机号码。"""
        self.fill(INPUT_PHONE, value)
        return self

    def fill_email(self, value: str) -> "AddUserPage":
        """填写邮箱。"""
        self.fill(INPUT_EMAIL, value)
        return self

    # ================================================================
    # 基本信息 — 选择
    # ================================================================

    def select_sex(self, value: str) -> "AddUserPage":
        """选择用户性别。

        Args:
            value: '0'=男, '1'=女, '2'=未知
        """
        self.locator(SELECT_SEX).select_option(value)
        return self

    def set_status(self, enable: bool = True) -> "AddUserPage":
        """设置用户状态。

        Args:
            enable: True=正常(勾选), False=停用(取消勾选)
        """
        cb = self.locator(INPUT_STATUS).first
        if enable:
            cb.check()
        else:
            cb.uncheck()
        return self

    # ================================================================
    # 归属部门（zTree 弹窗选择）
    # ================================================================

    def select_dept(self, dept_name: str) -> "AddUserPage":
        """选择归属部门。

        流程：点输入框 -> iframe zTree -> 获取 deptId ->
        直接设置表单 hidden deptId + deptName -> 关闭弹窗。
        """
        # 1. 点击输入框弹出弹窗
        self.locator(INPUT_DEPT_NAME).evaluate('el => el.click()')
        self.page.wait_for_timeout(800)

        # 2. 在 iframe 中通过 zTree API 获取节点 deptId
        dept_id = None
        for frame in self.page.frames:
            if 'selectDeptTree' in frame.url:
                result = frame.evaluate(
                    """(name) => {
                        var treeObj = $.fn.zTree.getZTreeObj('tree');
                        if (treeObj) {
                            var nodes = treeObj.transformToArray(treeObj.getNodes());
                            for (var i = 0; i < nodes.length; i++) {
                                if (nodes[i].name === name) return {id: nodes[i].id, name: nodes[i].name};
                            }
                        }
                        return null;
                    }""",
                    dept_name,
                )
                if result:
                    dept_id = result['id']
                break
        self.page.wait_for_timeout(200)

        # 3. 关闭弹窗
        close_btn = self.page.locator('.layui-layer-dialog .layui-layer-close').first
        if close_btn.count() > 0:
            close_btn.evaluate('el => el.click()')
        self.page.wait_for_timeout(300)

        # 4. 直接设置表单 deptId + deptName
        if dept_id is not None:
            self.page.locator(INPUT_DEPT_ID).evaluate(
                'el => { el.value = "' + str(dept_id) + '"; el.dispatchEvent(new Event("change")); }'
            )
        self.page.locator(INPUT_DEPT_NAME).evaluate(
            'el => { el.value = "' + dept_name + '"; el.dispatchEvent(new Event("change")); }'
        )

        return self

    # ================================================================
    # 岗位（下拉多选）
    # ================================================================

    def select_post(self, *post_names: str) -> "AddUserPage":
        """在岗位下拉中选择一个或多个岗位。

        Args:
            post_names: 岗位名称，如 '董事长', '项目经理'
        """
        sel = self.locator(SELECT_POST).first
        for name in post_names:
            sel.select_option(label=name)
        return self

    # ================================================================
    # 角色（checkbox）
    # ================================================================

    def check_role(self, role_name: str) -> "AddUserPage":
        """勾选指定名称的角色复选框。

        Args:
            role_name: 角色名称，如 '普通角色'
        """
        # 通过 JS 遍历 checkbox 的父标签文本匹配
        self.page.evaluate(
            """(name) => {
                var cbs = document.querySelectorAll('input[type=checkbox]');
                for (var i = 0; i < cbs.length; i++) {
                    var parent = cbs[i].parentElement;
                    if (parent && parent.textContent.indexOf(name) >= 0) {
                        if (!cbs[i].checked) cbs[i].click();
                        break;
                    }
                }
            }""",
            role_name,
        )
        return self

    def uncheck_role(self, role_name: str) -> "AddUserPage":
        """取消勾选指定角色。"""
        self.page.evaluate(
            """(name) => {
                var cbs = document.querySelectorAll('input[type=checkbox]');
                for (var i = 0; i < cbs.length; i++) {
                    var parent = cbs[i].parentElement;
                    if (parent && parent.textContent.indexOf(name) >= 0) {
                        if (cbs[i].checked) cbs[i].click();
                        break;
                    }
                }
            }""",
            role_name,
        )
        return self

    # ================================================================
    # 其他信息
    # ================================================================

    def fill_remark(self, value: str) -> "AddUserPage":
        """填写备注。"""
        self.locator(INPUT_REMARK).fill(value)
        return self

    # ================================================================
    # 按钮操作
    # ================================================================

    def click_submit(self) -> "AddUserPage":
        """点击保存/提交按钮。"""
        self.locator(BTN_SUBMIT).first.evaluate("el => el.click()")
        self.page.wait_for_timeout(1500)
        return self

    def click_close(self) -> "AddUserPage":
        """点击关闭/返回按钮。"""
        self.locator(BTN_CLOSE).first.evaluate("el => el.click()")
        return self

    # ================================================================
    # 断言
    # ================================================================

    def assert_loaded(self) -> "AddUserPage":
        """断言页面已加载。"""
        self.assert_visible(INPUT_USER_NAME)
        return self

    def assert_field_value(self, name: str, expected: str) -> "AddUserPage":
        """断言指定 name 的 input 值为预期。"""
        actual = self.locator(f"input[name='{name}']").first.input_value()
        assert actual == expected, f"字段 {name} 应为 '{expected}'，实际: '{actual}'"
        return self
