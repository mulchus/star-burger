#!/bin/bash
set -e

echo "Обновляем код из github"
git pull origin master

echo "Обновляем настройки Nginx и перезапускаем его"
cp star-burger /etc/nginx/sites-enabled/
systemctl restart nginx

echo "Создаем volume для media"
if ! [ -d /home/star-burger/web/media ]; then
        mkdir /home/star-burger/web/media
fi
docker volume create --driver local --opt type=none --opt device=/home/star-burger/web/media --opt o=bind star-burger_media_volume

echo "Создаем/обновляем образы web, db"
docker-compose -f docker-compose.prod.yml up -d --build
docker exec -u root star-burger_web_1 chown star-burger:star-burger /home/star-burger/web/media

echo "Собираем статику"
docker-compose -f docker-compose.prod.yml exec web python3 manage.py collectstatic --noinput

echo "Копируем статику на хост"
docker cp star-burger_web_1:/home/star-burger/web/staticfiles /home/star-burger/web/

echo "Выполняем миграции"
docker-compose -f docker-compose.prod.yml exec web python3 manage.py migrate --noinput

echo "Загружаем в БД данные"
cat data.json | sudo docker exec -i star-burger_web_1 python manage.py loaddata --format=json -

echo "Отправляем сообщение ROLLBAR"
eval "$(grep ^ROLLBAR_ENVIRONMENT= .env.prod)"
eval "$(grep ^ROLLBAR_ACCESS_TOKEN= .env.prod)"
GIT_SHA=$(exec git rev-parse HEAD)
curl -H "Content-Type: application/json" -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -X POST -d '{"environment": "'"$ROLLBAR_ENVIRONMENT"'","revision": "'"$GIT_SHA"'","rollbar_name": "star-burger","local_username": "'"$USER"'","comment": "New deploy on server","status": "succeeded"}' https://api.rollbar.com/api/1/deploy

echo "Деплой завершен успешно"
