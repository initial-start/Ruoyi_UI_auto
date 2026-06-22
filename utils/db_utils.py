"""数据库工具 — MySQL 连接与查询。

用于 UI 自动化后的数据库校验。

用法:
    from utils.db_utils import Database
    db = Database(config.database)
    row = db.query_one("SELECT * FROM sys_user WHERE login_name = %s", ("admin",))
    db.close()
"""

from __future__ import annotations

from typing import Any

import pymysql


class Database:
    """MySQL 数据库连接工具。

    支持上下文管理器:
        with Database(cfg) as db:
            row = db.query_one("SELECT ...")
    """

    def __init__(self, db_config: dict[str, Any]) -> None:
        self._conn = pymysql.connect(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 3306),
            user=db_config.get("user", "root"),
            password=db_config.get("password", "123456"),
            database=db_config.get("database", "ry"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def query_one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        """查询单条记录。"""
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def query_all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        """查询所有记录。"""
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        """查询记录数。"""
        row = self.query_one(f"SELECT COUNT(*) AS cnt FROM {table} WHERE {where}", params)
        return row["cnt"] if row else 0

    def exists(self, table: str, where: str = "1=1", params: tuple = ()) -> bool:
        """检查记录是否存在。"""
        return self.count(table, where, params) > 0

    def execute(self, sql: str, params: tuple = ()) -> int:
        """执行写操作，返回影响行数。"""
        with self._conn.cursor() as cur:
            rows = cur.execute(sql, params)
            self._conn.commit()
            return rows


# ================================================================
# RuoYi 业务查询（快捷方法）
# ================================================================


def query_user_by_login_name(db: Database, login_name: str) -> dict[str, Any] | None:
    """按 login_name 查询 sys_user 表。"""
    return db.query_one(
        "SELECT user_id, login_name, user_name, phonenumber, email, "
        "status, del_flag, create_time, dept_id "
        "FROM sys_user WHERE login_name = %s AND del_flag = '0'",
        (login_name,),
    )


def query_user_by_id(db: Database, user_id: int) -> dict[str, Any] | None:
    """按 user_id 查询 sys_user 表。"""
    return db.query_one(
        "SELECT user_id, login_name, user_name, phonenumber, email, "
        "status, del_flag, create_time "
        "FROM sys_user WHERE user_id = %s",
        (user_id,),
    )


def user_exists(db: Database, login_name: str) -> bool:
    """检查 login_name 是否存在且未删除。"""
    return db.exists(
        "sys_user", "login_name = %s AND del_flag = '0'", (login_name,)
    )
