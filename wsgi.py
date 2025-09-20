#!/usr/bin/env python3
"""
WSGI файл для развертывания 2FA веб-приложения на хостинге
"""

import os
import sys

# Добавляем путь к проекту в sys.path
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Импортируем приложение
from web_2fa_app import app

# Настройки для продакшена
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['DEBUG'] = False

if __name__ == "__main__":
    app.run()
