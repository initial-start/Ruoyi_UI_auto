# Ruoyi_UI_auto UI

## 项目介绍

本项目是基于 **Python + Playwright + Pytest + Allure** 自研轻量化 UI 自动化测试框架，对接 **RuoYi-Vue 若依后台管理系统**，完成登录模块、用户管理模块全套 UI 自动化回归测试，覆盖新增、修改、删除、导入导出、必填校验、弹窗断言、复选框联动等 90% 以上业务场景；实现用例数据与代码分离、测试数据自动前置造数 + 后置清理、UI 响应校验 + 数据库落库双重断言、失败自动截图、完整日志记录、Allure 可视化测试报告生成，可本地一键执行，适配 Jenkins 持续集成定时回归。

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

- 双重校验机制：页面展示校验 + 数据库落库校验，避免页面展示正常但底层数据异常的假通过问题
- 用例稳定可复用：自动生成唯一测试数据、执行后自动清理脏数据，无索引冲突，用例可反复执行
- 全局会话复用：封装登录夹具，全局一次登录，所有用例共享登录态，减少重复操作
- 低维护成本：所有入参、预期结果存于 YAML，新增测试场景仅新增数据，不用修改代码
- 问题快速定位：用例失败自动截图嵌入 Allure 报告，完整运行日志留存，步骤可追溯
- 工程化落地：多环境一键切换，支持本地调试，可集成 Jenkins 实现定时自动化回归

