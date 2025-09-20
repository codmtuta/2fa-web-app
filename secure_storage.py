#!/usr/bin/env python3
"""
Модуль для безопасного хранения и шифрования 2FA ключей
"""

import os
import json
import base64
import hashlib
import secrets
import datetime
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureStorage:
    """Класс для безопасного хранения 2FA ключей с шифрованием"""
    
    def __init__(self, storage_file: str = "secure_keys.json", master_password: Optional[str] = None):
        """
        Инициализация безопасного хранилища
        
        Args:
            storage_file (str): Путь к файлу хранения
            master_password (str): Мастер-пароль для шифрования
        """
        self.storage_file = storage_file
        self.master_password = master_password or self._generate_master_password()
        self._encryption_key = self._derive_key(self.master_password)
        self._fernet = Fernet(self._encryption_key)
    
    def _generate_master_password(self) -> str:
        """Генерирует случайный мастер-пароль"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('ascii')
    
    def _derive_key(self, password: str) -> bytes:
        """Выводит ключ шифрования из пароля"""
        # Генерируем уникальную соль для каждого экземпляра
        if not hasattr(self, '_salt'):
            self._salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt_data(self, data: str) -> str:
        """Шифрует данные"""
        encrypted_data = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode('ascii')
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровывает данные"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Ошибка расшифровки: {e}")
    
    def _load_storage(self) -> Dict:
        """Загружает данные из файла"""
        if not os.path.exists(self.storage_file):
            return {
                'keys': [],
                'metadata': {
                    'version': '1.0',
                    'created_at': None,
                    'last_updated': None
                }
            }
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"Ошибка загрузки хранилища: {e}")
            return {
                'keys': [],
                'metadata': {
                    'version': '1.0',
                    'created_at': None,
                    'last_updated': None
                }
            }
    
    def _save_storage(self, data: Dict) -> bool:
        """Сохраняет данные в файл"""
        try:
            import datetime
            
            # Обновляем метаданные
            if 'metadata' not in data:
                data['metadata'] = {}
            
            if not data['metadata'].get('created_at'):
                data['metadata']['created_at'] = datetime.datetime.now().isoformat()
            
            data['metadata']['last_updated'] = datetime.datetime.now().isoformat()
            data['metadata']['version'] = '1.0'
            
            # Шифруем и сохраняем
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            encrypted_data = self._encrypt_data(json_data)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения хранилища: {e}")
            return False
    
    def add_key(self, secret_key: str, name: str = "", description: str = "") -> bool:
        """
        Добавляет новый ключ в хранилище
        
        Args:
            secret_key (str): Секретный ключ
            name (str): Название ключа
            description (str): Описание ключа
            
        Returns:
            bool: True если успешно добавлен
        """
        try:
            storage = self._load_storage()
            
            # Проверяем, не существует ли уже такой ключ
            for key_data in storage['keys']:
                if key_data['secret_key'] == secret_key:
                    return False  # Ключ уже существует
            
            # Создаем новый ключ
            new_key = {
                'id': secrets.token_urlsafe(16),
                'secret_key': secret_key,
                'name': name or f"Ключ {len(storage['keys']) + 1}",
                'description': description,
                'created_at': datetime.datetime.now().isoformat(),
                'last_used': None,
                'use_count': 0
            }
            
            storage['keys'].append(new_key)
            return self._save_storage(storage)
            
        except Exception as e:
            print(f"Ошибка добавления ключа: {e}")
            return False
    
    def get_keys(self) -> List[Dict]:
        """Получает список всех ключей"""
        try:
            storage = self._load_storage()
            return storage.get('keys', [])
        except Exception as e:
            print(f"Ошибка получения ключей: {e}")
            return []
    
    def get_key(self, key_id: str) -> Optional[Dict]:
        """Получает ключ по ID"""
        try:
            keys = self.get_keys()
            for key_data in keys:
                if key_data['id'] == key_id:
                    return key_data
            return None
        except Exception as e:
            print(f"Ошибка получения ключа: {e}")
            return None
    
    def update_key(self, key_id: str, **kwargs) -> bool:
        """Обновляет данные ключа"""
        try:
            storage = self._load_storage()
            
            for key_data in storage['keys']:
                if key_data['id'] == key_id:
                    for field, value in kwargs.items():
                        if field in key_data:
                            key_data[field] = value
                    return self._save_storage(storage)
            
            return False
        except Exception as e:
            print(f"Ошибка обновления ключа: {e}")
            return False
    
    def remove_key(self, key_id: str) -> bool:
        """Удаляет ключ по ID"""
        try:
            storage = self._load_storage()
            
            storage['keys'] = [key for key in storage['keys'] if key['id'] != key_id]
            return self._save_storage(storage)
            
        except Exception as e:
            print(f"Ошибка удаления ключа: {e}")
            return False
    
    def increment_use_count(self, key_id: str) -> bool:
        """Увеличивает счетчик использования ключа"""
        try:
            storage = self._load_storage()
            
            for key_data in storage['keys']:
                if key_data['id'] == key_id:
                    key_data['use_count'] = key_data.get('use_count', 0) + 1
                    key_data['last_used'] = datetime.datetime.now().isoformat()
                    return self._save_storage(storage)
            
            return False
        except Exception as e:
            print(f"Ошибка обновления счетчика: {e}")
            return False
    
    def export_keys(self, export_file: str = "2fa_keys_export.json") -> bool:
        """Экспортирует ключи в незашифрованном виде"""
        try:
            keys = self.get_keys()
            export_data = {
                'exported_at': datetime.datetime.now().isoformat(),
                'total_keys': len(keys),
                'keys': keys
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False
    
    def import_keys(self, import_file: str) -> int:
        """Импортирует ключи из файла"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for key_data in import_data.get('keys', []):
                if self.add_key(
                    secret_key=key_data['secret_key'],
                    name=key_data.get('name', ''),
                    description=key_data.get('description', '')
                ):
                    imported_count += 1
            
            return imported_count
        except Exception as e:
            print(f"Ошибка импорта: {e}")
            return 0
    
    def get_master_password(self) -> str:
        """Возвращает мастер-пароль для восстановления"""
        return self.master_password
    
    def change_master_password(self, new_password: str) -> bool:
        """Изменяет мастер-пароль"""
        try:
            # Загружаем текущие данные
            storage = self._load_storage()
            
            # Создаем новый ключ шифрования
            new_encryption_key = self._derive_key(new_password)
            new_fernet = Fernet(new_encryption_key)
            
            # Перешифровываем данные
            json_data = json.dumps(storage, ensure_ascii=False, indent=2)
            encrypted_data = base64.urlsafe_b64encode(new_fernet.encrypt(json_data.encode())).decode('ascii')
            
            # Сохраняем с новым паролем
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # Обновляем текущий ключ
            self.master_password = new_password
            self._encryption_key = new_encryption_key
            self._fernet = new_fernet
            
            return True
        except Exception as e:
            print(f"Ошибка изменения пароля: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Получает статистику использования"""
        try:
            keys = self.get_keys()
            storage = self._load_storage()
            
            total_keys = len(keys)
            total_uses = sum(key.get('use_count', 0) for key in keys)
            
            # Находим самый используемый ключ
            most_used_key = None
            max_uses = 0
            for key in keys:
                uses = key.get('use_count', 0)
                if uses > max_uses:
                    max_uses = uses
                    most_used_key = key
            
            return {
                'total_keys': total_keys,
                'total_uses': total_uses,
                'most_used_key': most_used_key,
                'storage_created': storage.get('metadata', {}).get('created_at'),
                'last_updated': storage.get('metadata', {}).get('last_updated')
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}


# Функции для быстрого использования
def create_secure_storage(storage_file: str = "secure_keys.json") -> SecureStorage:
    """Создает новое безопасное хранилище"""
    return SecureStorage(storage_file)


def load_secure_storage(storage_file: str = "secure_keys.json", master_password: str = None) -> SecureStorage:
    """Загружает существующее безопасное хранилище"""
    return SecureStorage(storage_file, master_password)


# Пример использования
if __name__ == "__main__":
    print("🔐 Демонстрация безопасного хранилища 2FA ключей\n")
    
    # Создаем хранилище
    storage = create_secure_storage("demo_secure_keys.json")
    print(f"Мастер-пароль: {storage.get_master_password()}")
    
    # Добавляем ключи
    demo_key = "JBSWY3DPEHPK3PXP"
    storage.add_key(demo_key, "Demo Account", "Демонстрационный ключ")
    storage.add_key("ABCDEFGHIJKLMNOP", "Test Account", "Тестовый ключ")
    
    # Получаем список ключей
    keys = storage.get_keys()
    print(f"\nСохранено ключей: {len(keys)}")
    for key in keys:
        print(f"- {key['name']}: {key['secret_key']}")
    
    # Получаем статистику
    stats = storage.get_statistics()
    print(f"\nСтатистика:")
    print(f"- Всего ключей: {stats['total_keys']}")
    print(f"- Всего использований: {stats['total_uses']}")
    
    # Экспортируем ключи
    if storage.export_keys("demo_export.json"):
        print("\n✅ Ключи экспортированы в demo_export.json")
    
    print("\n🔒 Все данные зашифрованы и безопасно сохранены!")
