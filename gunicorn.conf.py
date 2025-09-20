#!/usr/bin/env python3
"""
Конфигурация Gunicorn для 2FA веб-приложения
"""

import os
import multiprocessing

# Базовые настройки
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Настройки логирования
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Настройки безопасности
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Настройки производительности
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Настройки для продакшена
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Настройки для разработки (если нужно)
if os.environ.get('FLASK_ENV') == 'development':
    workers = 1
    reload = True
    loglevel = 'debug'
