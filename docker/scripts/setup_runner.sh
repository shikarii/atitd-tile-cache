#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${RUNNER_TOKEN:-}" ]]; then
  echo "RUNNER_TOKEN is required. Export it before running this script."
  exit 1
fi

docker compose -f docker/docker-compose.yml up -d runner
docker compose -f docker/docker-compose.yml ps runner
