#!/bin/bash

set -Eeuo pipefail

cd /app

if [[ "${RUN_MIGRATIONS:-true}" == "true" ]]; then
    python -m manage migrate --noinput
fi

if [[ "${LOAD_INITIAL_DATA:-false}" == "true" ]]; then
    python -m manage loaddata legal_forms.json group.json
fi

exec "$@"
