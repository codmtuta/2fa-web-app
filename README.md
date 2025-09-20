# Генератор случайных чисел и паролей

Простая и удобная библиотека для генерации случайных целых чисел с заданным количеством цифр и безопасных паролей.

## Возможности

### Генерация случайных чисел
- ✅ Генерация случайного числа с точным количеством цифр
- ✅ Генерация нескольких чисел одновременно
- ✅ Генерация числа с количеством цифр в заданном диапазоне

### Генерация паролей
- ✅ Генерация паролей с настраиваемой длиной
- ✅ Выбор типов символов (заглавные, строчные буквы, цифры, символы)
- ✅ Предустановленные режимы (простой, безопасный)
- ✅ Генерация нескольких паролей одновременно


### Общие возможности
- ✅ Обработка ошибок и валидация входных данных
- ✅ Подробная документация и примеры использования
- ✅ Полное покрытие тестами

## Установка

Просто скопируйте файл `random_number_generator.py` в ваш проект.

## Использование

### Основные функции

#### `generate_random_number(digits: int) -> int`

Генерирует случайное целое число с заданным количеством цифр.

```python
from random_number_generator import generate_random_number

# Генерация числа с 3 цифрами (от 100 до 999)
number = generate_random_number(3)
print(number)  # Например: 456
```

#### `generate_multiple_random_numbers(digits: int, count: int) -> list[int]`

Генерирует несколько случайных чисел с заданным количеством цифр.

```python
from random_number_generator import generate_multiple_random_numbers

# Генерация 5 чисел с 4 цифрами
numbers = generate_multiple_random_numbers(4, 5)
print(numbers)  # Например: [1234, 5678, 9012, 3456, 7890]
```

#### `generate_random_number_with_range(min_digits: int, max_digits: int) -> int`

Генерирует случайное число с количеством цифр в заданном диапазоне.

```python
from random_number_generator import generate_random_number_with_range

# Генерация числа с количеством цифр от 2 до 5
number = generate_random_number_with_range(2, 5)
print(number)  # Например: 1234 (4 цифры)
```

### Примеры практического применения

#### Генерация PIN-кодов

```python
# Генерация 4-значных PIN-кодов
pin_codes = generate_multiple_random_numbers(4, 10)
for i, pin in enumerate(pin_codes, 1):
    print(f"PIN {i}: {pin}")
```

#### Генерация номеров телефонов

```python
# Генерация последних 7 цифр номера телефона
phone_suffix = generate_random_number(7)
print(f"+7-XXX-{phone_suffix}")
```

#### Генерация кодов подтверждения

```python
# Генерация 6-значного кода подтверждения
confirmation_code = generate_random_number(6)
print(f"Ваш код подтверждения: {confirmation_code}")
```

## Генерация паролей

### Основные функции

#### `generate_password(length: int, **options) -> str`

Генерирует пароль с настраиваемыми параметрами.

```python
from random_number_generator import generate_password

# Базовый пароль (все типы символов)
password = generate_password(12)
print(password)  # Например: "Kj8#mN2$pL9@"

# Пароль только из букв и цифр
password = generate_password(10, include_symbols=False)
print(password)  # Например: "mK9nL2pQ8r"

# Пароль только из цифр
password = generate_password(6, include_uppercase=False, 
                           include_lowercase=False, include_symbols=False)
print(password)  # Например: "847392"
```

#### `generate_secure_password(length: int = 12) -> str`

Генерирует безопасный пароль с рекомендуемыми настройками.

```python
from random_number_generator import generate_secure_password

# Безопасный пароль по умолчанию (12 символов)
password = generate_secure_password()
print(password)  # Например: "Kj8#mN2$pL9@"

# Безопасный пароль заданной длины
password = generate_secure_password(16)
print(password)  # Например: "Kj8#mN2$pL9@vX7!"
```

#### `generate_simple_password(length: int = 8) -> str`

Генерирует простой пароль только из букв и цифр.

```python
from random_number_generator import generate_simple_password

# Простой пароль по умолчанию (8 символов)
password = generate_simple_password()
print(password)  # Например: "mK9nL2pQ"

# Простой пароль заданной длины
password = generate_simple_password(12)
print(password)  # Например: "mK9nL2pQ8rXv"
```

#### `generate_multiple_passwords(count: int, length: int, **options) -> list[str]`

Генерирует несколько паролей с одинаковыми параметрами.

```python
from random_number_generator import generate_multiple_passwords

# 5 паролей по 10 символов
passwords = generate_multiple_passwords(5, 10)
for i, pwd in enumerate(passwords, 1):
    print(f"Пароль {i}: {pwd}")

# 3 простых пароля по 8 символов
simple_passwords = generate_multiple_passwords(3, 8, include_symbols=False)
print(simple_passwords)
```

### Примеры практического применения

#### Генерация паролей для тестирования

```python
# Простые пароли для тестирования
test_passwords = generate_multiple_passwords(5, 8, include_symbols=False)
for i, pwd in enumerate(test_passwords, 1):
    print(f"Тестовый пароль {i}: {pwd}")
```

#### Генерация паролей для продакшена

```python
# Безопасные пароли для продакшена
prod_passwords = generate_multiple_passwords(3, 16)
for i, pwd in enumerate(prod_passwords, 1):
    print(f"Продакшен пароль {i}: {pwd}")
```

#### Генерация PIN-кодов

```python
# 4-значные PIN-коды
pin_codes = generate_multiple_passwords(5, 4, include_uppercase=False, 
                                       include_lowercase=False, include_symbols=False)
for i, pin in enumerate(pin_codes, 1):
    print(f"PIN {i}: {pin}")
```


## Обработка ошибок

Функции включают валидацию входных данных:

```python
try:
    # Это вызовет ValueError
    generate_random_number(0)
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    # Это вызовет ValueError
    generate_password(0)
except ValueError as e:
    print(f"Ошибка: {e}")

try:
    # Это вызовет ValueError
    generate_password(8, include_uppercase=False, include_lowercase=False, 
                     include_digits=False, include_symbols=False)
except ValueError as e:
    print(f"Ошибка: {e}")

```

## Запуск примеров

```bash
# Запуск основного примера
python3 random_number_generator.py

# Запуск расширенных примеров
python3 example_usage.py

# Запуск демонстрации паролей
python3 password_demo.py

# Запуск тестов
python3 test_generator.py
```

## Требования

- Python 3.6+
- Модуль `random` (входит в стандартную библиотеку Python)

## Лицензия

Этот проект распространяется свободно для использования в любых целях.
