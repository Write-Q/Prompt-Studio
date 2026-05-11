import sqlite3
from pathlib import Path


# 项目根目录，对应 PromptStudio/
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库存放目录，对应 PromptStudio/data/
DATA_DIR = BASE_DIR / "data"

# SQLite 数据库文件路径
DB_PATH = DATA_DIR / "app.db"


def get_connection() -> sqlite3.Connection:
    """
    获取数据库连接。

    这里统一处理数据库目录创建和连接配置，
    后续路由层、服务层如果要访问数据库，都应该复用这个方法。
    """
    # 如果 data 目录还不存在，就自动创建
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 建立 SQLite 连接
    connection = sqlite3.connect(DB_PATH)

    # 让查询结果支持按列名读取，后续转字典时更方便
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """
    初始化数据库表结构。

    当前阶段先只负责创建三张核心业务表：
    1. prompt_templates
    2. knowledge_snippets
    3. generation_history
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        # Prompt 模板表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                content TEXT NOT NULL,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        # 知识片段表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tags TEXT,
                content TEXT NOT NULL,
                source TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        # 生成历史表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                variables_json TEXT,
                snippet_ids TEXT,
                final_prompt TEXT NOT NULL,
                created_at TEXT
            )
            """
        )

        # 提交建表操作
        connection.commit()


if __name__ == "__main__":
    # 允许直接运行这个文件，用来单独验证数据库是否初始化成功
    init_db()
    print(f"数据库初始化完成：{DB_PATH}")
