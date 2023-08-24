#!/bin/bash
set -e
echo "Обновляем код из github"
git pull origin master
echo "Создаем/обновляем образы web, db, nginx"
docker-compose -f docker-compose.prod.yml up -d --build
echo "Собираем статику"
docker-compose -f docker-compose.prod.yml exec web python3 manage.py collectstatic --noinput
echo "Выполняем миграции"
docker-compose -f docker-compose.prod.yml exec web python3 manage.py migrate --noinput
echo "Загружаем в БД данные"
cat data.json | sudo docker exec -i star-burger_web_1 python manage.py loaddata --format=json -
eval "$(grep ^ROLLBAR_ENVIRONMENT= .env)"
eval "$(grep ^ROLLBAR_ACCESS_TOKEN= .env)"
GIT_SHA=$(exec git rev-parse HEAD)
curl -H "Content-Type: application/json" -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -X POST -d '{"environment": "'"$ROLLBAR_ENVIRONMENT"'","revision": "'"$GIT_SHA"'","rollbar_name": "star-burger","local_username": "'"$USER"'","comment": "New deploy on server","status": "succeeded"}' https://api.rollbar.com/api/1/deploy
echo "Деплой завершен успешно"
