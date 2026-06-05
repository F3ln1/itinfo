# Деплой IT-INFO на VPS (Ubuntu + Nginx + Gunicorn + PostgreSQL)

## 1. Покупка VPS

| Провайдер     | Цена/мес       | Особенность              |
|---------------|----------------|--------------------------|
| VK Cloud      | ~300-700 руб   | Дата-центры в РФ         |
| Timeweb       | ~200-500 руб   | Да, есть в РФ            |
| Reg.ru        | ~200-400 руб   | Да, есть в РФ            |
| DigitalOcean  | $6             | Не в РФ, но удобно       |
| Hetzner       | ~4-6 евро      | Не в РФ, но дёшево       |

**Минимальные характеристики:**
- 1 vCPU, 1-2 ГБ RAM, 10-20 ГБ SSD
- Ubuntu 22.04 / 24.04

Покупаешь → тебе дают IP-адрес, root-пароль → подключаешься по SSH.

---

## 2. Подключение к серверу

```bash
ssh root@твой-ip-адрес
```

Первым делом:

```bash
apt update && apt upgrade -y
```

---

## 3. Установка PostgreSQL

```bash
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql
```

Создание БД и пользователя:

```bash
sudo -u postgres psql
```

Внутри psql:

```sql
CREATE DATABASE itinfo_db;
CREATE USER itinfo_user WITH PASSWORD 'твой_пароль';
GRANT ALL PRIVILEGES ON DATABASE itinfo_db TO itinfo_user;
\q
```

---

## 4. Установка Python и зависимостей

```bash
apt install python3 python3-pip python3-venv nginx git -y
```

Клонируем проект:

```bash
mkdir -p /var/www
cd /var/www
git clone https://github.com/твой-логин/itinfo.git
cd itinfo
```

Настраиваем окружение:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

## 5. Настройка Django

Создай **.env** на сервере:

```bash
nano .env
```

```
SECRET_KEY=сгенерируй_новый
DEBUG=False
ALLOWED_HOSTS=твой-ip,твой-домен.ru
DB_NAME=itinfo_db
DB_USER=itinfo_user
DB_PASSWORD=твой_пароль
DB_HOST=localhost
DB_PORT=5432
```

Собираем статику и миграции:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 6. Настройка Gunicorn (systemd)

Создаём службу:

```bash
nano /etc/systemd/system/itinfo.service
```

Вставь:

```ini
[Unit]
Description=IT-INFO Django Application
After=network.target postgresql.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/itinfo
ExecStart=/var/www/itinfo/venv/bin/gunicorn itinfo.wsgi --workers 3 --bind unix:/var/www/itinfo/itinfo.sock
Restart=always
RestartSec=5
EnvironmentFile=/var/www/itinfo/.env

[Install]
WantedBy=multi-user.target
```

Запускаем:

```bash
systemctl daemon-reload
systemctl start itinfo
systemctl enable itinfo
systemctl status itinfo  # проверить, что запустилось
```

---

## 7. Настройка Nginx

```bash
nano /etc/nginx/sites-available/itinfo
```

```nginx
server {
    listen 80;
    server_name твой-ip-адрес твой-домен.ru;

    location /static/ {
        alias /var/www/itinfo/staticfiles/;
    }

    location /media/ {
        alias /var/www/itinfo/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/itinfo/itinfo.sock;
    }
}
```

Включаем сайт:

```bash
ln -s /etc/nginx/sites-available/itinfo /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # удалить дефолтный
nginx -t  # проверить конфиг
systemctl restart nginx
```

---

## 8. SSL-сертификат (HTTPS) — бесплатно

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d твой-домен.ru
```

Выбираем **2 — Redirect** (авто-редирект HTTP → HTTPS).

Сертификат обновляется автоматически (проверить: `certbot renew --dry-run`).

---

## 9. Итоговая схема работы

```
Пользователь
    │
    ▼ (HTTPS)
Nginx (порт 443 — SSL)
    │
    ├── /static/ → читает файлы с диска (быстро)
    ├── /media/  → читает изображения с диска
    │
    ▼ (через Unix-сокет)
Gunicorn (воркеры 3 шт.)
    │
    ▼ (через ORM)
PostgreSQL
```

---

## 10. Обновление сайта

```bash
cd /var/www/itinfo
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart itinfo
```

Можно автоматизировать — через GitHub Actions при каждом push в main.

---

## 11. Мониторинг (если сайт упадёт)

```bash
systemctl status itinfo      # статус Django
systemctl status nginx       # статус Nginx
journalctl -u itinfo -n 20   # последние 20 логов Django
```

Если Gunicorn упадёт — `systemctl` сам перезапустит его (Restart=always).

---

## Что выбрать: Railway или VPS?

|             | Railway               | VPS                     |
|-------------|----------------------|-------------------------|
| Время       | 15 минут             | 1-2 часа                |
| Сложность   | Просто               | Средняя                 |
| Гибкость    | Ограниченная         | Полный контроль         |
| Цена        | Бесплатно / $5       | от 200 руб              |
| РФ          | Может тормозить      | Да, дата-центры в РФ    |

Если сайт для диплома и не планируешь много пользователей — **Railway проще**.
Если хочешь научиться администрировать Linux и сайт будет жить долго — **VPS**.
