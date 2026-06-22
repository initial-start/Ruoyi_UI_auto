# RuoYi UI 自动化测试框架

基于 **Playwright + Pytest + Allure** 的 RuoYi（若依）管理系统 Web UI 自动化测试。

## 快速开始

### 环境要求
- Python 3.12+
- Google Chrome 浏览器
- MySQL（可选，用于 DB 校验）

### 安装

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config/environments/test.yaml`，修改被测系统地址、登录凭据、Chrome 路径和数据库连接：

```yaml
base_url: "http://localhost"
browser:
  executable_path: "D:/Google/Chrome/Application/chrome.exe"  # 你的 Chrome 路径
credentials:
  username: "admin"
  password: "admin123"
database:          # 可选，不做 DB 校验可删除
  host: "localhost"
  password: "root"
```

> 注意：RuoYi 开启了图形验证码的话，需在 `application.yml` 中设置 `ruoyi.captchaType: false`

### 运行测试

```bash
# 默认测试环境（无头）
pytest

# 开发调试（有头 + 慢动作）
TEST_ENV=dev pytest --headed

# 冒烟测试
pytest -m smoke

# 指定模块
pytest testcases/test_login.py -v

# 并行执行
pytest -n auto
```

### 生成报告

```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 项目结构

```
Ruoyi_ui_auto/
├── config/                # 多环境 YAML 配置（dev/test/prod）
├── pages/                 # Page Object 层
│   ├── base_page.py       #   ★ 基类（30+ 通用操作）
│   ├── login_page.py      #   登录页
│   ├── main_page.py       #   主页仪表盘
│   ├── system/            #   业务模块页面
│   └── components/        #   可复用 UI 组件
├── testcases/             # 测试用例层
├── data/                  # YAML 测试数据
├── utils/                 # 工具层（日志/报告/断言/数据库）
├── conftest.py            # 全局 Pytest fixture
├── pytest.ini             # Pytest 配置
└── requirements.txt       # Python 依赖
```

## 添加新模块

以"角色管理"为例：

**1. 扫描页面元素**
```bash
# 用 Playwright 打开目标 URL，打印所有交互元素
```

**2. 创建 Page Object** — 在 `pages/system/` 下新建，继承 `BasePage`

**3. 创建测试数据** — 在 `data/` 下新建 `.yaml`，定义 `scenario` 字段区分操作类型

**4. 创建测试用例** — 在 `testcases/` 下新建 `test_xxx.py`，使用 `logged_in_page` fixture

**5. 注册标记** — 在 `pytest.ini` 的 `markers` 中添加模块标记

**6. 添加 DB 校验（可选）** — 在 `utils/db_utils.py` 中添加业务查询方法

## 架构原则

- 一个 URL 一个 Page Object
- 数据与代码分离（YAML 驱动）
- 禁止 `time.sleep()`，使用 Playwright 自动等待
- 中文编码用 Python 端过滤（避免 CSS `:has-text()` 乱码）
- 遮罩层用 JS click 绕过

## 后续改进方向

- [ ] 测试全面使用 MainPage + Sidebar 导航替代直接 `page.goto(url)`
- [ ] DataTable 组件集成到 UserManagementPage 等其他列表页
- [ ] 补充分页、导出、会话超时、角色/菜单/部门管理测试
- [ ] 导入文件路径改为相对于项目根目录
