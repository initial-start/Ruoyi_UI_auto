"""左侧菜单栏组件。

基于 http://localhost/index 实际 DOM 结构识别：

RuoYi 使用 Bootstrap nav + metisMenu 实现多级菜单：
  <nav class="navbar-default navbar-static-side">
    <ul class="nav" id="side-menu">
      <li>
        <a href="#">                          ← 父级菜单
          <span class="nav-label">系统管理</span>
          <span class="fa arrow"></span>       ← arrow = 有子菜单
        </a>
        <ul class="nav nav-second-level collapse">  ← collapse = 默认折叠
          <li><a class="menuItem" href="/system/user">用户管理</a></li>
          <li>
            <a href="javascript:;">日志管理<span class="fa arrow"></span></a>
            <ul class="nav nav-third-level collapse">  ← 第三级
              <li><a class="menuItem" href="/monitor/operlog">操作日志</a></li>
            </ul>
          </li>
        </ul>
      </li>
    </ul>
  </nav>

菜单级别：最多 3 级（nav-second-level / nav-third-level）
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage

# — 实际页面选择器 —
SIDE_MENU = "#side-menu"
MENU_ITEM = "a.menuItem"
NAV_LABEL = ".nav-label"


class Sidebar(BasePage):
    """左侧菜单栏 — Bootstrap + metisMenu 多级菜单。

    用法：
        sidebar = Sidebar(page)
        sidebar.navigate_to("系统管理", "用户管理")
        sidebar.navigate_to("系统管理", "日志管理", "操作日志")
        sidebar.navigate_to("首页")
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ————————————————————————————————————————
    # 导航
    # ————————————————————————————————————————

    def navigate_to(self, *menu_items: str) -> "Sidebar":
        """按层级导航到目标菜单项。

        自动展开父级 → 点击叶子节点 → 等待页面加载。
        支持 1~3 级菜单。

        Args:
            menu_items: 菜单路径
                一级: ("首页",)
                二级: ("系统管理", "用户管理")
                三级: ("系统管理", "日志管理", "操作日志")
        """
        n = len(menu_items)

        for i, item in enumerate(menu_items):
            is_leaf = (i == n - 1)

            if is_leaf:
                self._click_leaf(item)
            else:
                self._expand_parent(item)

        self.page.wait_for_load_state("networkidle")
        return self

    # ————————————————————————————————————————
    # 内部方法
    # ————————————————————————————————————————

    def _expand_parent(self, label: str) -> None:
        """展开父级菜单 — 查找 a > .nav-label 匹配的父节点并点击。"""
        link = self._find_menu_link(label)
        # JS click + 等待 Bootstrap collapse 展开动画
        link.evaluate("el => el.click()")
        # 轮询等待子级 ul 出现 .in 类
        parent_li = link.locator("..")
        for _ in range(20):  # 最多等 2 秒
            sub = parent_li.locator("ul.nav-second-level, ul.nav-third-level").first
            if sub.count() > 0:
                cls = sub.get_attribute("class") or ""
                if "in" in cls:
                    break
            self.page.wait_for_timeout(100)

    def _click_leaf(self, label: str) -> None:
        """点击叶子菜单项 — 优先 a.menuItem，回退 nav-label。"""
        link = self._find_menu_link(label)
        link.evaluate("el => el.click()")

    def _find_menu_link(self, label: str) -> Locator:
        """通过文本匹配找到菜单链接。

        实际 DOM 中的标签结构：
          - 顶级父节点: <a><span class="nav-label">系统管理</span><span class="fa arrow"></span></a>
          - 子级父节点: <a><span>日志管理</span><span class="fa arrow"></span></a>  ← 无 .nav-label!
          - 叶子节点:   <a class="menuItem" href="...">用户管理</a>
          - 单级菜单:   <a class="menuItem"><span class="nav-label">首页</span></a>

        策略（按优先级）：
          1. a.menuItem 精确文本匹配（叶子节点）
          2. a 标签下所有 span 精确文本匹配（父节点，含 .nav-label 和纯 span）
          3. 全 #side-menu a 宽松子串匹配
        """
        all_links = self.page.locator("#side-menu a").all()

        # 策略1：a.menuItem 精确匹配（叶子节点）
        for el in all_links:
            if "menuItem" not in (el.get_attribute("class") or ""):
                continue
            if el.inner_text().strip() == label:
                return el

        # 策略2：a 标签下任意直系 span 精确匹配（父节点）
        #         顶级父节点用 span.nav-label，子级父节点用 span 无 class
        for el in all_links:
            for span in el.locator("> span").all():
                try:
                    if span.inner_text().strip() == label:
                        return el
                except:
                    continue

        # 策略3：全 #side-menu a 宽松子串匹配
        for el in all_links:
            try:
                if label in el.inner_text():
                    return el
            except:
                pass

        raise LookupError(f"在侧边栏中找不到菜单项: '{label}'")

    # ————————————————————————————————————————
    # 信息获取
    # ————————————————————————————————————————

    def get_all_top_menus(self) -> list[str]:
        """获取所有顶级菜单的标签文字。"""
        labels = self.page.locator(
            f"{SIDE_MENU} > li > a {NAV_LABEL}"
        ).all()
        return [l.inner_text().strip() for l in labels]

    def is_expanded(self, label: str) -> bool:
        """检查指定父级菜单是否已展开。"""
        parent_li = self._find_by_nav_label(label).locator("..")
        sub = parent_li.locator("ul.nav-second-level, ul.nav-third-level").first
        if sub.count() == 0:
            return False
        cls = sub.get_attribute("class") or ""
        return "in" in cls

    # ————————————————————————————————————————
    # 断言
    # ————————————————————————————————————————

    def assert_loaded(self) -> "Sidebar":
        """断言侧边栏已渲染。"""
        self.assert_visible(SIDE_MENU)
        return self
