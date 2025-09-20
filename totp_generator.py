#!/usr/bin/env python3
"""
Генератор TOTP (Time-based One-Time Password) кодов для 2FA аутентификации
Аналог Google Authenticator и других 2FA приложений
"""

import hmac
import hashlib
import time
import base64
import struct
from typing import Optional, List, Dict, Any
import secrets
import string
from functools import lru_cache


class TOTPGenerator:
    """Генератор TOTP кодов для двухфакторной аутентификации"""
    
    def __init__(self, secret_key: str = None, digits: int = 6, period: int = 30):
        """
        Инициализация генератора TOTP
        
        Args:
            secret_key (str): Секретный ключ в base32 формате
            digits (int): Количество цифр в коде (6 или 8)
            period (int): Период действия кода в секундах (обычно 30)
        """
        self.digits = digits
        self.period = period
        self.secret_key = secret_key or self.generate_secret_key()
        
        # Валидация параметров
        if digits not in [6, 8]:
            raise ValueError("Количество цифр должно быть 6 или 8")
        if period <= 0:
            raise ValueError("Период должен быть положительным числом")
    
    @staticmethod
    def generate_secret_key(length: int = 16) -> str:
        """
        Генерирует случайный секретный ключ в base32 формате
        
        Args:
            length (int): Длина ключа в байтах
            
        Returns:
            str: Секретный ключ в base32 формате
        """
        # Генерируем случайные байты
        random_bytes = secrets.token_bytes(length)
        # Кодируем в base32
        secret_key = base64.b32encode(random_bytes).decode('ascii')
        return secret_key
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _base32_decode_static(secret: str) -> bytes:
        """
        Декодирует base32 строку в байты (статический метод с кэшированием)
        
        Args:
            secret (str): Строка в base32 формате
            
        Returns:
            bytes: Декодированные байты
        """
        # Добавляем padding если необходимо
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        try:
            return base64.b32decode(secret.upper())
        except Exception as e:
            raise ValueError(f"Неверный формат секретного ключа: {e}")
    
    def _base32_decode(self, secret: str) -> bytes:
        """Декодирует base32 строку в байты - использует статический метод"""
        return self._base32_decode_static(secret)
    
    def _get_time_counter(self, timestamp: Optional[float] = None) -> int:
        """
        Получает счетчик времени для TOTP
        
        Args:
            timestamp (float): Временная метка (по умолчанию текущее время)
            
        Returns:
            int: Счетчик времени
        """
        if timestamp is None:
            timestamp = time.time()
        return int(timestamp // self.period)
    
    @staticmethod
    def _hmac_sha1_static(key: bytes, message: bytes) -> bytes:
        """
        Вычисляет HMAC-SHA1 (статический метод)
        
        Args:
            key (bytes): Ключ
            message (bytes): Сообщение
            
        Returns:
            bytes: HMAC-SHA1 хеш
        """
        return hmac.new(key, message, hashlib.sha1).digest()
    
    def _hmac_sha1(self, key: bytes, message: bytes) -> bytes:
        """Вычисляет HMAC-SHA1 - использует статический метод"""
        return self._hmac_sha1_static(key, message)
    
    @staticmethod
    def _dynamic_truncate_static(hmac_hash: bytes) -> int:
        """
        Динамическое усечение HMAC хеша согласно RFC 4226 (статический метод)
        
        Args:
            hmac_hash (bytes): HMAC хеш
            
        Returns:
            int: Усеченное значение
        """
        offset = hmac_hash[-1] & 0x0f
        binary = struct.unpack('>I', hmac_hash[offset:offset + 4])[0]
        binary &= 0x7fffffff
        return binary
    
    def _dynamic_truncate(self, hmac_hash: bytes) -> int:
        """Динамическое усечение HMAC хеша - использует статический метод"""
        return self._dynamic_truncate_static(hmac_hash)
    
    def generate_totp(self, timestamp: Optional[float] = None) -> str:
        """
        Генерирует TOTP код с улучшенной обработкой ошибок
        
        Args:
            timestamp (float): Временная метка (по умолчанию текущее время)
            
        Returns:
            str: TOTP код
            
        Raises:
            ValueError: При неверном формате ключа или параметрах
            RuntimeError: При ошибке генерации кода
        """
        try:
            # Декодируем секретный ключ
            key = self._base32_decode(self.secret_key)
            
            # Получаем счетчик времени
            counter = self._get_time_counter(timestamp)
            
            # Конвертируем счетчик в байты (8 байт, big-endian)
            counter_bytes = struct.pack('>Q', counter)
            
            # Вычисляем HMAC-SHA1
            hmac_hash = self._hmac_sha1(key, counter_bytes)
            
            # Динамическое усечение
            truncated = self._dynamic_truncate(hmac_hash)
            
            # Получаем код нужной длины
            code = truncated % (10 ** self.digits)
            
            # Форматируем код с ведущими нулями
            return f"{code:0{self.digits}d}"
            
        except ValueError as e:
            raise ValueError(f"Ошибка валидации при генерации TOTP: {e}")
        except Exception as e:
            raise RuntimeError(f"Неожиданная ошибка при генерации TOTP: {e}")
    
    def verify_totp(self, code: str, timestamp: Optional[float] = None, 
                   window: int = 1) -> bool:
        """
        Проверяет TOTP код
        
        Args:
            code (str): Код для проверки
            timestamp (float): Временная метка (по умолчанию текущее время)
            window (int): Окно допустимых временных сдвигов
            
        Returns:
            bool: True если код верный, False иначе
        """
        if timestamp is None:
            timestamp = time.time()
        
        current_counter = self._get_time_counter(timestamp)
        
        # Проверяем код в окне времени
        for i in range(-window, window + 1):
            test_counter = current_counter + i
            test_timestamp = test_counter * self.period
            expected_code = self.generate_totp(test_timestamp)
            
            if code == expected_code:
                return True
        
        return False
    
    def get_remaining_time(self, timestamp: Optional[float] = None) -> int:
        """
        Получает оставшееся время действия текущего кода
        
        Args:
            timestamp (float): Временная метка (по умолчанию текущее время)
            
        Returns:
            int: Оставшееся время в секундах
        """
        if timestamp is None:
            timestamp = time.time()
        
        return self.period - int(timestamp % self.period)
    
    def get_qr_code_data(self, account_name: str = "Account", 
                        issuer: str = "2FA Service") -> str:
        """
        Генерирует данные для QR кода в формате otpauth://
        
        Args:
            account_name (str): Имя аккаунта
            issuer (str): Название сервиса
            
        Returns:
            str: URL для QR кода
        """
        import urllib.parse
        
        params = {
            'secret': self.secret_key,
            'issuer': issuer,
            'algorithm': 'SHA1',
            'digits': str(self.digits),
            'period': str(self.period)
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"otpauth://totp/{account_name}?{query_string}"
        
        return url
    
    def get_info(self) -> Dict[str, Any]:
        """
        Получает информацию о генераторе
        
        Returns:
            dict: Информация о генераторе
        """
        current_code = self.generate_totp()
        remaining_time = self.get_remaining_time()
        
        return {
            'secret_key': self.secret_key,
            'current_code': current_code,
            'remaining_time': remaining_time,
            'digits': self.digits,
            'period': self.period,
            'qr_code_url': self.get_qr_code_data()
        }


class HOTPGenerator:
    """Генератор HOTP (HMAC-based One-Time Password) кодов"""
    
    def __init__(self, secret_key: str = None, digits: int = 6):
        """
        Инициализация генератора HOTP
        
        Args:
            secret_key (str): Секретный ключ в base32 формате
            digits (int): Количество цифр в коде (6 или 8)
        """
        self.digits = digits
        self.secret_key = secret_key or TOTPGenerator.generate_secret_key()
        
        if digits not in [6, 8]:
            raise ValueError("Количество цифр должно быть 6 или 8")
    
    def _base32_decode(self, secret: str) -> bytes:
        """Декодирует base32 строку в байты - использует общий метод"""
        return TOTPGenerator._base32_decode_static(secret)
    
    def _hmac_sha1(self, key: bytes, message: bytes) -> bytes:
        """Вычисляет HMAC-SHA1 - использует общий метод"""
        return TOTPGenerator._hmac_sha1_static(key, message)
    
    def _dynamic_truncate(self, hmac_hash: bytes) -> int:
        """Динамическое усечение HMAC хеша - использует общий метод"""
        return TOTPGenerator._dynamic_truncate_static(hmac_hash)
    
    def generate_hotp(self, counter: int) -> str:
        """
        Генерирует HOTP код для заданного счетчика
        
        Args:
            counter (int): Счетчик
            
        Returns:
            str: HOTP код
        """
        # Декодируем секретный ключ
        key = self._base32_decode(self.secret_key)
        
        # Конвертируем счетчик в байты (8 байт, big-endian)
        counter_bytes = struct.pack('>Q', counter)
        
        # Вычисляем HMAC-SHA1
        hmac_hash = self._hmac_sha1(key, counter_bytes)
        
        # Динамическое усечение
        truncated = self._dynamic_truncate(hmac_hash)
        
        # Получаем код нужной длины
        code = truncated % (10 ** self.digits)
        
        # Форматируем код с ведущими нулями
        return f"{code:0{self.digits}d}"
    
    def verify_hotp(self, code: str, counter: int, window: int = 5) -> bool:
        """
        Проверяет HOTP код
        
        Args:
            code (str): Код для проверки
            counter (int): Ожидаемый счетчик
            window (int): Окно допустимых счетчиков
            
        Returns:
            bool: True если код верный, False иначе
        """
        for i in range(window):
            test_counter = counter + i
            expected_code = self.generate_hotp(test_counter)
            
            if code == expected_code:
                return True
        
        return False


# Функции для быстрого использования
def generate_totp_code(secret_key: str, digits: int = 6) -> str:
    """
    Быстрая генерация TOTP кода
    
    Args:
        secret_key (str): Секретный ключ в base32 формате
        digits (int): Количество цифр в коде
        
    Returns:
        str: TOTP код
    """
    generator = TOTPGenerator(secret_key, digits)
    return generator.generate_totp()


def generate_hotp_code(secret_key: str, counter: int, digits: int = 6) -> str:
    """
    Быстрая генерация HOTP кода
    
    Args:
        secret_key (str): Секретный ключ в base32 формате
        counter (int): Счетчик
        digits (int): Количество цифр в коде
        
    Returns:
        str: HOTP код
    """
    generator = HOTPGenerator(secret_key, digits)
    return generator.generate_hotp(counter)


def create_new_secret_key(length: int = 16) -> str:
    """
    Создает новый секретный ключ
    
    Args:
        length (int): Длина ключа в байтах
        
    Returns:
        str: Новый секретный ключ в base32 формате
    """
    return TOTPGenerator.generate_secret_key(length)


# Пример использования
if __name__ == "__main__":
    print("🔐 Демонстрация TOTP генератора\n")
    
    # Создаем генератор с демонстрационным ключом
    demo_key = "JBSWY3DPEHPK3PXP"  # Демонстрационный ключ с сайта
    totp = TOTPGenerator(demo_key)
    
    print(f"Секретный ключ: {totp.secret_key}")
    print(f"Текущий код: {totp.generate_totp()}")
    print(f"Оставшееся время: {totp.get_remaining_time()} секунд")
    print(f"QR код URL: {totp.get_qr_code_data('Demo Account', '2FA Demo')}")
    
    print("\n" + "="*50)
    print("🔄 Демонстрация HOTP генератора\n")
    
    # Создаем HOTP генератор
    hotp = HOTPGenerator(demo_key)
    
    print("HOTP коды для разных счетчиков:")
    for counter in range(5):
        code = hotp.generate_hotp(counter)
        print(f"Счетчик {counter}: {code}")
    
    print("\n" + "="*50)
    print("🆕 Создание нового ключа\n")
    
    # Создаем новый ключ
    new_key = create_new_secret_key()
    print(f"Новый секретный ключ: {new_key}")
    
    # Создаем генератор с новым ключом
    new_totp = TOTPGenerator(new_key)
    print(f"Код с новым ключом: {new_totp.generate_totp()}")
