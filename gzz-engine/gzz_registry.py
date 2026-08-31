"""
Gzz 编码注册表
SQLite 持久化，防重号，支持查询和导出
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gzz_registry.db")


def get_db():
    """获取数据库连接，自动建表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gzz_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            prefix TEXT NOT NULL,
            name TEXT,
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_prefix ON gzz_codes(prefix)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_code ON gzz_codes(code)
    """)
    conn.commit()
    return conn


def register(code: str, name: str = "", description: str = "") -> bool:
    """
    注册编码，返回 True=新增，False=已存在
    """
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO gzz_codes (code, prefix, name, description, created_at) VALUES (?, ?, ?, ?, ?)",
            (code, code.split("-")[1] if "-" in code else "?", name, description,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_next_seq(prefix_key: str) -> int:
    """
    根据前缀键查当前最大序号，返回下一个可用序号
    prefix_key 格式: P-SXJ-CN / E-GOVERN-CARBON-20251006
    """
    conn = get_db()
    # 构造 LIKE 模式
    like_pattern = f"Gzz-{prefix_key}-%"
    cursor = conn.execute(
        "SELECT code FROM gzz_codes WHERE code LIKE ? ORDER BY code DESC LIMIT 1",
        (like_pattern,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return 1

    # 提取最后一个 - 后面的序号
    code = row[0]
    try:
        seq = int(code.rsplit("-", 1)[-1])
        return seq + 1
    except (ValueError, IndexError):
        return 1


def lookup(code: str) -> dict:
    """查询单个编码"""
    conn = get_db()
    cursor = conn.execute(
        "SELECT code, prefix, name, description, created_at FROM gzz_codes WHERE code = ?",
        (code,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "code": row[0],
        "prefix": row[1],
        "name": row[2],
        "description": row[3],
        "created_at": row[4],
    }


def list_all(prefix: str = None) -> list:
    """列出所有编码，可按前缀过滤"""
    conn = get_db()
    if prefix:
        cursor = conn.execute(
            "SELECT code, prefix, name, description, created_at FROM gzz_codes WHERE prefix = ? ORDER BY code",
            (prefix,)
        )
    else:
        cursor = conn.execute(
            "SELECT code, prefix, name, description, created_at FROM gzz_codes ORDER BY code"
        )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"code": r[0], "prefix": r[1], "name": r[2], "description": r[3], "created_at": r[4]}
        for r in rows
    ]


def count_by_prefix() -> dict:
    """统计各前缀编码数量"""
    conn = get_db()
    cursor = conn.execute(
        "SELECT prefix, COUNT(*) FROM gzz_codes GROUP BY prefix ORDER BY prefix"
    )
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def export_all() -> str:
    """导出全量编码清单为文本"""
    all_codes = list_all()
    if not all_codes:
        return "（空）"

    lines = []
    lines.append(f"Gzz 编码注册表 — 全量导出 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    lines.append("=" * 60)
    for c in all_codes:
        lines.append(f"{c['code']:50s} | {c['prefix']:4s} | {c['name'] or '-'}")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print("当前注册表:", count_by_prefix())
    print("导出:", export_all()[:200])