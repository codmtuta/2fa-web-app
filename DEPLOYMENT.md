# Инструкция по развертыванию 2FA веб-приложения

## Обзор

Это веб-приложение для генерации 2FA кодов, аналог BrowserScan 2FA. Поддерживает TOTP (Time-based One-Time Password) алгоритм.

## Поддерживаемые платформы

- **Heroku** (рекомендуется для быстрого развертывания)
- **Railway**
- **Render**
- **DigitalOcean App Platform**
- **AWS Elastic Beanstalk**
- **Google Cloud Run**
- **VPS с Ubuntu/Debian**

## Быстрое развертывание на Heroku

### 1. Подготовка

```bash
# Установите Heroku CLI
# Скачайте с https://devcenter.heroku.com/articles/heroku-cli

# Войдите в аккаунт Heroku
heroku login

# Создайте новое приложение
heroku create your-2fa-app-name
```

### 2. Настройка переменных окружения

```bash
# Установите секретный ключ
heroku config:set SECRET_KEY="your-super-secret-key-here"

# Установите порт (обычно автоматически)
heroku config:set PORT=5000

# Установите режим продакшена
heroku config:set FLASK_ENV=production
```

### 3. Развертывание

```bash
# Добавьте файлы в git (если еще не сделано)
git init
git add .
git commit -m "Initial commit"

# Разверните на Heroku
git push heroku main
```

### 4. Открытие приложения

```bash
# Откройте приложение в браузере
heroku open
```

## Развертывание на Railway

### 1. Подготовка

```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в аккаунт
railway login
```

### 2. Развертывание

```bash
# Создайте новый проект
railway init

# Разверните
railway up
```

### 3. Настройка переменных

В панели Railway установите:
- `SECRET_KEY`: ваш секретный ключ
- `FLASK_ENV`: production
- `PORT`: 5000

## Развертывание на VPS (Ubuntu/Debian)

### 1. Подготовка сервера

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python 3.9+
sudo apt install python3 python3-pip python3-venv nginx -y

# Создайте пользователя для приложения
sudo adduser --system --group 2fa-app
sudo mkdir -p /opt/2fa-app
sudo chown 2fa-app:2fa-app /opt/2fa-app
```

### 2. Установка приложения

```bash
# Переключитесь на пользователя приложения
sudo su - 2fa-app

# Скопируйте файлы в /opt/2fa-app
# (используйте scp, git clone или другой способ)

# Создайте виртуальное окружение
cd /opt/2fa-app
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройка systemd сервиса

Создайте файл `/etc/systemd/system/2fa-app.service`:

```ini
[Unit]
Description=2FA Web Application
After=network.target

[Service]
User=2fa-app
Group=2fa-app
WorkingDirectory=/opt/2fa-app
Environment=PATH=/opt/2fa-app/venv/bin
Environment=FLASK_ENV=production
Environment=SECRET_KEY=your-secret-key-here
ExecStart=/opt/2fa-app/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервиса

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите и запустите сервис
sudo systemctl enable 2fa-app
sudo systemctl start 2fa-app

# Проверьте статус
sudo systemctl status 2fa-app
```

### 5. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/2fa-app`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Включите сайт
sudo ln -s /etc/nginx/sites-available/2fa-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Настройка SSL (Let's Encrypt)

```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получите сертификат
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## Переменные окружения

### Обязательные

- `SECRET_KEY`: Секретный ключ для Flask сессий
- `FLASK_ENV`: Режим работы (production/development)

### Опциональные

- `PORT`: Порт для запуска (по умолчанию 5000)
- `HOST`: Хост для привязки (по умолчанию 0.0.0.0)
- `CORS_ORIGINS`: Разрешенные домены для CORS
- `WEB_CONCURRENCY`: Количество воркеров Gunicorn
- `LOG_LEVEL`: Уровень логирования

## Мониторинг и логи

### Heroku

```bash
# Просмотр логов
heroku logs --tail

# Мониторинг
heroku ps:scale web=1
```

### VPS

```bash
# Логи systemd
sudo journalctl -u 2fa-app -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Безопасность

### Рекомендации

1. **Измените SECRET_KEY** - используйте случайную строку длиной не менее 32 символов
2. **Настройте HTTPS** - обязательно для продакшена
3. **Ограничьте CORS** - укажите только нужные домены
4. **Используйте файрвол** - настройте UFW или iptables
5. **Регулярно обновляйте** - следите за обновлениями зависимостей

### Пример безопасного SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Масштабирование

### Горизонтальное масштабирование

Для высоких нагрузок рассмотрите:

1. **Redis** для хранения сессий
2. **PostgreSQL/MySQL** для постоянного хранения ключей
3. **Load Balancer** (Nginx, HAProxy)
4. **Docker** для контейнеризации

### Пример с Redis

```bash
# Установите Redis
sudo apt install redis-server -y

# Добавьте в requirements.txt
echo "redis==5.0.1" >> requirements.txt
```

## Устранение неполадок

### Частые проблемы

1. **Порт занят**: Проверьте `sudo netstat -tlnp | grep :5000`
2. **Права доступа**: Убедитесь что пользователь имеет права на файлы
3. **Зависимости**: Проверьте `pip list` и `requirements.txt`
4. **Логи**: Проверьте логи сервиса и Nginx

### Команды для диагностики

```bash
# Проверка статуса сервиса
sudo systemctl status 2fa-app

# Проверка портов
sudo netstat -tlnp | grep :5000

# Проверка процессов
ps aux | grep gunicorn

# Тест подключения
curl http://localhost:5000/api/demo
```

## Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в правильности переменных окружения
3. Проверьте доступность портов
4. Убедитесь в корректности конфигурации веб-сервера

## Обновление

```bash
# Остановите сервис
sudo systemctl stop 2fa-app

# Обновите код
git pull origin main

# Установите новые зависимости
source venv/bin/activate
pip install -r requirements.txt

# Запустите сервис
sudo systemctl start 2fa-app
```
