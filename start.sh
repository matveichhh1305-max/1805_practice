#!/bin/bash
set -e

mkdir -p logs postgres

# ── PostgreSQL ──────────────────────────────────────────────
pg_ctl stop -D "$PGDATA" 2>/dev/null || true

if [ ! -d "$PGDATA/base" ]; then
  initdb -D "$PGDATA"
  cp postgresql.conf.tpl "$PGDATA/postgresql.conf"
  socket_dir="$PWD/postgres"
  escaped_dir=$(echo "$socket_dir" | sed 's/\//\\\//g')
  sed -i "s/replace_unix_dir/${escaped_dir}/" "$PGDATA/postgresql.conf"
fi

pg_ctl -D "$PGDATA" -l "$PWD/postgresql.log" start
sleep 2

DB_USER=$(whoami)
if ! psql -h 127.0.0.1 -U "$DB_USER" -d appdb -c '\q' 2>/dev/null; then
  psql -h 127.0.0.1 -U "$DB_USER" -d postgres -c "CREATE DATABASE appdb;" 2>/dev/null || true
fi

# ── Jupyter on internal port 5002 ───────────────────────────
jupyter notebook \
  --ip=127.0.0.1 \
  --port=5002 \
  --no-browser \
  --ServerApp.token='' \
  --ServerApp.password='' \
  --ServerApp.allow_origin='*' \
  --ServerApp.base_url='/jupyter/' \
  --ServerApp.disable_check_xsrf=True &

# ── Flask on internal port 5001 ─────────────────────────────
python main.py &

# ── nginx on port 5000 (only public port) ───────────────────
sleep 3
nginx -c "$PWD/nginx.conf" -g "daemon off;"
