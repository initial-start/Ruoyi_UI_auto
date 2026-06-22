"""测试数据加载器。

支持从 YAML 文件加载测试数据，并提供 pytest parametrize 辅助方法。

用法：
    from data.testdata_loader import load_yaml, parametrize_from_yaml

    # 直接加载
    data = load_yaml("login_data.yaml")

    # 用于 parametrize
    cases, ids = parametrize_from_yaml("login_data.yaml", "invalid_cases")
    @pytest.mark.parametrize("case", cases, ids=ids)
    def test_login(self, case):
        ...
"""

from pathlib import Path
from typing import Any

import yaml

# 数据目录路径
DATA_DIR = Path(__file__).resolve().parent


def load_yaml(filename: str) -> dict[str, Any]:
    """加载 YAML 测试数据文件。

    Args:
        filename: YAML 文件名（相对于 data/ 目录），如 "login_data.yaml"

    Returns:
        解析后的字典

    Raises:
        FileNotFoundError: 文件不存在时
    """
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data or {}


def parametrize_from_yaml(
    filename: str,
    scenario: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    """从 YAML 文件中提取指定场景的测试用例，返回 parametrize 所需的 (cases, ids)。

    YAML 数据格式要求:
        scenario_name:
          - name: "case_1"      # 用作测试 ID
            field1: value1
            field2: value2
          - name: "case_2"
            field1: value1
            ...

    Args:
        filename: YAML 文件名（相对于 data/ 目录）
        scenario: 场景名称（YAML 中的顶级 key）

    Returns:
        (cases, ids) — cases 是字典列表，ids 是测试名称列表

    Example:
        # login_data.yaml:
        #   invalid_cases:
        #     - name: "wrong_password"
        #       username: "admin"
        #       password: "wrong"
        #       expected: "密码错误"

        cases, ids = parametrize_from_yaml("login_data.yaml", "invalid_cases")
        # cases = [{"name": "wrong_password", "username": "admin", ...}]
        # ids = ["wrong_password"]
    """
    data = load_yaml(filename)
    cases = data.get(scenario, [])

    if not cases:
        raise ValueError(
            f"在 {filename} 中找不到场景 '{scenario}' 或场景为空"
        )

    ids = [case.get("name", f"case_{i}") for i, case in enumerate(cases)]

    return cases, ids
