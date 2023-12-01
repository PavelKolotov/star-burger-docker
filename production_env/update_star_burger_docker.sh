#!/bin/bash

set -e

PROJECT_DIR=/opt/star-burger-docker

cd $PROJECT_DIR

ENV_FILE="$PROJECT_DIR/production_env/.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "Файл .env не найден"
    exit 1
fi

echo "Обновление репозитория"
git pull

echo "Пересборка Docker образов"
docker-compose -f $PROJECT_DIR/production_env/docker-compose.yml build

echo "Перезапуск контейнеров"
docker-compose -f $PROJECT_DIR/production_env/docker-compose.yml down
docker-compose -f $PROJECT_DIR/production_env/docker-compose.yml up -d

echo "Очистка неиспользуемых Docker образов и ресурсов"
docker system prune -af


docker cp production_env_django_1:/app/staticfiles /var/www/starburger/
docker cp production_env_frontend_1:/app/bundles /var/www/starburger/staticfiles

systemctl reload nginx


commit=`git rev-parse HEAD`

curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
     -H "accept: application/json" \
     -H "content-type: application/json" \
     -X POST "https://api.rollbar.com/api/1/deploy" \
     -d '{
  "environment": "production_env",
  "revision": "'$commit'",
  "rollbar_username": "admin",
  "local_username": "admin",
  "comment": "deploy",
  "status": "succeeded"
}'

if [ $? -eq 0 ]; then
   echo "Деплой успешно завершен."
else
    echo "Деплой не удался."
fi
