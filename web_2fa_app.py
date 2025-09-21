#!/usr/bin/env python3
"""
Веб-приложение для генерации 2FA кодов
Аналог BrowserScan 2FA
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS


from totp_generator import TOTPGenerator, create_new_secret_key
from login_generator import LoginGenerator

# Безопасный импорт secure_storage
try:
    from secure_storage import SecureStorage
    secure_storage = SecureStorage("secure_2fa_keys.json")
except ImportError as e:
    print(f"Warning: secure_storage not available: {e}")
    secure_storage = None
except Exception as e:
    print(f"Warning: secure_storage initialization failed: {e}")
    secure_storage = None


app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # Для сессий Flask

# Конфигурация
DEMO_KEY = "JBSWY3DPEHPK3PXP"
MAX_KEYS_PER_SESSION = 10

# Хранилище сессий (в продакшене использовать Redis или базу данных)
sessions: Dict[str, List[Dict]] = {}

# Генератор логинов
login_generator = LoginGenerator()


class Web2FAApp:
    """Веб-приложение для генерации 2FA кодов"""
    
    def __init__(self):
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка маршрутов"""
        app.route('/')(self.index)
        app.route('/2fa')(self.index)
        app.route('/api/generate', methods=['POST'])(self.api_generate)
        app.route('/api/validate', methods=['POST'])(self.api_validate)
        app.route('/api/add_key', methods=['POST'])(self.api_add_key)
        app.route('/api/remove_key', methods=['POST'])(self.api_remove_key)
        app.route('/api/get_keys', methods=['GET'])(self.api_get_keys)
        app.route('/api/demo', methods=['GET'])(self.api_demo)
        app.route('/api/generate_login', methods=['GET'])(self.api_generate_login)
        
        # Multiple keys support (BrowserScan style)
        app.route('/api/generate_multiple', methods=['POST'])(self.api_generate_multiple)
        
        # app.route('/api/secure_add_key', methods=['POST'])(self.api_secure_add_key)
        # app.route('/api/secure_get_keys', methods=['GET'])(self.api_secure_get_keys)
        # app.route('/api/secure_remove_key', methods=['POST'])(self.api_secure_remove_key)
        # app.route('/api/export_keys', methods=['GET'])(self.api_export_keys)
        # app.route('/api/import_keys', methods=['POST'])(self.api_import_keys)
        # app.route('/api/statistics', methods=['GET'])(self.api_statistics)
    
    def index(self):
        """Главная страница с поддержкой URL параметров"""
        # Получаем ключ из URL параметров
        key_from_url = request.args.get('key', '')
        return render_template('2fa_web.html', initial_key=key_from_url)
    
    def api_generate(self):
        """API для генерации 2FA кода"""
        try:
            data = request.get_json()
            secret_key = data.get('secret_key', '').upper().strip()
            session_id = data.get('session_id', 'default')
            
            if not secret_key:
                return jsonify({'error': 'Секретный ключ не указан'}), 400
            
            # Создаем генератор
            totp = TOTPGenerator(secret_key)
            current_code = totp.generate_totp()
            remaining_time = totp.get_remaining_time()
            
            # Сохраняем ключ в сессии
            self._add_key_to_session(session_id, secret_key)
            
            return jsonify({
                'success': True,
                'code': current_code,
                'remaining_time': remaining_time,
                'secret_key': secret_key,
                'timestamp': time.time()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_validate(self):
        """API для проверки 2FA кода"""
        try:
            data = request.get_json()
            secret_key = data.get('secret_key', '').upper().strip()
            code = data.get('code', '').strip()
            
            if not secret_key or not code:
                return jsonify({'error': 'Секретный ключ и код обязательны'}), 400
            
            # Создаем генератор и проверяем код
            totp = TOTPGenerator(secret_key)
            is_valid = totp.verify_totp(code)
            
            return jsonify({
                'success': True,
                'valid': is_valid,
                'message': 'Код верный' if is_valid else 'Код неверный'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_add_key(self):
        """API для добавления ключа в сессию"""
        try:
            data = request.get_json()
            secret_key = data.get('secret_key', '').upper().strip()
            session_id = data.get('session_id', 'default')
            name = data.get('name', '')
            
            if not secret_key:
                return jsonify({'error': 'Секретный ключ не указан'}), 400
            
            # Проверяем валидность ключа
            totp = TOTPGenerator(secret_key)
            test_code = totp.generate_totp()
            
            # Получаем текущие ключи для правильного подсчета
            current_keys = self._get_session_keys(session_id)
            
            # Добавляем ключ в сессию
            key_data = {
                'secret_key': secret_key,
                'name': name or f"Ключ {len(current_keys) + 1}",
                'added_at': datetime.now().isoformat()
            }
            
            # Проверяем, не добавлен ли уже этот ключ
            current_keys = self._get_session_keys(session_id)
            existing_keys = {key['secret_key'] for key in current_keys}
            if secret_key in existing_keys:
                return jsonify({
                    'success': False,
                    'error': 'Этот ключ уже добавлен в сессию'
                }), 400
            
            self._add_key_to_session(session_id, secret_key, key_data)
            
            return jsonify({
                'success': True,
                'message': 'Ключ успешно добавлен',
                'test_code': test_code,
                'key_data': key_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_remove_key(self):
        """API для удаления ключа из сессии"""
        try:
            data = request.get_json()
            secret_key = data.get('secret_key', '').upper().strip()
            session_id = data.get('session_id', 'default')
            
            if not secret_key:
                return jsonify({'error': 'Секретный ключ не указан'}), 400
            
            # Удаляем ключ из сессии
            removed = self._remove_key_from_session(session_id, secret_key)
            
            if removed:
                return jsonify({
                    'success': True,
                    'message': 'Ключ успешно удален'
                })
            else:
                return jsonify({'error': 'Ключ не найден'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_get_keys(self):
        """API для получения всех ключей сессии"""
        try:
            session_id = request.args.get('session_id', 'default')
            keys = self._get_session_keys(session_id)
            
            # Добавляем текущие коды для каждого ключа
            result = []
            for key_data in keys:
                try:
                    totp = TOTPGenerator(key_data['secret_key'])
                    current_code = totp.generate_totp()
                    remaining_time = totp.get_remaining_time()
                    
                    result.append({
                        **key_data,
                        'current_code': current_code,
                        'remaining_time': remaining_time
                    })
                except Exception as e:
                    result.append({
                        **key_data,
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'keys': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_demo(self):
        """API для демонстрации"""
        try:
            totp = TOTPGenerator(DEMO_KEY)
            current_code = totp.generate_totp()
            remaining_time = totp.get_remaining_time()
            
            return jsonify({
                'success': True,
                'demo_key': DEMO_KEY,
                'current_code': current_code,
                'remaining_time': remaining_time,
                'qr_code_url': totp.get_qr_code_data('Demo Account', '2FA Demo')
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_generate_login(self):
        """API для генерации логина"""
        try:
            # Получаем параметры из запроса
            prefix = request.args.get('prefix', '')
            length = int(request.args.get('length', 8))
            
            # Валидация длины
            if length < 3 or length > 50:
                return jsonify({
                    'success': False,
                    'error': 'Длина логина должна быть от 3 до 50 символов'
                }), 400
            
            login = login_generator.generate_login(prefix=prefix, length=length)
            if login:
                return jsonify({
                    'success': True,
                    'login': login,
                    'prefix': prefix,
                    'length': length
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Не удалось сгенерировать логин'
                }), 400
                
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Неверный формат длины логина'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
    
    def api_secure_add_key(self):
        """API для безопасного добавления ключа"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            data = request.get_json()
            secret_key = data.get('secret_key', '').upper().strip()
            name = data.get('name', '')
            description = data.get('description', '')
            
            if not secret_key:
                return jsonify({'error': 'Секретный ключ не указан'}), 400
            
            # Проверяем валидность ключа
            totp = TOTPGenerator(secret_key)
            test_code = totp.generate_totp()
            
            # Добавляем в безопасное хранилище
            success = secure_storage.add_key(secret_key, name, description)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Ключ безопасно сохранен',
                    'test_code': test_code,
                    'master_password': secure_storage.get_master_password()
                })
            else:
                return jsonify({'error': 'Ключ уже существует или ошибка сохранения'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_secure_get_keys(self):
        """API для получения ключей из безопасного хранилища"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            keys = secure_storage.get_keys()
            
            # Добавляем текущие коды для каждого ключа
            result = []
            for key_data in keys:
                try:
                    totp = TOTPGenerator(key_data['secret_key'])
                    current_code = totp.generate_totp()
                    remaining_time = totp.get_remaining_time()
                    
                    result.append({
                        'id': key_data['id'],
                        'name': key_data['name'],
                        'description': key_data.get('description', ''),
                        'secret_key': key_data['secret_key'],
                        'current_code': current_code,
                        'remaining_time': remaining_time,
                        'created_at': key_data['created_at'],
                        'last_used': key_data.get('last_used'),
                        'use_count': key_data.get('use_count', 0)
                    })
                except Exception as e:
                    result.append({
                        'id': key_data['id'],
                        'name': key_data['name'],
                        'description': key_data.get('description', ''),
                        'secret_key': key_data['secret_key'],
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'keys': result,
                'total_count': len(result)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_secure_remove_key(self):
        """API для удаления ключа из безопасного хранилища"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            data = request.get_json()
            key_id = data.get('key_id', '')
            
            if not key_id:
                return jsonify({'error': 'ID ключа не указан'}), 400
            
            success = secure_storage.remove_key(key_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Ключ успешно удален'
                })
            else:
                return jsonify({'error': 'Ключ не найден'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_export_keys(self):
        """API для экспорта ключей"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            export_file = f"2fa_export_{int(time.time())}.json"
            success = secure_storage.export_keys(export_file)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Ключи экспортированы',
                    'export_file': export_file
                })
            else:
                return jsonify({'error': 'Ошибка экспорта'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_import_keys(self):
        """API для импорта ключей"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            if 'file' not in request.files:
                return jsonify({'error': 'Файл не загружен'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Файл не выбран'}), 400
            
            # Сохраняем временный файл
            temp_file = f"temp_import_{int(time.time())}.json"
            file.save(temp_file)
            
            # Импортируем ключи
            imported_count = secure_storage.import_keys(temp_file)
            
            # Удаляем временный файл
            os.remove(temp_file)
            
            return jsonify({
                'success': True,
                'message': f'Импортировано {imported_count} ключей',
                'imported_count': imported_count
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_statistics(self):
        """API для получения статистики"""
        try:
            if secure_storage is None:
                return jsonify({'error': 'Безопасное хранилище недоступно'}), 503
                
            stats = secure_storage.get_statistics()
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def _get_session_keys(self, session_id: str) -> List[Dict]:
        """Получает ключи для сессии"""
        if session_id not in sessions:
            sessions[session_id] = []
        return sessions[session_id]
    
    def _add_key_to_session(self, session_id: str, secret_key: str, key_data: Optional[Dict] = None):
        """Добавляет ключ в сессию с оптимизированной проверкой"""
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Используем set для быстрой проверки существования ключа
        existing_keys = {key['secret_key'] for key in sessions[session_id]}
        if secret_key in existing_keys:
            return  # Ключ уже существует
        
        # Ограничиваем количество ключей
        if len(sessions[session_id]) >= MAX_KEYS_PER_SESSION:
            sessions[session_id].pop(0)  # Удаляем самый старый ключ
        
        if key_data is None:
            # Получаем текущее количество ключей для правильного номера
            current_count = len(sessions[session_id])
            key_data = {
                'secret_key': secret_key,
                'name': f"Ключ {current_count + 1}",
                'added_at': datetime.now().isoformat()
            }
        
        sessions[session_id].append(key_data)
    
    def _remove_key_from_session(self, session_id: str, secret_key: str) -> bool:
        """Удаляет ключ из сессии"""
        if session_id not in sessions:
            return False
        
        for i, key_data in enumerate(sessions[session_id]):
            if key_data['secret_key'] == secret_key:
                sessions[session_id].pop(i)
                return True
        
        return False
    
    def api_get_auth_providers(self):
        """API для получения доступных провайдеров аутентификации"""
        try:
            providers = get_available_providers()
            return jsonify({
                'success': True,
                'providers': providers,
                'count': len(providers)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    def api_generate_multiple(self):
        """API для генерации кодов для множественных ключей (BrowserScan style)"""
        try:
            data = request.get_json()
            if not data or 'keys' not in data:
                return jsonify({'success': False, 'error': 'Keys required'}), 400
            
            keys_input = data['keys']
            if isinstance(keys_input, str):
                # Разделяем ключи по запятой
                keys = [key.strip() for key in keys_input.split(',') if key.strip()]
            else:
                keys = keys_input
            
            results = []
            for key in keys:
                try:
                    totp = TOTPGenerator(key)
                    code = totp.generate_totp()
                    remaining_time = totp.get_remaining_time()
                    
                    results.append({
                        'key': key,
                        'code': code,
                        'remaining_time': remaining_time,
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'key': key,
                        'error': str(e),
                        'success': False
                    })
            
            return jsonify({
                'success': True,
                'results': results,
                'count': len(results)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


# Создаем экземпляр приложения
web_app = Web2FAApp()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
