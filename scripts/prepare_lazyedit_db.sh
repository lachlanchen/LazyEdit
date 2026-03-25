#!/bin/bash
set -euo pipefail

# prepare_lazyedit_db.sh
# Installs PostgreSQL if needed, ensures the lazyedit_db database exists,
# sets passwords for postgres/lachlan, and grants lazyedit_db privileges.
#
# Safe to rerun:
# - apt skips already-installed packages
# - cluster/service start is idempotent
# - roles/passwords are updated in place
# - database creation is guarded
# - grants are safe to repeat

if [[ $EUID -ne 0 ]]; then
    echo "Please run with sudo." >&2
    exit 1
fi

DB_NAME="${DB_NAME:-lazyedit_db}"
APP_USER="${APP_USER:-lachlan}"
APP_PASSWORD="${APP_PASSWORD:-the11thfzpe.g.}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-the11th3ddaq}"

echo "Preparing PostgreSQL for LazyEdit..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y postgresql postgresql-client

echo "Ensuring PostgreSQL service is enabled and running..."
systemctl enable --now postgresql

echo "Setting postgres password..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';"

echo "Ensuring application role ${APP_USER} exists..."
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${APP_USER}'" | grep -qx '1'; then
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE ROLE ${APP_USER} LOGIN PASSWORD '${APP_PASSWORD}';"
else
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER ${APP_USER} WITH PASSWORD '${APP_PASSWORD}';"
fi

echo "Ensuring database ${DB_NAME} exists..."
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -qx '1'; then
    sudo -u postgres createdb -O "${APP_USER}" "${DB_NAME}"
fi

echo "Granting privileges..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${APP_USER};"

echo "Database ready."
echo "Suggested DSN:"
echo "postgresql://${APP_USER}:${APP_PASSWORD}@localhost:5432/${DB_NAME}"
