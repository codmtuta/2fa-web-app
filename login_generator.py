import random
import string

class LoginGenerator:
    def __init__(self):
        """
        Инициализация генератора логинов
        """
        # Базовые слова для генерации логинов
        self.base_words = [
            'user', 'admin', 'player', 'gamer', 'hacker', 'coder', 'dev', 'test',
            'demo', 'guest', 'member', 'vip', 'pro', 'master', 'king', 'queen',
            'ninja', 'warrior', 'hero', 'legend', 'star', 'moon', 'sun', 'fire',
            'ice', 'storm', 'thunder', 'lightning', 'shadow', 'ghost', 'spirit',
            'angel', 'demon', 'dragon', 'phoenix', 'wolf', 'tiger', 'lion', 'bear',
            'eagle', 'falcon', 'hawk', 'raven', 'fox', 'cat', 'dog', 'rabbit',
            'mouse', 'snake', 'spider', 'bee', 'butterfly', 'fish', 'shark',
            'whale', 'dolphin', 'octopus', 'crab', 'lobster', 'turtle', 'frog',
            'lizard', 'gecko', 'chameleon', 'iguana', 'python', 'cobra', 'viper',
            'rattlesnake', 'boa', 'anaconda', 'python', 'java', 'script', 'html',
            'css', 'react', 'vue', 'angular', 'node', 'express', 'django', 'flask',
            'fastapi', 'spring', 'laravel', 'symfony', 'rails', 'sinatra', 'gin',
            'echo', 'fiber', 'chi', 'gorilla', 'mux', 'iris', 'beego', 'revel'
        ]
    
    def generate_login(self, prefix="", length=8):
        """
        Генерирует случайный логин
        
        Args:
            prefix (str): Префикс для логина (необязательно)
            length (int): Длина логина (по умолчанию 8)
        
        Returns:
            str: Сгенерированный логин
        """
        try:
            # Выбираем случайное базовое слово
            base_word = random.choice(self.base_words)
            
            # Определяем длину случайной части
            remaining_length = max(3, length - len(prefix))
            
            # Генерируем случайную часть
            random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=remaining_length))
            
            # Собираем логин
            if prefix:
                login = prefix + random_part
            else:
                # Если нет префикса, используем базовое слово + случайную часть
                word_length = min(len(base_word), remaining_length - 2)
                random_length = remaining_length - word_length
                
                login = base_word[:word_length] + ''.join(random.choices(string.digits, k=random_length))
            
            # Обрезаем до нужной длины
            login = login[:length]
            
            return login
            
        except Exception as e:
            print(f"Ошибка при генерации логина: {e}")
            return None
    
    def generate_multiple_logins(self, count=1, prefix="", length=8):
        """
        Генерирует несколько логинов
        
        Args:
            count (int): Количество логинов для генерации
            prefix (str): Префикс для логинов (необязательно)
            length (int): Длина логинов (по умолчанию 8)
            
        Returns:
            list: Список сгенерированных логинов
        """
        generated_logins = []
        for _ in range(count):
            login = self.generate_login(prefix, length)
            if login:
                generated_logins.append(login)
        return generated_logins
    
    def get_stats(self):
        """
        Возвращает статистику по генератору логинов
        
        Returns:
            dict: Словарь со статистикой
        """
        return {
            "total_base_words": len(self.base_words),
            "status": "Генератор готов к работе",
            "sample_words": self.base_words[:10]
        }


# Функция для быстрого использования
def generate_login_quick(prefix="", length=8):
    """
    Быстрая функция для генерации одного логина
    
    Args:
        prefix (str): Префикс для логина (необязательно)
        length (int): Длина логина (по умолчанию 8)
        
    Returns:
        str: Сгенерированный логин
    """
    generator = LoginGenerator()
    return generator.generate_login(prefix, length)


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
    print("Генерация логинов с префиксом:")
    for i in range(5):
        login = generator.generate_login(prefix="user", length=10)
        print(f"{i+1}. {login}")
    
    print()
    print("Генерация 5 логинов сразу:")
    multiple_logins = generator.generate_multiple_logins(5)
    for i, login in enumerate(multiple_logins, 1):
        print(f"{i}. {login}")
