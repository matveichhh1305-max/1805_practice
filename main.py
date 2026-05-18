from flask import Flask
from waitress import serve
import psycopg2
import os

app = Flask(__name__)

def get_connection():
    username = os.environ.get('USER', 'runner')
    return psycopg2.connect(host="127.0.0.1", database="appdb", user=username)

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()

    sections = []

    # 1. Версия базы данных
    cur.execute("SELECT version();")
    db_version = cur.fetchone()[0]
    sections.append({
        "title": "1. Версия базы данных PostgreSQL",
        "headers": ["version"],
        "rows": [[db_version]]
    })

    # 2. Названия всех таблиц во всех схемах
    cur.execute("""
        SELECT schemaname, tablename
        FROM pg_tables
        ORDER BY schemaname, tablename;
    """)
    tables = cur.fetchall()
    sections.append({
        "title": f"2. Таблицы в базе данных (всего: {len(tables)})",
        "headers": ["schemaname", "tablename"],
        "rows": tables
    })

    # 3. Столбцы 3 таблиц из разных схем: pg_namespace, sql_features, students
    chosen = [
        ("pg_catalog",        "pg_namespace"),
        ("information_schema","sql_features"),
        ("public",            "students"),
    ]
    for schema, table in chosen:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        sections.append({
            "title": f"3. Столбцы таблицы «{schema}.{table}»",
            "headers": ["column_name", "data_type"],
            "rows": cur.fetchall()
        })

    # 4. Все записи 3 выбранных столбцов из тех же таблиц
    cur.execute("SELECT nspname, nspowner, nspacl FROM pg_catalog.pg_namespace;")
    sections.append({
        "title": "4. Записи «pg_catalog.pg_namespace» (nspname, nspowner, nspacl)",
        "headers": ["nspname", "nspowner", "nspacl"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT feature_id, feature_name, is_supported FROM information_schema.sql_features;")
    sections.append({
        "title": "4. Записи «information_schema.sql_features» (feature_id, feature_name, is_supported)",
        "headers": ["feature_id", "feature_name", "is_supported"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT name, age, city FROM public.students;")
    sections.append({
        "title": "4. Записи «public.students» (name, age, city)",
        "headers": ["name", "age", "city"],
        "rows": cur.fetchall()
    })

    # 5. Те же записи с устранением дубликатов (DISTINCT)
    cur.execute("SELECT DISTINCT nspname, nspowner, nspacl FROM pg_catalog.pg_namespace;")
    sections.append({
        "title": "5. Записи «pg_catalog.pg_namespace» — без дубликатов",
        "headers": ["nspname", "nspowner", "nspacl"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT DISTINCT feature_id, feature_name, is_supported FROM information_schema.sql_features;")
    sections.append({
        "title": "5. Записи «information_schema.sql_features» — без дубликатов",
        "headers": ["feature_id", "feature_name", "is_supported"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT DISTINCT name, age, city FROM public.students;")
    sections.append({
        "title": "5. Записи «public.students» — без дубликатов",
        "headers": ["name", "age", "city"],
        "rows": cur.fetchall()
    })

    # 6. starelid, relname, stanullfrac из pg_statistic где stanullfrac от 0.2 до 0.8
    cur.execute("""
        SELECT s.starelid, c.relname, s.stanullfrac
        FROM pg_statistic s
        JOIN pg_class c ON c.oid = s.starelid
        WHERE s.stanullfrac BETWEEN 0.2 AND 0.8
        ORDER BY s.starelid;
    """)
    sections.append({
        "title": "6. pg_statistic: starelid, relname, stanullfrac (от 0.2 до 0.8)",
        "headers": ["starelid", "relname", "stanullfrac"],
        "rows": cur.fetchall()
    })

    # 7. starelid, stanullfrac, stadistinct где stadistinct = 1.0 или 3.0
    cur.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_statistic
        WHERE stadistinct = 1.0 OR stadistinct = 3.0
        ORDER BY starelid;
    """)
    sections.append({
        "title": "7. pg_statistic: starelid, stanullfrac, stadistinct — где stadistinct = 1.0 или 3.0",
        "headers": ["starelid", "stanullfrac", "stadistinct"],
        "rows": cur.fetchall()
    })

    # 8. starelid, stanullfrac, stadistinct где stadistinct = 1.0, сортировка по starelid ASC
    cur.execute("""
        SELECT starelid, stanullfrac, stadistinct
        FROM pg_statistic
        WHERE stadistinct = 1.0
        ORDER BY starelid ASC;
    """)
    sections.append({
        "title": "8. pg_statistic: starelid, stanullfrac, stadistinct — где stadistinct = 1.0 (сортировка по starelid ↑)",
        "headers": ["starelid", "stanullfrac", "stadistinct"],
        "rows": cur.fetchall()
    })

    # 9. AVG(stawidth), MAX(stanullfrac), AVG(stadistinct), SUM(stadistinct) где starelid = 1247
    cur.execute("""
        SELECT
            AVG(stawidth)    AS avg_stawidth,
            MAX(stanullfrac) AS max_stanullfrac,
            AVG(stadistinct) AS avg_stadistinct,
            SUM(stadistinct) AS sum_stadistinct
        FROM pg_statistic
        WHERE starelid = 1247;
    """)
    sections.append({
        "title": "9. pg_statistic (starelid = 1247): AVG(stawidth), MAX(stanullfrac), AVG(stadistinct), SUM(stadistinct)",
        "headers": ["avg_stawidth", "max_stanullfrac", "avg_stadistinct", "sum_stadistinct"],
        "rows": cur.fetchall()
    })

    cur.close()
    conn.close()

    # Рендер HTML
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>PostgreSQL — поэтапный вывод</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; background: #f5f7fa; color: #222; }
    h1 { color: #2c3e50; margin-bottom: 30px; }
    .section { background: #fff; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                margin-bottom: 28px; padding: 20px 24px; }
    h2 { font-size: 1.05rem; color: #1a73e8; margin: 0 0 14px 0; }
    table { border-collapse: collapse; width: 100%; }
    th { background: #1a73e8; color: #fff; padding: 8px 12px; text-align: left; font-size: 0.85rem; }
    td { padding: 7px 12px; border-bottom: 1px solid #e8eaf0; font-size: 0.88rem; }
    tr:last-child td { border-bottom: none; }
    tr:nth-child(even) td { background: #f0f4ff; }
    .empty { color: #999; font-size: 0.85rem; }
  </style>
</head>
<body>
<h1>PostgreSQL — поэтапный вывод данных</h1>
"""

    for sec in sections:
        html += f'<div class="section"><h2>{sec["title"]}</h2>'
        if not sec["rows"]:
            html += '<p class="empty">Нет данных</p>'
        else:
            html += "<table><thead><tr>"
            for h in sec["headers"]:
                html += f"<th>{h}</th>"
            html += "</tr></thead><tbody>"
            for row in sec["rows"]:
                html += "<tr>"
                for cell in row:
                    html += f"<td>{cell}</td>"
                html += "</tr>"
            html += "</tbody></table>"
        html += "</div>"

    html += "</body></html>"
    return html

serve(app, host='0.0.0.0', port=5000, url_scheme='https')
