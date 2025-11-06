#!/bin/bash

DIR=$(dirname "$0")
cd "$DIR"

uv run ilgwg_desktop_gremlins.py "$@" 2>/dev/null &
PID=$!
disown $PID
