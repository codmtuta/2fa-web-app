#!/usr/bin/env python3
"""
Скрипт для запуска 2FA веб-приложения в продакшене
"""

import os
import sys
from web_2fa_app import app

def main():
    """Запуск приложения в продакшене"""
    
    # Настройки для продакшена
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-secret-key')
    
    # Получаем порт из переменных окружения
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Запуск 2FA веб-приложения в продакшене...")
    print(f"Адрес: http://{host}:{port}")
    print(f"Режим: {'DEBUG' if app.config['DEBUG'] else 'PRODUCTION'}")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
