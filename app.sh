#!/bin/bash

export BACKEND_INTERFACE="${BACKEND_INTERFACE:-127.0.0.1}"
export BACKEND_PORT="${BACKEND_PORT:-8000}"
export BACKEND_HOSTNAME="${BACKEND_HOSTNAME:-localhost}"
export FRONTEND_INTERFACE="${FRONTEND_INTERFACE:-127.0.0.1}"
export FRONTEND_PORT="${FRONTEND_PORT:-8080}"

trap 'kill $pid 2> /dev/null' INT TERM EXIT QUIT
env -C backend uvicorn app:app --host "$BACKEND_INTERFACE" --port "$BACKEND_PORT" &
readonly pid=$!

env -C frontend npm run serve -- --host "$FRONTEND_INTERFACE" --port "$FRONTEND_PORT"
wait
