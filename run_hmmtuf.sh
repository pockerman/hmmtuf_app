#!/bin/bash
clear

export DJANGO_SETTINGS_MODULE=hmmtuf.settings

read  -p "Enter option [0-2] (0 = Quit, 1 = Debug, 2 = Local deploy) > "

if [[ "$REPLY" =~ ^[0-2]$ ]]; then
	if [[ "$REPLY" == 0 ]]; then
		echo "Quiting..."
		exit
	fi

	if [[ "$REPLY" == 1 ]]; then
		echo "Running local dev..."
		python3 manage.py runserver
	fi

	if [[ "$REPLY" == 2 ]]; then
		echo "Running local deploy dev..."
		echo "Stopping Gunicorn..."
		sudo systemctl stop gunicorn
		echo "Stopping nginx..."
		sudo systemctl stop nginx

		echo "Start Gunicorn..."
		sudo systemctl start gunicorn

		echo "Start nginx..."
		sudo systemctl start nginx
	fi
else

	echo "Unknown option ${REPLY} was given" >&2
	exit 1
fi




