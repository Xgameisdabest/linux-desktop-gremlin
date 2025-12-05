#!/bin/bash

# an extremely simple gremlin picker using rofi

# get the directory where this script is *actually* located (even if symlinked)
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
	DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"

# list all gremlins in spritesheet (relative to script dir)
available_gremlins=$(command ls -1 "$SCRIPT_DIR/spritesheet" 2>/dev/null)

# use rofi to pick the selected gremlin

main_menu() {
	pick=$(echo -e "$available_gremlins\nExit" | rofi -dmenu)

	if [[ -z $pick || $pick == "Exit" ]]; then
		exit 0
	fi

	"$SCRIPT_DIR/run.sh" "$pick"
}

main_menu
