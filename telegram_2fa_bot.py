#!/usr/bin/env python3
"""
Телеграм бот для генерации 2FA кодов
Аналог BrowserScan 2FA для Telegram
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

from totp_generator import TOTPGenerator, HOTPGenerator, create_new_secret_key


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://twofa-web-app.onrender.com')
DEMO_KEY = "JBSWY3DPEHPK3PXP"  # Демонстрационный ключ с BrowserScan

# Хранилище пользовательских ключей (в продакшене использовать базу данных)
user_keys: Dict[int, List[Dict]] = {}


class Telegram2FABot:
    """Телеграм бот для генерации 2FA кодов"""
    
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("demo", self.demo_command))
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        self.application.add_handler(CommandHandler("add", self.add_key_command))
        self.application.add_handler(CommandHandler("list", self.list_keys_command))
        self.application.add_handler(CommandHandler("remove", self.remove_key_command))
        self.application.add_handler(CommandHandler("web", self.web_app_command))
        
        # Обработчики сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        welcome_text = f"""
🔐 <b>Добро пожаловать в 2FA Bot!</b>

Привет, {username}! Я помогу тебе генерировать коды двухфакторной аутентификации.

<b>Основные команды:</b>
• /demo - Демонстрация с тестовым ключом
• /add - Добавить новый секретный ключ
• /list - Показать сохраненные ключи
• /generate - Сгенерировать код для ключа
• /web - Открыть веб-версию
• /help - Справка

<b>Быстрый старт:</b>
1. Используй /demo для тестирования
2. Добавь свои ключи через /add
3. Генерируй коды через /generate

