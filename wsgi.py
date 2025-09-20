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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = False

# Для Render
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
