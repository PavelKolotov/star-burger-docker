# Сайт доставки еды Star Burger

Это сайт сети ресторанов [Star Burger](https://star-burger-docker.universal-web.online/). Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Необходимо установить [Docker](https://docs.docker.com/), для запуска на локальной машине [Docker Desktop](https://docs.docker.com/desktop/).

Клонируйте репозиторий:
```sh
git clone https://github.com/PavelKolotov/star-burger-docker.git
```

Перейдите в каталог проекта:
```sh
cd star-burger-docker
```

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

- `ROLLBAR_ACCESS_TOKEN` — ваш ключ от [Rollbar](https://rollbar.com/)
- `ROLLBAR_ENVIRONMENT` — настройка environment в Rollbar задаёт название окружения или инсталляции сайта.
- `YANDEX_GEOCODER_API_KEY`- в [кабинете разработчика](https://developer.tech.yandex.ru/) в API JavaScript API и HTTP Геокодер получите ключ.

Для сборки и запуска контейнеров используйте команду:
```sh
docker-compose up --build
```
Эта команда сначала соберет образы из Dockerfile и затем запустит контейнеры.

Если вы уже собрали образы и хотите просто запустить контейнеры, используйте:
```sh
docker-compose up
```
Это запустит все сервисы, определенные в файле docker-compose.yml


После запуска контейнера сайт будет досупен по адресу [http://localhost:8080](http://localhost:8080)

## Как запустить production-версию сайта

Необходимо установить [Docker](https://docs.docker.com/), для удалённых серверов следует использовать гайд по установке [Docker Engine](https://docs.docker.com/engine/install/).

Клонируйте репозиторий на сервер:
```sh
git clone https://github.com/PavelKolotov/star-burger-docker.git
```
Перейдите в каталог проекта:
```sh
cd star-burger-docker
```

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

- `DEBUG` — дебаг-режим. Поставьте `False`.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)
- `ROLLBAR_ACCESS_TOKEN` — ваш ключ от [Rollbar](https://rollbar.com/)
- `ROLLBAR_ENVIRONMENT` — настройка environment в Rollbar задаёт название окружения или инсталляции сайта.
- `DB_URL` - параметры подключения к БД в формате URL (postgres://<пользователь>:<пароль>@<хост>:<порт>/<имя_базы_данных>)
- `YANDEX_GEOCODER_API_KEY`- в [кабинете разработчика](https://developer.tech.yandex.ru/) в API JavaScript API и HTTP Геокодер получите ключ.


Перейдите в каталог проекта:
```sh
cd star-burger-docker/production
```

В файле production/docker-compose.yml замените:
nginx volumes: `- ../nginx/nginx.certbot.conf:/etc/nginx/conf.d/default.conf` на `- ../nginx/nginx.conf:/etc/nginx/conf.d/default.conf`
и ports: `- "8082:80"` на `- "80:80"`

Запустите сборку (если порт 80 занят, освободите его на время создания сертификатов SSL):
```sh
docker-compose up --build
```

Создайте SSL сертификаты запустив команду:

```sh
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d <ВАШ АДРЕС САЙТА> --agree-tos --email <ВАШ EMAIL>
```

После успешного создания сертификатов верните изменения в файле `production/docker-compose.yml` и перезапустите сборку:

```sh
docker-compose down
docker-compose up --build
```

## Обновление кода на сервере

Для обновления запустите из каталога с проектом bash скрипт:

```sh
./update_star_burger_docker.sh
```


После запуска контейнера сайт будет досупен по вашему адресу.


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).
