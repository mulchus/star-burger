#!/bin/bash
set -e
echo "Переходим в виртуальное окружение"
source venv/bin/activate
echo $(whereis python)
echo "Обновляем код из github"
echo $(git pull origin master)
echo "Устанавливаем библиотеки"
echo "python:"
echo $(pip install -r requirements.txt)
echo "Node JS:"
echo $(npm ci --dev)
echo "Пересобираем проект JS"
echo $(./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./")
echo "Выполняем миграции"
echo $(./manage.py migrate --noinput)
echo "Обновляем статику"
echo $(./manage.py collectstatic --noinput)
echo "Перезапускаем сайт"
echo $(systemctl restart star-burger)
echo "Деплой завершен успешно"
