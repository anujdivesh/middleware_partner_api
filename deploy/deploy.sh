#!/usr/bin/env bash
# Deploy helper for the PaRTnR2 middleware API.
#
# Both modes use the single config file deploy/.env (template: deploy/.env.example).
#
# Local / development (no Docker, uses the vpartner virtualenv):
#   ./deploy/deploy.sh local [--install] [--port 8000] [--no-run]
#
# Production (Docker: postgres + gunicorn + nginx):
#   ./deploy/deploy.sh prod [up|down|restart|logs|status|migrate|createsuperuser|shell]
#   ./deploy/deploy.sh prod up --restore-latest [--yes]   deploy with the newest backup
#   ./deploy/deploy.sh prod up --restore FILE [--yes]     deploy with a specific backup
#
# Database backups (plain .sql in deploy/backups/, .sql.gz also restorable;
# newest = latest by name):
#   ./deploy/deploy.sh backup local|prod
#   ./deploy/deploy.sh backups                            list backups
set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DEPLOY_DIR/.." && pwd)"
ENV_FILE="$DEPLOY_DIR/.env"
BACKUP_DIR="$DEPLOY_DIR/backups"

# Override with VENV_ACTIVATE=/path/to/bin/activate if the venv lives elsewhere.
VENV_ACTIVATE="${VENV_ACTIVATE:-$ROOT_DIR/../vpartner/bin/activate}"

# Same project name the root docker-compose.yml used, so existing volumes
# (postgres_data, media_volume, static_volume) are reused, not recreated empty.
COMPOSE_PROJECT="middleware_partner_api"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.prod.yml"

log()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWARN:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

env_value() {
  grep -E "^$1=" "$ENV_FILE" | tail -n1 | cut -d= -f2- | sed -e 's/^["'\'']//' -e 's/["'\'']$//'
}

require_env_file() {
  if [[ ! -f "$ENV_FILE" ]]; then
    cp "$DEPLOY_DIR/.env.example" "$ENV_FILE"
    die "Created deploy/.env from deploy/.env.example - fill it in, then rerun."
  fi

  local key value missing=()
  for key in "$@"; do
    value="$(env_value "$key" || true)"
    if [[ -z "$value" || "$value" == "change_me" ]]; then
      missing+=("$key")
    fi
  done
  [[ ${#missing[@]} -eq 0 ]] || die "deploy/.env is missing values for: ${missing[*]}"
}

# ---------------------------------------------------------------- local ----

deploy_local() {
  local install=0 run=1 port=8000
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --install) install=1 ;;
      --no-run)  run=0 ;;
      --port)    port="${2:?--port needs a value}"; shift ;;
      -h|--help) usage ;;
      *) die "unknown option for local: $1" ;;
    esac
    shift
  done

  [[ -f "$VENV_ACTIVATE" ]] || die "virtualenv not found at $VENV_ACTIVATE (set VENV_ACTIVATE)"
  # shellcheck disable=SC1090
  source "$VENV_ACTIVATE"
  log "Using $(python --version) from $(command -v python)"

  require_env_file POSTGRES_PASSWORD

  export DJANGO_ENV=development
  cd "$ROOT_DIR"

  if [[ $install -eq 1 ]]; then
    log "Installing requirements"
    pip install -r requirements.txt
  fi

  log "Checking Django configuration and database connection"
  python manage.py check --database default

  log "Applying migrations"
  python manage.py migrate --noinput

  if [[ $run -eq 1 ]]; then
    log "Starting development server on http://127.0.0.1:$port/partner_api/"
    exec python manage.py runserver "127.0.0.1:$port"
  fi
  log "Done (server not started: --no-run)"
}

# ----------------------------------------------------------- production ----

# Prefer the compose plugin, fall back to standalone docker-compose.
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
else
  COMPOSE_CMD=(docker-compose)
fi

compose() {
  "${COMPOSE_CMD[@]}" \
    -p "$COMPOSE_PROJECT" \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    "$@"
}

check_prod_env() {
  command -v docker >/dev/null || die "docker is not installed"
  "${COMPOSE_CMD[@]}" version >/dev/null 2>&1 || die "neither 'docker compose' nor 'docker-compose' is available"

  require_env_file DJANGO_SECRET_KEY DJANGO_ALLOWED_HOSTS \
                   POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD

  if grep -qiE '^DJANGO_DEBUG=(1|true|yes|on)' "$ENV_FILE"; then
    warn "DJANGO_DEBUG is on in deploy/.env - it applies to production too."
  fi
}

wait_for_db() {
  local i
  for i in $(seq 1 60); do
    if compose exec -T db sh -c 'pg_isready -h localhost -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  die "database container did not become ready"
}

