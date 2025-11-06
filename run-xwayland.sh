#!/bin/bash

# navigate to the script directory
DIR=$(dirname "$0")
cd "$DIR"

# runs with xwayland + uv package manager
QT_QPA_PLATFORM=xcb python ilgwg_desktop_gremlins.py "$@" 2>/dev/null &
PID=$!
disown $PID
