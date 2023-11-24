#!/bin/bash

python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении миграций"
    exit 1
fi

python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo "Ошибка при выполнении collectstatic"
    exit 1
fi

exec gunicorn -w 3 star_burger.wsgi:application --bind 0.0.0.0:8081