<b>Безопасность:</b>
🔒 Все ключи хранятся локально
🔒 Коды генерируются в реальном времени
🔒 Никакие данные не передаются третьим лицам
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Демо", callback_data="demo")],
            [InlineKeyboardButton("➕ Добавить ключ", callback_data="add_key")],
            [InlineKeyboardButton("🌐 Веб-версия", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 <b>Справка по 2FA Bot</b>

<b>🔧 Команды:</b>
• <code>/start</code> - Главное меню
• <code>/demo</code> - Демонстрация с тестовым ключом
• <code>/add &lt;ключ&gt;</code> - Добавить секретный ключ
• <code>/list</code> - Показать сохраненные ключи
• <code>/generate &lt;номер&gt;</code> - Сгенерировать код
• <code>/remove &lt;номер&gt;</code> - Удалить ключ
• <code>/web</code> - Открыть веб-версию

<b>📝 Примеры использования:</b>
• <code>/add JBSWY3DPEHPK3PXP</code> - добавить ключ
• <code>/generate 1</code> - сгенерировать код для первого ключа
• <code>/remove 2</code> - удалить второй ключ

<b>🔑 Формат ключей:</b>
Ключи должны быть в формате Base32 (например: JBSWY3DPEHPK3PXP)

<b>⏰ Время действия кодов:</b>
• TOTP коды действуют 30 секунд
• Коды обновляются автоматически

<b>🛡️ Безопасность:</b>
• Ключи хранятся только на твоем устройстве
• Никто не имеет доступа к твоим ключам
• Коды генерируются локально
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /demo"""
        try:
            # Создаем генератор с демонстрационным ключом
            totp = TOTPGenerator(DEMO_KEY)
            current_code = totp.generate_totp()
            remaining_time = totp.get_remaining_time()
            
            demo_text = f"""
🎯 <b>Демонстрация 2FA</b>

<b>Демонстрационный ключ:</b>
<code>{DEMO_KEY}</code>

<b>Текущий код:</b>
<code>{current_code}</code>

<b>⏰ Осталось времени:</b> {remaining_time} сек

<b>📱 Как использовать:</b>
1. Скопируй ключ выше
2. Добавь его в Google Authenticator
3. Сравни коды - они должны совпадать!

<b>🔄 Код обновляется каждые 30 секунд</b>
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data="demo_refresh")],
                [InlineKeyboardButton("➕ Добавить этот ключ", callback_data=f"add_demo_{DEMO_KEY}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(demo_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка демонстрации: {str(e)}")
    
    async def add_key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /add"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажи секретный ключ!\n\n"
                "Пример: <code>/add JBSWY3DPEHPK3PXP</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        secret_key = context.args[0].upper().strip()
        
        try:
            # Проверяем валидность ключа
            totp = TOTPGenerator(secret_key)
            test_code = totp.generate_totp()
            
            # Инициализируем список ключей пользователя если нужно
            if user_id not in user_keys:
                user_keys[user_id] = []
            
            # Проверяем, не добавлен ли уже этот ключ
            for key_data in user_keys[user_id]:
                if key_data['secret_key'] == secret_key:
                    await update.message.reply_text("⚠️ Этот ключ уже добавлен!")
                    return
            
            # Добавляем ключ
            key_data = {
                'secret_key': secret_key,
                'added_at': datetime.now().isoformat(),
                'name': f"Ключ {len(user_keys[user_id]) + 1}"
            }
            user_keys[user_id].append(key_data)
            
            success_text = f"""
✅ <b>Ключ успешно добавлен!</b>

<b>Секретный ключ:</b>
<code>{secret_key}</code>

<b>Тестовый код:</b>
<code>{test_code}</code>

<b>📋 Команды:</b>
• <code>/generate {len(user_keys[user_id])}</code> - сгенерировать код
• <code>/list</code> - показать все ключи
            """
            
            await update.message.reply_text(success_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Неверный формат ключа: {str(e)}")
    
    async def list_keys_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /list"""
        user_id = update.effective_user.id
        
        if user_id not in user_keys or not user_keys[user_id]:
            await update.message.reply_text(
                "📝 У тебя пока нет сохраненных ключей.\n\n"
                "Добавь первый ключ командой: <code>/add JBSWY3DPEHPK3PXP</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        list_text = "📋 <b>Твои сохраненные ключи:</b>\n\n"
        
        for i, key_data in enumerate(user_keys[user_id], 1):
            try:
                totp = TOTPGenerator(key_data['secret_key'])
                current_code = totp.generate_totp()
                remaining_time = totp.get_remaining_time()
                
                list_text += f"""
<b>{i}. {key_data['name']}</b>
🔑 <code>{key_data['secret_key']}</code>
🔢 <code>{current_code}</code> (⏰ {remaining_time}с)
📅 Добавлен: {datetime.fromisoformat(key_data['added_at']).strftime('%d.%m.%Y %H:%M')}

"""
            except Exception as e:
                list_text += f"❌ <b>{i}. {key_data['name']}</b> - Ошибка: {str(e)}\n\n"
        
        list_text += "\n<b>💡 Команды:</b>\n"
        list_text += "• <code>/generate &lt;номер&gt;</code> - сгенерировать код\n"
        list_text += "• <code>/remove &lt;номер&gt;</code> - удалить ключ"
        
        keyboard = []
        for i in range(0, len(user_keys[user_id]), 2):
            row = []
            for j in range(2):
                if i + j < len(user_keys[user_id]):
                    row.append(InlineKeyboardButton(
                        f"🔢 {i + j + 1}", 
                        callback_data=f"generate_{i + j + 1}"
                    ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(list_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /generate"""
        user_id = update.effective_user.id
        
        if user_id not in user_keys or not user_keys[user_id]:
            await update.message.reply_text(
                "❌ У тебя нет сохраненных ключей!\n\n"
                "Добавь ключ командой: <code>/add JBSWY3DPEHPK3PXP</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажи номер ключа!\n\n"
                "Пример: <code>/generate 1</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        try:
            key_index = int(context.args[0]) - 1
            
            if key_index < 0 or key_index >= len(user_keys[user_id]):
                await update.message.reply_text(f"❌ Неверный номер ключа! Доступны номера 1-{len(user_keys[user_id])}")
                return
            
            key_data = user_keys[user_id][key_index]
            totp = TOTPGenerator(key_data['secret_key'])
            current_code = totp.generate_totp()
            remaining_time = totp.get_remaining_time()
            
            generate_text = f"""
🔢 <b>2FA Код</b>

<b>Ключ:</b> {key_data['name']}
<b>Секретный ключ:</b> <code>{key_data['secret_key']}</code>

<b>Текущий код:</b>
<code>{current_code}</code>

<b>⏰ Осталось времени:</b> {remaining_time} секунд

<b>🔄 Код обновится через {remaining_time} секунд</b>
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{key_index + 1}")],
                [InlineKeyboardButton("🗑️ Удалить ключ", callback_data=f"remove_{key_index + 1}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(generate_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            
        except ValueError:
            await update.message.reply_text("❌ Номер ключа должен быть числом!")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка генерации: {str(e)}")
    
    async def remove_key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /remove"""
        user_id = update.effective_user.id
        
        if user_id not in user_keys or not user_keys[user_id]:
            await update.message.reply_text("❌ У тебя нет сохраненных ключей!")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажи номер ключа для удаления!\n\n"
                "Пример: <code>/remove 1</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        try:
            key_index = int(context.args[0]) - 1
            
            if key_index < 0 or key_index >= len(user_keys[user_id]):
                await update.message.reply_text(f"❌ Неверный номер ключа! Доступны номера 1-{len(user_keys[user_id])}")
                return
            
            removed_key = user_keys[user_id].pop(key_index)
            
            await update.message.reply_text(
                f"✅ Ключ <b>{removed_key['name']}</b> успешно удален!",
                parse_mode=ParseMode.HTML
            )
            
        except ValueError:
            await update.message.reply_text("❌ Номер ключа должен быть числом!")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка удаления: {str(e)}")
    
    async def web_app_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /web"""
        web_text = """
🌐 <b>Веб-версия 2FA Bot</b>

Открой веб-версию для удобного управления ключами и генерации кодов.

<b>Возможности веб-версии:</b>
• 📱 Адаптивный интерфейс
• 🔄 Автообновление кодов
• 📊 Визуальные индикаторы времени
• 🎨 Современный дизайн
        """
        
        keyboard = [
            [InlineKeyboardButton("🌐 Открыть веб-версию", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("📱 Вернуться в бот", callback_data="back_to_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(web_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.strip()
        
        # Проверяем, является ли сообщение секретным ключом
        if self.is_valid_secret_key(text):
            await self.auto_add_key(update, text)
        else:
            await update.message.reply_text(
                "❓ Не понимаю эту команду.\n\n"
                "Используй /help для получения справки или /start для главного меню."
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "demo":
            await self.demo_command(update, context)
        elif data == "demo_refresh":
            await self.demo_command(update, context)
        elif data == "add_key":
            await query.edit_message_text(
                "➕ <b>Добавление ключа</b>\n\n"
                "Отправь секретный ключ в формате Base32.\n\n"
                "Пример: <code>JBSWY3DPEHPK3PXP</code>",
                parse_mode=ParseMode.HTML
            )
        elif data.startswith("add_demo_"):
            secret_key = data.replace("add_demo_", "")
            context.args = [secret_key]
            await self.add_key_command(update, context)
        elif data.startswith("generate_"):
            key_num = int(data.replace("generate_", ""))
            context.args = [str(key_num)]
            await self.generate_command(update, context)
        elif data.startswith("refresh_"):
            key_num = int(data.replace("refresh_", ""))
            context.args = [str(key_num)]
            await self.generate_command(update, context)
        elif data.startswith("remove_"):
            key_num = int(data.replace("remove_", ""))
            context.args = [str(key_num)]
            await self.remove_key_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "back_to_bot":
            await self.start_command(update, context)
    
    def is_valid_secret_key(self, text: str) -> bool:
        """Проверяет, является ли текст валидным секретным ключом"""
        # Убираем пробелы и приводим к верхнему регистру
        text = text.upper().strip()
        
        # Проверяем длину (минимум 16 символов)
        if len(text) < 16:
            return False
        
        # Проверяем, что содержит только допустимые символы Base32
        if not re.match(r'^[A-Z2-7]+$', text):
            return False
        
        # Пытаемся создать TOTP генератор для проверки
        try:
            TOTPGenerator(text)
            return True
        except:
            return False
    
    async def auto_add_key(self, update: Update, secret_key: str):
        """Автоматически добавляет ключ, если сообщение похоже на секретный ключ"""
        user_id = update.effective_user.id
        
        # Инициализируем список ключей пользователя если нужно
        if user_id not in user_keys:
            user_keys[user_id] = []
        
        # Проверяем, не добавлен ли уже этот ключ
        for key_data in user_keys[user_id]:
            if key_data['secret_key'] == secret_key.upper():
                await update.message.reply_text("⚠️ Этот ключ уже добавлен!")
                return
        
        try:
            # Добавляем ключ
            key_data = {
                'secret_key': secret_key.upper(),
                'added_at': datetime.now().isoformat(),
                'name': f"Ключ {len(user_keys[user_id]) + 1}"
            }
            user_keys[user_id].append(key_data)
            
            totp = TOTPGenerator(secret_key.upper())
            current_code = totp.generate_totp()
            remaining_time = totp.get_remaining_time()
            
            success_text = f"""
✅ <b>Ключ автоматически добавлен!</b>

<b>Секретный ключ:</b>
<code>{secret_key.upper()}</code>

<b>Текущий код:</b>
<code>{current_code}</code>

<b>⏰ Осталось времени:</b> {remaining_time} сек

<b>📋 Команды:</b>
• <code>/generate {len(user_keys[user_id])}</code> - сгенерировать код
• <code>/list</code> - показать все ключи
            """
            
            await update.message.reply_text(success_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Неверный формат ключа: {str(e)}")
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск 2FA Telegram Bot...")
        self.application.run_polling()


def main():
    """Главная функция"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Ошибка: Не установлен TELEGRAM_BOT_TOKEN!")
        print("Установи переменную окружения или измени BOT_TOKEN в коде.")
        return
    
    bot = Telegram2FABot()
    bot.run()


if __name__ == "__main__":
    main()
