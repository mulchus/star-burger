# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

[ссылка на сайт - https://testoftest.ru/](https://testoftest.ru/)
![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

### 1. [Установите Python](https://www.python.org/), если он отсутствует.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.6.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.


### 2. Для обеспечения работы базы данных PostgreSQL требуется [его установка в Linux](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-22-04):

- обновите кэш менеджера пакетов:
```sh
sudo apt update
```

- установите СУБД PostgreSQL:
```sh
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib
```

- проверьте правильность установки (должна отобразиться версия PostgreSQL / Linux)
```sh
pg_config --version
```

Затем создайте базу данных PostgreSQL и инициализируйте её:
переходим в PostgreSQL
```sh
sudo -u postgres psql
```

возможно предварительно понадобиться включить PostgreSQL:
```sh
sudo pg_lsclusters
sudo pg_ctlcluster [Ver кластера] main start
```

### 2.2. Установите [сервер Nginx](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)
Затем создайте файл настроек:
```sh
vi /etc/nginx/sites-enabled/star-burger
```
со следующим содержимым:
```
# HTTP - redirect all requests to HTTPS
server {
    server_name имя_домена www.имя_домена;

    listen ip-адрес_сервера:80;
    if ($host = 'www.имя_домена') {
        return 301 https://имя_домена$request_uri;
    }

    return 301 https://имя_домена$request_uri;
}

server {
    server_name имя_домена www.имя_домена;

    location / {
      include '/etc/nginx/proxy_params';
      proxy_pass http://127.0.0.1:8080/;
    }

    location /media/ {
        alias /opt/star-burger/media/;
    }

    location /static/ {
        alias /opt/star-burger/staticfiles/;
    }

    if ($host = 'www.имя_домена') {
        return 301 https://имя_домена$request_uri;
    }


    listen ip-адрес_сервера:443 ssl;
    ssl_certificate /etc/letsencrypt/live/testoftest.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/testoftest.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```
Выход из редактора: Escape, `:w`, Enter, `:q`, Enter

Перезапустить сервер Nginx:
```sh
systemctl restart nginx
```


### 3. Далее инициализируем для работы БД
(подставляемые переменные ниже будут задействованы для работы сайта):
```sh
CREATE DATABASE имя_базы_данных;
CREATE USER имя_пользователя_БД WITH PASSWORD пароль_пользователя_БД;
ALTER ROLE имя_пользователя_БД SET client_encoding TO 'utf8';
ALTER ROLE имя_пользователя_БД SET default_transaction_isolation TO 'read committed';
ALTER ROLE имя_пользователя_БД SET timezone TO 'Europe/Moscow';
GRANT ALL PRIVILEGES ON DATABASE имя_базы_данных TO имя_пользователя_БД;
```

`\q` - выйти из PostgreSQL

### 4. Для запуска сайта нужно запустить **одновременно** бэкенд и фронтенд, в двух разных терминалах.

### Собрать бэкенд

Перейдите в папку будущего расположения проекта и скачайте код:
```sh
git clone https://github.com/devmanorg/star-burger.git
```
Здесь и далее, если получаете отказ исполнения команды типа `permission denided`, используйте перед командой
префикс `sudo`.

Перейдите в каталог проекта:
```sh
cd star-burger
```

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Определите переменные окружения. Создайте файл `.env` в каталоге `star_burger/` и положите туда такой код:

- `SECRET_KEY=django-insecure-0if40nf4nf93n4`
- `DEBUG=...  — дебаг-режим. Поставьте `True`, чтобы увидеть отладочную информацию в случае ошибки. Выключается значением `False`.
- `ALLOWED_HOSTS=`... — по умолчанию: localhost, 127.0.0.1. [документация Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `YANDEX_API_KEY=`... - получить ключ от сервиса Яндекс [Yandex geocoder API](https://developer.tech.yandex.ru/services).
- `DATABASE_URL=`'postgres://`user`:`pass`@localhost/`dbname`', где:
  - user - имя пользователя БД;
  - pass - пароль пользователя БД;
  - dbname - имя базы данных, введенные ранее на этапе создания БД.


### Собрать фронтенд

**Откройте новый терминал**. Для работы сайта в dev-режиме необходима одновременная работа сразу двух программ `gunicorn` и `parcel`. Каждая требует себе отдельного терминала. Чтобы не выключать `gunicorn` откройте для фронтенда новый терминал и все нижеследующие инструкции выполняйте там.

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что Node.js и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```sh
nodejs --version
# v16.16.0
# Если ошибка, попробуйте node:
node --version
# v16.16.0

npm --version
# 8.11.0
```

Версия `nodejs` должна быть не младше `10.0` и не старше `16.16`. Лучше ставьте `16.16.0`, её мы тестировали. Версия `npm` не важна. Как обновить Node.js читайте в статье: [How to Update Node.js](https://phoenixnap.com/kb/update-node-js-version).


### Далее запустите скрипт деплоя проекта, который выполнит цикл действий по установке проекта:
```sh
chmod +x deploy_star_burger.sh
./deploy_star_burger.sh
```
Этот скрипт используется и после обновления кода на github.

### Запустите фронтенд:


Во втором окне, где устанавливался Node JS, перейдите в виртуальное окружение:
```sh
source venv/bin/activate
```
Далее запустите сборку фронтенда и не выключайте. Parcel будет работать в фоне и следить за изменениями в JS-коде:
```sh
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Если вы на Windows, то вам нужна та же команда, только с другими слешами в путях:
```sh
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Дождитесь завершения первичной сборки. Это вполне может занять 10 и более секунд. О готовности вы узнаете по сообщению в консоли:
```
✨  Built in 10.89s
```

Parcel будет следить за файлами в каталоге `bundles-src`. Сначала он прочитает содержимое `index.js` и узнает какие другие файлы он импортирует. Затем Parcel перейдёт в каждый из этих подключенных файлов и узнает что импортируют они. И так далее, пока не закончатся файлы. В итоге Parcel получит полный список зависимостей. Дальше он соберёт все эти сотни мелких файлов в большие бандлы `bundles/index.js` и `bundles/index.css`. Они полностью самодостаточно и потому пригодны для запуска в браузере. Именно эти бандлы сервер отправит клиенту.


### Запустите бэкенд:
В первом окне, где устанавливался Python, перейдите в виртуальное окружение:
```sh
source venv/bin/activate
```
Далее:
```sh
gunicorn -b ip-адрес_сервера:8080 --workers 3 star_burger.wsgi:application
```

Откройте сайт в браузере по адресу [ip-адрес_сервера](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу или некорректное изображение сайта, значит имеются проблемы в работе фронтенда. Проверьте правильность своих действий и трэйсбэки.


При успешной установке, если зайти на страницу  [http://127.0.0.1:8000/](http://127.0.0.1:8000/), то вместо пустой страницы вы увидите:

![](https://dvmn.org/filer/canonical/1594651900/687/)

Каталог `bundles` в репозитории особенный — туда Parcel складывает результаты своей работы. Эта директория предназначена исключительно для результатов сборки фронтенда и потому исключёна из репозитория с помощью `.gitignore`.

**Сбросьте кэш браузера <kbd>Ctrl-F5</kbd>.** Браузер при любой возможности старается кэшировать файлы статики: CSS, картинки и js-код. Порой это приводит к странному поведению сайта, когда код уже давно изменился, но браузер этого не замечает и продолжает использовать старую закэшированную версию. В норме Parcel решает эту проблему самостоятельно. Он следит за пересборкой фронтенда и предупреждает JS-код в браузере о необходимости подтянуть свежий код. Но если вдруг что-то у вас идёт не так, то начните ремонт со сброса браузерного кэша, жмите <kbd>Ctrl-F5</kbd>.


## Как запустить prod-версию сайта

Проделайте все вышеуказанные действия для запуска dev-версии сайта, за исключением:
- запуска фронтенда. Используйте команду:
```sh
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

- в файле `.env` в каталоге `star_burger/` измените следующие настройки:

- `DEBUG=` — дебаг-режим. Поставьте `False`.
- `SECRET_KEY=` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте.
   Получить секретный ключ Django:
```shell
python
>>> from django.core.management.utils import get_random_secret_key
>>> get_random_secret_key()
```
- `ALLOWED_HOSTS=` — необходимо внести через запятую IP-адреса или домены своего сервера. [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)
- `ROLLBAR_ACCESS_TOKEN=`... - зарегистрировать проект и взять ключ POST_SERVER_ITEM_ACCESS_TOKEN в разделе `Settings - Project Access Tokens`
- `ROLLBAR_ENVIRONMENT=production`


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
