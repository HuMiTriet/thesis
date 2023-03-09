#!/usr/bin/env bash

check_env_loaded() {
	if [[ "$VIRTUAL_ENV" == "" ]]; then
		echo "Please source a virtual env before cont"
		exit 1
	fi
}

start_server() {
	flask --app server run --port 5000 &
	flask --app registrar run --port 5001 &
	flask --app client run --port 5002 &
	flask --app client run --port 5003 &
}

end_server() {
	kill -9 "$(lsof -t -i:5000)"
	kill -9 "$(lsof -t -i:5001)"
	kill -9 "$(lsof -t -i:5002)"
	kill -9 "$(lsof -t -i:5003)"
}

if [[ "$1" == "start" ]]; then
	check_env_loaded
	start_server
elif [[ "$1" == "end" ]]; then
	check_env_loaded
	end_server
fi
