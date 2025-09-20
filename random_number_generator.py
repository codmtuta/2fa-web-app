import random
import math
import string


def generate_random_number(digits: int) -> int:
    """
    Генерирует случайное целое число с заданным количеством цифр.
    
    Args:
        digits (int): Количество цифр в числе (должно быть больше 0)
    
    Returns:
        int: Случайное число с указанным количеством цифр
    
    Raises:
        ValueError: Если количество цифр меньше или равно 0
    """
    if digits <= 0:
        raise ValueError("Количество цифр должно быть больше 0")
    
    # Вычисляем минимальное и максимальное значение для заданного количества цифр
    min_value = 10 ** (digits - 1)  # Например, для 3 цифр: 100
    max_value = (10 ** digits) - 1  # Например, для 3 цифр: 999
    
    return random.randint(min_value, max_value)


def generate_multiple_random_numbers(digits: int, count: int) -> list[int]:
    """
    Генерирует несколько случайных чисел с заданным количеством цифр.
    
    Args:
        digits (int): Количество цифр в каждом числе
        count (int): Количество чисел для генерации
    
    Returns:
        list[int]: Список случайных чисел
    """
    if count <= 0:
        raise ValueError("Количество чисел должно быть больше 0")
    
    return [generate_random_number(digits) for _ in range(count)]


def generate_random_number_with_range(min_digits: int, max_digits: int) -> int:
    """
    Генерирует случайное число с количеством цифр в заданном диапазоне.
    
    Args:
        min_digits (int): Минимальное количество цифр
        max_digits (int): Максимальное количество цифр
    
    Returns:
        int: Случайное число с количеством цифр в заданном диапазоне
    """
    if min_digits <= 0 or max_digits <= 0:
        raise ValueError("Количество цифр должно быть больше 0")
    
    if min_digits > max_digits:
        raise ValueError("Минимальное количество цифр не может быть больше максимального")
    
    # Случайно выбираем количество цифр в заданном диапазоне
    random_digits = random.randint(min_digits, max_digits)
    
    return generate_random_number(random_digits)


def generate_password(length: int, include_uppercase: bool = True, include_lowercase: bool = True, 
                     include_digits: bool = True, include_symbols: bool = True) -> str:
    """
    Генерирует случайный пароль с заданными параметрами.
    
    Args:
        length (int): Длина пароля (должна быть больше 0)
        include_uppercase (bool): Включать ли заглавные буквы (A-Z)
        include_lowercase (bool): Включать ли строчные буквы (a-z)
        include_digits (bool): Включать ли цифры (0-9)
        include_symbols (bool): Включать ли специальные символы (!@#$%^&*)
    
    Returns:
        str: Сгенерированный пароль
    
    Raises:
        ValueError: Если длина пароля меньше или равна 0, или если не выбрано ни одного типа символов
    """
    if length <= 0:
        raise ValueError("Длина пароля должна быть больше 0")
    
    # Формируем набор символов для генерации
    charset = ""
    
    if include_uppercase:
        charset += string.ascii_uppercase
    if include_lowercase:
        charset += string.ascii_lowercase
    if include_digits:
        charset += string.digits
    if include_symbols:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not charset:
        raise ValueError("Необходимо выбрать хотя бы один тип символов для пароля")
    
    # Генерируем пароль
    password = ''.join(random.choice(charset) for _ in range(length))
    
    return password


def generate_secure_password(length: int = 12) -> str:
    """
    Генерирует безопасный пароль с рекомендуемыми настройками.
    
    Args:
        length (int): Длина пароля (по умолчанию 12)
    
    Returns:
        str: Безопасный пароль
    """
    return generate_password(
        length=length,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_symbols=True
    )


def generate_simple_password(length: int = 8) -> str:
    """
    Генерирует простой пароль только из букв и цифр.
    
    Args:
        length (int): Длина пароля (по умолчанию 8)
    
    Returns:
        str: Простой пароль
    """
    return generate_password(
        length=length,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_symbols=False
    )


def generate_multiple_passwords(count: int, length: int, **kwargs) -> list[str]:
    """
    Генерирует несколько паролей с одинаковыми параметрами.
    
    Args:
        count (int): Количество паролей для генерации
        length (int): Длина каждого пароля
        **kwargs: Дополнительные параметры для generate_password
    
    Returns:
        list[str]: Список сгенерированных паролей
    """
    if count <= 0:
        raise ValueError("Количество паролей должно быть больше 0")
    
    return [generate_password(length, **kwargs) for _ in range(count)]




# Примеры использования
if __name__ == "__main__":
    print("=== Генератор случайных чисел ===\n")
    
    # Пример 1: Генерация числа с 3 цифрами
    print("1. Число с 3 цифрами:")
    number = generate_random_number(3)
    print(f"   Результат: {number}")
    print(f"   Количество цифр: {len(str(number))}\n")
    
    # Пример 2: Генерация числа с 5 цифрами
    print("2. Число с 5 цифрами:")
    number = generate_random_number(5)
    print(f"   Результат: {number}")
    print(f"   Количество цифр: {len(str(number))}\n")
    
    # Пример 3: Генерация нескольких чисел
    print("3. 5 чисел с 4 цифрами:")
    numbers = generate_multiple_random_numbers(4, 5)
    for i, num in enumerate(numbers, 1):
        print(f"   {i}. {num}")
    print()
    
    # Пример 4: Генерация числа с переменным количеством цифр
    print("4. Число с количеством цифр от 2 до 6:")
    number = generate_random_number_with_range(2, 6)
    print(f"   Результат: {number}")
    print(f"   Количество цифр: {len(str(number))}\n")
    
    # Пример 5: Обработка ошибок
    print("5. Обработка ошибок:")
    try:
        generate_random_number(0)
    except ValueError as e:
        print(f"   Ошибка: {e}")
    
    try:
        generate_random_number(-1)
    except ValueError as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "="*50)
    print("=== Генератор паролей ===\n")
    
    # Пример 1: Простой пароль
    print("1. Простой пароль (8 символов):")
    password = generate_simple_password(8)
    print(f"   Результат: {password}")
    print(f"   Длина: {len(password)} символов\n")
    
    # Пример 2: Безопасный пароль
    print("2. Безопасный пароль (12 символов):")
    password = generate_secure_password(12)
    print(f"   Результат: {password}")
    print(f"   Длина: {len(password)} символов\n")
    
    # Пример 3: Пароль с настройками
    print("3. Пароль с настройками (10 символов, только буквы):")
    password = generate_password(10, include_uppercase=True, include_lowercase=True, 
                                include_digits=False, include_symbols=False)
    print(f"   Результат: {password}")
    print(f"   Длина: {len(password)} символов\n")
    
    # Пример 4: Несколько паролей
    print("4. 5 паролей по 6 символов:")
    passwords = generate_multiple_passwords(5, 6)
    for i, pwd in enumerate(passwords, 1):
        print(f"   {i}. {pwd}")
    print()
    
    # Пример 5: Пароли разной длины
    print("5. Пароли разной длины:")
    for length in [6, 8, 12, 16]:
        password = generate_secure_password(length)
        print(f"   {length} символов: {password}")
    print()
    
    # Пример 6: Обработка ошибок
    print("6. Обработка ошибок:")
    try:
        generate_password(0)
    except ValueError as e:
        print(f"   Ошибка (длина 0): {e}")
    
    try:
        generate_password(8, include_uppercase=False, include_lowercase=False, 
                         include_digits=False, include_symbols=False)
    except ValueError as e:
        print(f"   Ошибка (нет символов): {e}")
    
