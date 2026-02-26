#!/usr/bin/env bash
# Wait for app health then run integration tests
set -euo pipefail
echo "waiting for app health..."
python - <<'PY'
import time, requests, sys
for i in range(300):
    try:
        r = requests.get('http://app:8000/health', timeout=1)
        if r.status_code == 200:
            print('app healthy')
            break
    except Exception:
        pass
    time.sleep(0.2)
else:
    print('timeout waiting for app', file=sys.stderr)
    sys.exit(2)
PY

echo "resetting test database..."
python - <<'PY'
import os
try:
    from pymongo import MongoClient
except Exception:
    print('pymongo not available; skipping DB reset')
    raise

uri = os.environ.get('MONGO_CONNECTION_STRING', 'mongodb://mongo:27017')
client = MongoClient(uri)
db_name = 'deriven-database'
try:
    client.drop_database(db_name)
    print(f'dropped database {db_name}')
except Exception as e:
    print('failed to drop database:', e)
    # don't abort tests; continue
PY

echo "running integration tests..."
pytest -v tests/integration -q || pytest -v -q