# Replace the production database with the contents of a backup file.
restore_prod_db() {
  local file="$1" assume_yes="$2"
  [[ -f "$file" ]] || die "backup not found: $file"

  log "Starting the database container"
  compose up -d db
  wait_for_db

  if [[ "$assume_yes" -ne 1 ]]; then
    warn "This REPLACES the production database '$(env_value POSTGRES_DB)' with $(basename "$file")."
    read -r -p "Type 'restore' to continue: " answer
    [[ "$answer" == "restore" ]] || die "restore cancelled"
  fi

  log "Safety backup of the current production database first"
  backup_prod "pre-restore"

  log "Stopping web so nothing is connected during the restore"
  compose stop web >/dev/null 2>&1 || true

  log "Recreating the database"
  compose exec -T db sh -c \
    'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres \
       -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\" WITH (FORCE)" \
       -c "CREATE DATABASE \"$POSTGRES_DB\" OWNER \"$POSTGRES_USER\""'

  log "Loading $(basename "$file")"
  # \restrict / \unrestrict lines come from newer pg_dump versions; older psql
  # in the postgres:14 image doesn't know them, and they aren't needed here.
  read_backup "$file" \
    | grep -vE '^\\(un)?restrict ' \
    | compose exec -T db sh -c 'psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null
  log "Restore complete"
}

deploy_prod() {
  local action="${1:-up}"
  [[ $# -gt 0 ]] && shift
  check_prod_env
  cd "$ROOT_DIR"

  case "$action" in
    up)
      local restore_file="" assume_yes=0
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --restore-latest) restore_file="$(latest_backup)" || die "no backups in deploy/backups/" ;;
          --restore)        restore_file="${2:?--restore needs a backup file}"; shift ;;
          --yes|-y)         assume_yes=1 ;;
          *) die "unknown option for prod up: $1" ;;
        esac
        shift
      done
      # Accept a bare file name from deploy/backups/.
      if [[ -n "$restore_file" && ! -f "$restore_file" && -f "$BACKUP_DIR/$restore_file" ]]; then
        restore_file="$BACKUP_DIR/$restore_file"
      fi

      log "Building images"
      compose build
      if [[ -n "$restore_file" ]]; then
        restore_prod_db "$restore_file" "$assume_yes"
      fi
      log "Starting containers (web runs migrate + collectstatic on start)"
      compose up -d --remove-orphans
      compose ps
      log "Follow logs with: ./deploy/deploy.sh prod logs"
      ;;
    down)            compose down "$@" ;;
    restart)         compose restart "$@" ;;
    logs)            compose logs -f --tail=200 "$@" ;;
    status|ps)       compose ps ;;
    migrate)         compose exec web python manage.py migrate --noinput ;;
    createsuperuser) compose exec web python manage.py createsuperuser ;;
    shell)           compose exec web python manage.py shell ;;
    -h|--help)       usage ;;
    *) die "unknown prod action: $action" ;;
  esac
}

# -------------------------------------------------------------- backups ----

# All backups (.sql and older .sql.gz), oldest first by name.
backup_files() {
  ls -1 "$BACKUP_DIR"/*.sql "$BACKUP_DIR"/*.sql.gz 2>/dev/null | sort || true
}

# Newest backup by file name (names start with a sortable timestamp).
latest_backup() {
  local latest
  latest="$(backup_files | tail -n1)"
  [[ -n "$latest" ]] || return 1
  echo "$latest"
}

# Print a backup's SQL, uncompressing .sql.gz files.
read_backup() {
  case "$1" in
    *.gz) gunzip -c "$1" ;;
    *)    cat "$1" ;;
  esac
}

new_backup_path() {
  mkdir -p "$BACKUP_DIR"
  echo "$BACKUP_DIR/$(date +%Y%m%d-%H%M%S)_$1.sql"
}

# Write stdin to a backup file atomically and report it.
save_backup() {
  local out="$1" tmp="$1.partial"
  cat > "$tmp"
  [[ -s "$tmp" ]] || { rm -f "$tmp"; die "backup came out empty"; }
  mv "$tmp" "$out"
  log "Backup written: deploy/backups/$(basename "$out") ($(du -h "$out" | cut -f1))"
}

backup_local() {
  command -v pg_dump >/dev/null || die "pg_dump is not installed"
  require_env_file POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD
  local out
  out="$(new_backup_path local)"
  log "Backing up local database $(env_value POSTGRES_DB) on $(env_value POSTGRES_HOST)"
  PGPASSWORD="$(env_value POSTGRES_PASSWORD)" pg_dump \
    -h "$(env_value POSTGRES_HOST)" -p "$(env_value POSTGRES_PORT)" \
    -U "$(env_value POSTGRES_USER)" -d "$(env_value POSTGRES_DB)" \
    --no-owner --no-privileges \
    | save_backup "$out"
}

backup_prod() {
  local label="${1:-prod}" out
  out="$(new_backup_path "$label")"
  log "Backing up production database (db container)"
  compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
    | save_backup "$out"
}

run_backup() {
  case "${1:-}" in
    local) backup_local ;;
    prod|production)
      check_prod_env
      cd "$ROOT_DIR"
      backup_prod
      ;;
    *) die "usage: ./deploy/deploy.sh backup local|prod" ;;
  esac
}

list_backups() {
  if [[ -z "$(backup_files)" ]]; then
    log "No backups yet in deploy/backups/"
    return
  fi
  backup_files | while read -r f; do
    printf '%8s  %s\n' "$(du -h "$f" | cut -f1)" "$(basename "$f")"
  done
  log "Latest: $(basename "$(latest_backup)")"
}

# ----------------------------------------------------------------- main ----

case "${1:-}" in
  local|dev|development) shift; deploy_local "$@" ;;
  prod|production)       shift; deploy_prod "$@" ;;
  backup)                shift; run_backup "$@" ;;
  backups)               list_backups ;;
  -h|--help|"")          usage ;;
  *) usage 1 ;;
esac
