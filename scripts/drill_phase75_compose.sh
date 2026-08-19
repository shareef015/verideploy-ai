#!/usr/bin/env bash
set -euo pipefail
# Live local reliability drill. Run only on an isolated developer/CI Docker host.
compose=(docker compose -f docker-compose.yml)
cleanup() { "${compose[@]}" up -d postgres redis kafka minio keycloak ai-service gateway >/dev/null 2>&1 || true; }
trap cleanup EXIT

"${compose[@]}" up -d postgres redis kafka minio keycloak db-migrate ai-service gateway
curl --fail --silent http://localhost:4000/api/v1/health/ready >/dev/null

"${compose[@]}" restart ai-service gateway
curl --retry 20 --retry-delay 2 --retry-all-errors --fail --silent http://localhost:4000/api/v1/health/ready >/dev/null

for dependency in postgres redis kafka minio keycloak; do
  "${compose[@]}" stop "$dependency"
  if curl --silent --fail http://localhost:4000/api/v1/health/ready >/dev/null 2>&1; then
    echo "expected readiness failure while $dependency is stopped" >&2
    exit 1
  fi
  "${compose[@]}" start "$dependency"
  curl --retry 30 --retry-delay 2 --retry-all-errors --fail --silent http://localhost:4000/api/v1/health/ready >/dev/null
done

echo "Phase 75 live compose smoke/restart/dependency-failure drill: PASS"
