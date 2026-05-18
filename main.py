from flask import Flask
from waitress import serve
import psycopg2
from psycopg2 import sql
from html import escape

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database="appdb",
        user="runner"
    )

def rows_to_text(rows):
    if not rows:
        return "Нет данных"

    result = []
    for row in rows:
        result.append(str(row))

    return "\n".join(result)

def section(title, content):
    return f"\n\n===== {title} =====\n{content}"

@app.route("/")
def index():
    output = []

    connection = get_connection()
    cursor = connection.cursor()

    # 1. Информация о версии базы данных PostgreSQL
    cursor.execute("SELECT version();")
    output.append(section(
        "1. Версия базы данных PostgreSQL",
        rows_to_text(cursor.fetchall())
    ))

    # 2. Названия таблиц в базе данных PostgreSQL
    cursor.execute("""
        SELECT schemaname, tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname NOT IN ('information_schema')
        ORDER BY schemaname, tablename;
    """)
    tables = cursor.fetchall()

    output.append(section(
        "2. Таблицы в базе данных PostgreSQL",
        rows_to_text(tables)
    ))

    # Берём 3 любые таблицы из найденных
    selected_tables = tables[:3]

    output.append(section(
        "3. Выбранные 3 таблицы",
        rows_to_text(selected_tables)
    ))

    # 3, 4, 5. Столбцы, все записи, записи без дублей
    for schema_name, table_name in selected_tables:
        table_title = f"{schema_name}.{table_name}"

        # Названия 3 любых столбцов выбранной таблицы
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
            rows_to_text([(column,) for column in columns])
        ))

        if not columns:
            output.append(section(
                f"Таблица {table_title}",
                "В таблице нет столбцов"
            ))
            continue

        # Все записи 3 любых столбцов из выбранной таблицы
        query_all = sql.SQL("SELECT {} FROM {}.{};").format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )

        cursor.execute(query_all)
        output.append(section(
            f"4. Все записи 3 столбцов таблицы {table_title}",
            rows_to_text(cursor.fetchall())
        ))

        # Все записи 3 любых столбцов с устранением дубликатов
        query_distinct = sql.SQL("SELECT DISTINCT {} FROM {}.{};").format(
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )

        cursor.execute(query_distinct)
        output.append(section(
            f"5. Все записи 3 столбцов таблицы {table_title} без дубликатов",
            rows_to_text(cursor.fetchall())
        ))

    # 6. starelid, stanullfrac из pg_statistic,
    # где stanullfrac от 0.2 до 0.8
    cursor.execute("""
        SELECT starelid, stanullfrac
        FROM pg_catalog.pg_statistic
        WHERE stanullfrac BETWEEN 0.2 AND 0.8;
    """)

    output.append(section(
        "6. starelid, stanullfrac из pg_statistic, где stanullfrac от 0.2 до 0.8",
        rows_to_text(cursor.fetchall())
    ))

    # 7. starelid, stanullfrac, stadistinct из pg_statistic,
    # где stadistinct равен 1.0 или 3.0
    cursor.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_catalog.pg_statistic
        WHERE stadistinct = 1.0
           OR stadistinct = 3.0;
    """)

    output.append(section(
        "7. starelid, stanullfrac, stadistinct из pg_statistic, где stadistinct = 1.0 или 3.0",
rows_to_text(cursor.fetchall())
    ))

    # 8. starelid, stanullfrac, stadistinct из pg_statistic,
    # где stadistinct равен 1.0,
    # сортировка по возрастанию starelid
    cursor.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_catalog.pg_statistic
        WHERE stadistinct = 1.0
        ORDER BY starelid ASC;
    """)

    output.append(section(
        "8. pg_statistic, где stadistinct = 1.0, сортировка по starelid",
        rows_to_text(cursor.fetchall())
    ))

    # 9. Среднее stawidth, максимум stanullfrac,
    # среднее stadistinct и сумма stadistinct,
    # где starelid = 1247
    cursor.execute("""
        SELECT
            AVG(stawidth) AS average_stawidth,
            MAX(stanullfrac) AS max_stanullfrac,
            AVG(stadistinct) AS average_stadistinct,
            SUM(stadistinct) AS sum_stadistinct
        FROM pg_catalog.pg_statistic
        WHERE starelid = 1247;
    """)

    output.append(section(
        "9. Агрегатные значения из pg_statistic, где starelid = 1247",
        rows_to_text(cursor.fetchall())
    ))

    cursor.close()
    connection.close()

    page_text = "\n".join(output)

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Задание 11</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #f5f5f5;
            }}
            pre {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <h1>Задание 11</h1>
        <pre>{escape(page_text)}</pre>
    </body>
    </html>
    """

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000, url_scheme="https")