# start Postgres
pg_ctl stop

if [ ! -d "data/base" ]; then
  initdb
  cp postgresql.conf.tpl data/postgresql.conf
  
  socker_dir="\/home\/runner\/${REPL_SLUG}\/postgres"
  
  sed -i "s/replace_unix_dir/${socker_dir}/" data/postgresql.conf
fi

pg_ctl -l /home/runner/${REPL_SLUG}/postgresql.log start

sleep 2

if ! psql -h 127.0.0.1 -d appdb -c '\q' 2>/dev/null; then
  psql -h 127.0.0.1 -d postgres -c "create database appdb;" 2>/dev/null || true
fi

# start Flask app
python main.py
