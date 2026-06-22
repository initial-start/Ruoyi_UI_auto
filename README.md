# RuoYi_UI_Automation_Testing_Framework

## 项目介绍

本项目是基于 **Python + Playwright + Pytest** 自研轻量化 UI 自动化测试框架，对接 **RuoYi-Vue 若依后台管理系统**，完成登录模块、用户管理模块全套 UI 自动化回归测试，覆盖新增、修改、删除、导入导出、必填校验、弹窗断言、复选框联动等 90% 以上业务场景；实现用例数据与代码分离、测试数据自动前置造数 + 后置清理、UI 响应校验 + 数据库落库双重断言、失败自动截图、完整日志记录、Allure 可视化测试报告生成，可本地一键执行，适配 Jenkins 持续集成定时回归。

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 运行引擎 | Pytest | 用例管理、参数化、Fixture 前置后置、标记筛选执行 |
| UI 自动化 | Playwright | 浏览器驱动，自动等待，支持无头/有头模式切换 |
| 页面对象 | Page Object Model | 遵循 PO 思想，抽取页面公共操作封装基础页 |
| 数据驱动 | YAML + parametrize | 测试数据与代码解耦，加用例不改 Python 代码 |
| 数据库校验 | PyMySQL | 封装 Database 工具类，UI 操作后查库做双重断言 |
| 测试报告 | Allure | 步骤追溯、失败截图、附件、可视化图表 |
| 日志处理 | logging 双通道 | 控制台 INFO + 文件 DEBUG，记录完整操作链路 |
| 配置管理 | YAML 多环境 | dev/test/prod 三套环境，TEST_ENV 环境变量一键切换 |

## 项目目录说明

Ruoyi_ui_auto/
├── conftest.py              # 全局夹具、失败截图钩子
├── pytest.ini               # pytest运行配置、用例标签定义
├── requirements.txt         # 项目第三方依赖清单
├── README.md                # 项目使用说明文档
│
├── config/                  # 全局配置模块：环境配置、全局参数管理
│
├── pages/                   # POM页面对象层：封装页面元素与交互操作
│
├── testcases/               # 测试用例层：存放各业务模块自动化用例
│
├── data/                    # 测试数据层：YAML维护所有用例测试数据
│
├── utils/                   # 通用工具层：日志、报告、断言、数据库工具
│
├── reports/allure-results/  # Allure测试报告原始数据目录
├── screenshots/             # 用例失败截图存储目录
└── logs/                    # 自动化运行日志存放目录

## UI 操作执行调用链

```
test_xxx.py → AddUserPage.fill_user_name(xxx) → BasePage.fill(selector, value) → page.locator.fill()
                                                                                      │
                                                                      Playwright 自动等待 + 聚焦 + 清空 + 输入
```

> BasePage 所有交互方法返回 self，支持链式调用：`page.fill("a").fill("b").click("c")`

## 数据驱动执行数据流

```
data/*.yaml → testdata_loader.parametrize_from_yaml() → @pytest.mark.parametrize
                                                              │
                                          ┌───────────────────┴───────────────────┐
                                          │                                       │
                                    scenario: add                          scenario: validate
                                   登录 → 填写表单 → 提交                  登录 → 空字段 → 点击保存
                                   → 弹窗处理 → 搜索断言                  → 必填标红断言
                                   → 数据库落库双重校验
```

## 框架核心亮点

- **UI + DB 双重断言**：不仅校验页面显示结果，额外查询 MySQL 校验数据真实新增 / 修改 / 删除状态，规避 UI 假成功问题。删除操作断言 `sys_user.del_flag = '2'`
- **数据环境自闭环**：新增测试自动生成唯一用户名（时间戳后缀），删除测试先造数据再删，避免主键 / 唯一索引冲突，用例可重复稳定执行
- **鉴权适配**：`logged_in_page` fixture 全局一次登录 + 处理安全弹窗，全部用例共享已认证 Page，无需重复登录
- **用例低维护**：用户信息、断言期望、操作类型全部配置在 YAML，新增场景只需加一条 YAML 数据，无需改动 Python 测试代码
- **弹窗自动处理**：封装 PopupAssert 链式断言器，一行代码完成 `wait_for_popup().assert_contains("确定删除").confirm()`
- **问题可追溯**：测试失败自动截取整页截图附加到 Allure 报告，完整请求日志留存，步骤级 Allure 追溯
- **工程化可落地**：支持本地一键 `pytest` 执行，多环境配置切换，接入 Jenkins 实现定时自动回归、报告邮件推送
