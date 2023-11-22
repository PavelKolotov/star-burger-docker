#!/bin/bash

set -e

PROJECT_DIR=/opt/star-burger-docker

cd $PROJECT_DIR

ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "Файл .env не найден"
    exit 1
fi

echo "Обновление репозитория"
git pull

echo "Пересборка Docker образов"
docker-compose -f $PROJECT_DIR/production/docker-compose.yml build

echo "Перезапуск контейнеров"
docker-compose -f $PROJECT_DIR/production/docker-compose.yml down
docker-compose -f $PROJECT_DIR/production/docker-compose.yml up -d

echo "Очистка неиспользуемых Docker образов и ресурсов"
docker system prune -af

commit=`git rev-parse HEAD`

curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
     -H "accept: application/json" \
     -H "content-type: application/json" \
     -X POST "https://api.rollbar.com/api/1/deploy" \
     -d '{
  "environment": "production",
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
