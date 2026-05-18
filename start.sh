#!/bin/bash
# start Postgres
pg_ctl stop -D "$PGDATA" 2>/dev/null || true

if [ ! -d "$PGDATA/base" ]; then
  initdb -D "$PGDATA"
  cp postgresql.conf.tpl "$PGDATA/postgresql.conf"

  socket_dir="$PWD/postgres"
  mkdir -p "$socket_dir"
  escaped_dir=$(echo "$socket_dir" | sed 's/\//\\\//g')
  sed -i "s/replace_unix_dir/${escaped_dir}/" "$PGDATA/postgresql.conf"
fi

pg_ctl -D "$PGDATA" -l "$PWD/postgresql.log" start

sleep 2

DB_USER=$(whoami)
if ! psql -h 127.0.0.1 -U "$DB_USER" -d appdb -c '\q' 2>/dev/null; then
  psql -h 127.0.0.1 -U "$DB_USER" -d postgres -c "CREATE DATABASE appdb;" 2>/dev/null || true
fi

# start Flask app
python main.py
