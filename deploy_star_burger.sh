#!/bin/bash
set -e
echo "Переходим в виртуальное окружение"
source venv/bin/activate
echo "Обновляем код из github"
git pull origin master
echo "Устанавливаем библиотеки"
echo "Pyton"
pip install -r requirements.txt
echo "Node JS:"
npm ci --dev
echo "Пересобираем проект JS"
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Выполняем миграции"
./manage.py migrate --noinput
echo "Коммитим изменения в git"
git commit -a --allow-empty-message -m ''
git push
echo "Обновляем статику"
./manage.py collectstatic --noinput
echo "Перезапускаем сайт"
systemctl restart star-burger
eval "$(grep ^ROLLBAR_ENVIRONMENT= .env)"
eval "$(grep ^ROLLBAR_ACCESS_TOKEN= .env)"
GIT_SHA=$(exec git rev-parse HEAD)
curl -H "Content-Type: application/json" -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -X POST -d '{"environment": "'"$ROLLBAR_ENVIRONMENT"'","revision": "'"$GIT_SHA"'","rollbar_name": "star-burger","local_username": "'"$USER"'","comment": "","status": "succeeded"}' https://api.rollbar.com/api/1/deploy
echo "Деплой завершен успешно"
