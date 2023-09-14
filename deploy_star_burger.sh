#!/bin/bash
set -e

echo "Обновляем код из github"
git pull origin master
chmod u+x entrypoint.prod.sh
chmod u+x delete.sh

echo "Обновляем настройки Nginx и перезапускаем его"
cp star-burger /etc/nginx/sites-enabled/
systemctl restart nginx

echo "Создаем/обновляем образы web, db"
docker-compose -f docker-compose.prod.yml up -d --build
docker update --restart unless-stopped star-burger_web_1 star-burger_db_1
docker exec -u root star-burger_web_1 chown star-burger:star-burger /home/star-burger/web/media
docker exec -u root star-burger_web_1 chown star-burger:star-burger /home/star-burger/web/staticfiles

echo "Создаем папку staticfiles"
if ! [ -d ./staticfiles ]; then
                mkdir staticfiles
fi

echo "Собираем статику"
docker-compose -f docker-compose.prod.yml exec web python3 manage.py collectstatic --noinput

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
