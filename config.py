#!/usr/bin/env python3
"""
Конфигурация для 2FA веб-приложения
"""

import os
from datetime import timedelta

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Настройки сессий
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Ограничения
    MAX_KEYS_PER_SESSION = 10
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Безопасность
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS настройки
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Демо ключ
    DEMO_KEY = "JBSWY3DPEHPK3PXP"

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Дополнительные настройки безопасности для продакшена
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
