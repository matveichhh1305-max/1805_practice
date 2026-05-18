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

    # 2. Названия таблиц в базе данных
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

    # 3. Названия столбцов 3 таблиц: students, courses, grades
    for table in ["students", "courses", "grades"]:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table,))
        cols = cur.fetchall()
        sections.append({
            "title": f"3. Столбцы таблицы «{table}»",
            "headers": ["column_name", "data_type"],
            "rows": cols
        })

    # 4. Все записи 3 столбцов из выбранных таблиц
    cur.execute("SELECT name, age, city FROM students;")
    sections.append({
        "title": "4. Записи таблицы «students» (name, age, city)",
        "headers": ["name", "age", "city"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT title, department, credits FROM courses;")
    sections.append({
        "title": "4. Записи таблицы «courses» (title, department, credits)",
        "headers": ["title", "department", "credits"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT student_id, course_id, grade FROM grades;")
    sections.append({
        "title": "4. Записи таблицы «grades» (student_id, course_id, grade)",
        "headers": ["student_id", "course_id", "grade"],
        "rows": cur.fetchall()
    })

    # 5. Те же записи с устранением дубликатов (DISTINCT)
    cur.execute("SELECT DISTINCT name, age, city FROM students;")
    sections.append({
        "title": "5. Записи «students» (name, age, city) — без дубликатов",
        "headers": ["name", "age", "city"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT DISTINCT title, department, credits FROM courses;")
    sections.append({
        "title": "5. Записи «courses» (title, department, credits) — без дубликатов",
        "headers": ["title", "department", "credits"],
        "rows": cur.fetchall()
    })

    cur.execute("SELECT DISTINCT student_id, course_id, grade FROM grades;")
    sections.append({
        "title": "5. Записи «grades» (student_id, course_id, grade) — без дубликатов",
        "headers": ["student_id", "course_id", "grade"],
        "rows": cur.fetchall()
    })

    # 6. starelid, stanullfrac из pg_statistic где stanullfrac между 0.2 и 0.8
    cur.execute("""
        SELECT s.starelid, c.relname, s.stanullfrac
        FROM pg_statistic s
        JOIN pg_class c ON c.oid = s.starelid
        WHERE s.stanullfrac BETWEEN 0.2 AND 0.8
        ORDER BY s.starelid;
    """)
    sections.append({
        "title": "6. pg_statistic: starelid, relname и stanullfrac (от 0.2 до 0.8)",
        "headers": ["starelid", "relname", "stanullfrac"],
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
