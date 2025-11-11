#!/bin/bash

# an extremely simple gremlin picker using rofi

# list all gremlins in spritesheet
available_gremlins=$(command ls -1 spritesheet)

# use rofi to pick the selected gremlin
pick=$(echo -e "$available_gremlins" | rofi -dmenu)

if [[ -z $pick ]]; then
	exit 0
fi

# check which session to launch (use uv)
if [[ $XDG_SESSION_TYPE == "wayland" ]]; then
	#check whether if they want to use uv or not
	pick_uv=$(echo -e "Uv\nNon-uv" | rofi -dmenu)
	if [[ $pick_uv == "Uv" ]]; then
		./run-uv-xwayland.sh $pick
	elif [[ $pick_uv == "Non-Uv" ]]; then
		./run-xwayland.sh $pick
	fi
elif [[ $XDG_SESSION_TYPE == "x11" ]]; then
	#check whether if they want to use uv or not
	pick_uv=$(echo -e "Uv\nNon-uv" | rofi -dmenu)
	if [[ $pick_uv == "Uv" ]]; then
		./run-uv-x11.sh $pick
	elif [[ $pick_uv == "Non-Uv" ]]; then
		./run-x11.sh $pick
	fi
fi
