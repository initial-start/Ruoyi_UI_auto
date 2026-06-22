"""Allure 报告辅助工具。

提供截图附加、文本附件等便捷方法，避免在测试/页面对象中重复编写 Allure API。
"""

from pathlib import Path

import allure
from playwright.sync_api import Page

from config.settings import SCREENSHOT_DIR


def attach_screenshot(page: Page, name: str = "screenshot") -> None:
    """截取整页截图并附加到 Allure 报告。

    Args:
        page: Playwright Page 对象
        name: Allure 附件中显示的名称
    """
    png_bytes = page.screenshot(full_page=True, type="png")
    allure.attach(
        png_bytes,
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def attach_text(content: str, name: str = "info") -> None:
    """附加文本内容到 Allure 报告。

    Args:
        content: 要附加的文本
        name: 附件名称
    """
    allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def save_screenshot_to_file(page: Page, name: str = "screenshot") -> Path:
    """保存截图到 screenshots/ 目录并返回文件路径。

    Args:
        page: Playwright Page 对象
        name: 文件名（不含扩展名）

    Returns:
        Path: 截图文件路径
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=path, full_page=True)
    return path
