from flask import Flask, request
from waitress import serve
import psycopg2
from psycopg2 import sql
from html import escape
import os

app = Flask(__name__)

def get_connection():
    username = os.environ.get('USER', 'runner')
    return psycopg2.connect(
        host="127.0.0.1",
        database="appdb",
        user=username
    )

def rows_to_text(rows):
    if not rows:
        return "Нет данных"
    return "\n".join(str(row) for row in rows)

def section(title, content):
    return f"\n\n===== {title} =====\n{content}"

@app.route("/")
def index():
    output = []

    connection = get_connection()
    cursor = connection.cursor()

    # 1. Версия базы данных PostgreSQL
    cursor.execute("SELECT version();")
    output.append(section(
        "1. Версия базы данных PostgreSQL",
        rows_to_text(cursor.fetchall())
    ))

    # 2. Названия таблиц в базе данных PostgreSQL
    cursor.execute("""
        SELECT schemaname, tablename
        FROM pg_catalog.pg_tables
        ORDER BY schemaname, tablename;
    """)
    tables = cursor.fetchall()
    output.append(section(
        f"2. Таблицы в базе данных PostgreSQL (всего: {len(tables)})",
        rows_to_text(tables)
    ))

    # 3, 4, 5. Берём 3 таблицы: pg_namespace, sql_features, students
    selected_tables = [
        ("pg_catalog",        "pg_namespace"),
        ("information_schema","sql_features"),
        ("public",            "students"),
    ]

    for schema_name, table_name in selected_tables:
        table_title = f"{schema_name}.{table_name}"

        # 3. Названия 3 любых столбцов
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position
            LIMIT 3;
        """, (schema_name, table_name))

        columns = [row[0] for row in cursor.fetchall()]

        output.append(section(
            f"3. Названия 3 столбцов таблицы {table_title}",
            rows_to_text([(c,) for c in columns])
        ))

        if not columns:
            continue

        # 4. Все записи 3 выбранных столбцов
        query_all = sql.SQL("SELECT {} FROM {}.{};").format(
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )
        cursor.execute(query_all)
        output.append(section(
            f"4. Все записи 3 столбцов таблицы {table_title}",
            rows_to_text(cursor.fetchall())
        ))

        # 5. Те же записи без дубликатов
        query_distinct = sql.SQL("SELECT DISTINCT {} FROM {}.{};").format(
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )
        cursor.execute(query_distinct)
        output.append(section(
            f"5. Записи 3 столбцов таблицы {table_title} без дубликатов",
            rows_to_text(cursor.fetchall())
        ))

    # 6. starelid, stanullfrac из pg_statistic где stanullfrac от 0.2 до 0.8
    cursor.execute("""
        SELECT starelid, stanullfrac
        FROM pg_catalog.pg_statistic
        WHERE stanullfrac BETWEEN 0.2 AND 0.8
        ORDER BY starelid;
    """)
    output.append(section(
        "6. starelid, stanullfrac из pg_statistic, где stanullfrac от 0.2 до 0.8",
        rows_to_text(cursor.fetchall())
    ))

    # 7. starelid, stanullfrac, stadistinct где stadistinct = 1.0 или 3.0
    cursor.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_catalog.pg_statistic
        WHERE stadistinct = 1.0 OR stadistinct = 3.0
        ORDER BY starelid;
    """)
    output.append(section(
        "7. starelid, stanullfrac, stadistinct из pg_statistic, где stadistinct = 1.0 или 3.0",
        rows_to_text(cursor.fetchall())
    ))

    # 8. starelid, stanullfrac, stadistinct где stadistinct = 1.0, сортировка по starelid ASC
    cursor.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_catalog.pg_statistic
        WHERE stadistinct = 1.0
        ORDER BY starelid ASC;
    """)
    output.append(section(
        "8. starelid, stanullfrac, stadistinct из pg_statistic, где stadistinct = 1.0 (↑ по starelid)",
        rows_to_text(cursor.fetchall())
    ))

    # 9. AVG(stawidth), MAX(stanullfrac), AVG(stadistinct), SUM(stadistinct) где starelid = 1247
    cursor.execute("""
        SELECT
            AVG(stawidth)    AS avg_stawidth,
            MAX(stanullfrac) AS max_stanullfrac,
            AVG(stadistinct) AS avg_stadistinct,
            SUM(stadistinct) AS sum_stadistinct
        FROM pg_catalog.pg_statistic
        WHERE starelid = 1247;
    """)
    output.append(section(
        "9. AVG(stawidth), MAX(stanullfrac), AVG(stadistinct), SUM(stadistinct) из pg_statistic, где starelid = 1247",
        rows_to_text(cursor.fetchall())
    ))

    cursor.close()
    connection.close()

    page_text = "\n".join(output)

    dev_domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    jupyter_url = "/jupyter/"

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>PostgreSQL — поэтапный вывод</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; margin: 0; }}
        .navbar {{
            background: #1a73e8;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin: -20px -20px 24px -20px;
        }}
        .navbar span {{ color: white; font-weight: bold; font-size: 1rem; flex: 1; }}
        .btn {{
            display: inline-block;
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: bold;
            text-decoration: none;
            cursor: pointer;
            border: none;
        }}
        .btn-active {{ background: white; color: #1a73e8; }}
        .btn-jupyter {{ background: #f57c00; color: white; }}
        .btn-jupyter:hover {{ background: #e65100; }}
        pre {{ background: white; padding: 20px; border-radius: 8px;
               white-space: pre-wrap; word-wrap: break-word; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="navbar">
        <span>PostgreSQL — поэтапный вывод данных</span>
        <a class="btn btn-active">Flask App</a>
        <a class="btn btn-jupyter" href="{jupyter_url}" target="_blank">Открыть Jupyter Notebook</a>
    </div>
    <pre>{escape(page_text)}</pre>
</body>
</html>"""

serve(app, host="127.0.0.1", port=5001)
