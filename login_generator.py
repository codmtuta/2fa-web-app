import json
import random
import os

class LoginGenerator:
    def __init__(self, json_file_path="logins_100000.json"):
        """
        Инициализация генератора логинов
        
        Args:
            json_file_path (str): Путь к файлу с логинами
        """
        self.json_file_path = json_file_path
        self.logins = []
        self.load_logins()
    
    def load_logins(self):
        """Загружает логины из JSON файла"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                self.logins = json.load(file)
            print(f"Загружено {len(self.logins)} логинов из файла {self.json_file_path}")
        except FileNotFoundError:
            print(f"Файл {self.json_file_path} не найден!")
            self.logins = []
        except json.JSONDecodeError:
            print(f"Ошибка при чтении JSON файла {self.json_file_path}")
            self.logins = []
    
    def generate_login(self):
        """
        Генерирует логин с добавлением случайных цифр в начале и конце
        
        Returns:
            str: Сгенерированный логин или None если нет доступных логинов
        """
        if not self.logins:
            print("Нет доступных логинов для генерации")
            return None
        
        # Выбираем случайный логин из списка
        base_login = random.choice(self.logins)
        
        # Генерируем случайное количество цифр для начала (1-2)
        prefix_digits = random.randint(1, 2)
        prefix = ''.join([str(random.randint(0, 9)) for _ in range(prefix_digits)])
        
        # Генерируем случайное количество цифр для конца (1-2)
        suffix_digits = random.randint(1, 2)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(suffix_digits)])
        
        # Собираем финальный логин
        generated_login = prefix + base_login + suffix
        
        return generated_login
    
    def generate_multiple_logins(self, count=1):
        """
        Генерирует несколько логинов
        
        Args:
            count (int): Количество логинов для генерации
            
        Returns:
            list: Список сгенерированных логинов
        """
        generated_logins = []
        for _ in range(count):
            login = self.generate_login()
            if login:
                generated_logins.append(login)
        return generated_logins
    
    def get_stats(self):
        """
        Возвращает статистику по загруженным логинам
        
        Returns:
            dict: Словарь со статистикой
        """
        if not self.logins:
            return {"total_logins": 0, "status": "Нет данных"}
        
        return {
            "total_logins": len(self.logins),
            "status": "Данные загружены",
            "sample_logins": self.logins[:5] if len(self.logins) >= 5 else self.logins
        }


# Функция для быстрого использования
def generate_login_from_file(json_file_path="logins_100000.json"):
    """
    Быстрая функция для генерации одного логина
    
    Args:
        json_file_path (str): Путь к файлу с логинами
        
    Returns:
        str: Сгенерированный логин
    """
    generator = LoginGenerator(json_file_path)
    return generator.generate_login()


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр генератора
    generator = LoginGenerator()
    
    # Показываем статистику
    stats = generator.get_stats()
    print("Статистика:", stats)
    print()
    
    # Генерируем несколько логинов для демонстрации
    print("Примеры сгенерированных логинов:")
    for i in range(10):
        login = generator.generate_login()
        print(f"{i+1}. {login}")
    
    print()
    print("Генерация 5 логинов сразу:")
    multiple_logins = generator.generate_multiple_logins(5)
    for i, login in enumerate(multiple_logins, 1):
        print(f"{i}. {login}")
