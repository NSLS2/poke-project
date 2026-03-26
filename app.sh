#!/bin/bash

export BACKEND_PORT="${BACKEND_PORT:-8000}"
export FRONTEND_PORT="${FRONTEND_PORT:-8080}"

trap 'kill $pid 2> /dev/null' INT TERM EXIT QUIT
env -C backend uvicorn app:app --port "$BACKEND_PORT" &
readonly pid=$!

env -C frontend npm run serve -- --port "$FRONTEND_PORT"
wait
