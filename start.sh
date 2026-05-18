#!/bin/bash
# Указывает, что скрипт нужно выполнять с помощью Bash

# start Postgres
# Комментарий: дальше запускается PostgreSQL

pg_ctl stop -D "$PGDATA" 2>/dev/null || true
# Пытается остановить PostgreSQL, использующий каталог данных $PGDATA
# 2>/dev/null скрывает ошибки
# || true не даёт скрипту завершиться с ошибкой, если PostgreSQL не был запущен

if [ ! -d "$PGDATA/base" ]; then
# Проверяет, существует ли каталог "$PGDATA/base"
# Если его нет, значит база PostgreSQL ещё не инициализирована

  initdb -D "$PGDATA"
  # Инициализирует новый каталог данных PostgreSQL в $PGDATA

  cp postgresql.conf.tpl "$PGDATA/postgresql.conf"
  # Копирует шаблон конфигурации PostgreSQL в рабочий конфигурационный файл

  socket_dir="$PWD/postgres"
  # Создаёт переменную socket_dir
  # В ней хранится путь к папке postgres внутри текущей директории проекта

  mkdir -p "$socket_dir"
  # Создаёт директорию для Unix-сокета PostgreSQL
  # Флаг -p не выдаёт ошибку, если директория уже существует

  escaped_dir=$(echo "$socket_dir" | sed 's/\//\\\//g')
  # Экранирует символы / в пути
  # Это нужно, чтобы путь можно было безопасно вставить в команду sed

  sed -i "s/replace_unix_dir/${escaped_dir}/" "$PGDATA/postgresql.conf"
  # Заменяет строку replace_unix_dir в postgresql.conf на путь к директории сокета
fi
# Конец блока инициализации PostgreSQL

pg_ctl -D "$PGDATA" -l "$PWD/postgresql.log" start
# Запускает PostgreSQL
# -D "$PGDATA" указывает каталог данных
# -l "$PWD/postgresql.log" указывает файл для логов

sleep 2
# Ждёт 2 секунды, чтобы PostgreSQL успел запуститься

DB_USER=$(whoami)
# Сохраняет имя текущего пользователя системы в переменную DB_USER

if ! psql -h 127.0.0.1 -U "$DB_USER" -d appdb -c '\q' 2>/dev/null; then
# Проверяет, можно ли подключиться к базе appdb
# -h 127.0.0.1 подключается по TCP к localhost
# -U "$DB_USER" использует текущего пользователя
# -d appdb указывает базу данных appdb
# -c '\q' сразу выходит из psql
# Если подключиться не удалось, выполняется блок then

  psql -h 127.0.0.1 -U "$DB_USER" -d postgres -c "CREATE DATABASE appdb;" 2>/dev/null || true
  # Подключается к системной базе postgres
  # Пытается создать базу данных appdb
  # Ошибки скрываются
  # || true не даёт скрипту упасть, если база уже существует или возникла другая ошибка
fi
# Конец проверки и создания базы appdb

# start Flask app
# Комментарий: дальше запускается Flask-приложение

python main.py
# Запускает Python-файл main.py, в котором находится Flask-приложение