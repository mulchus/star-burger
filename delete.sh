#!/bin/bash
# set -e

echo "Stop containers"
docker stop star-burger_web_1
docker stop star-burger_db_1
docker stop star-burger_nginx_1

echo "Remove containers"
docker rm star-burger_web_1
docker rm star-burger_db_1
docker rm star-burger_nginx_1

echo "Remove images"
docker rmi star-burger_web
docker rmi star-burger_db
docker rmi star-burger_nginx
echo "Prune all old data"
docker system prune -a -f

echo "Очистка успешно завершена"
