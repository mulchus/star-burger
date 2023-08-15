#!/bin/bash
# set -e
echo "Переходим в виртуальное окружение"
source venv/bin/activate
echo $(whereis python)
echo "Отчищаем историю сессий сайта"
echo $(python3 manage.py clearsessions)
echo "Очистка истории сессий сайта успешно завершена"
