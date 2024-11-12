# 🤖 Telegram UserBot для Управления Диалогами

## 🎯 Зачем этот проект?

Этот бот создан для автоматизации работы с клиентами в Telegram. Он помогает организовать диалоги по папкам, отслеживать активность пользователей и автоматически отправлять follow-up сообщения, если пользователь не отвечает.

## ✨ Основные возможности

- 📁 Автоматическая организация диалогов по папкам
- 🔄 Ротация пользователей между папками
- 📊 Сбор статистики по папкам и активности
- ⏰ Автоматические напоминания (пинги) неактивным пользователям
- ⚫️ Черный список для блокировки нежелательных карт
- 🗄 Интеграция с Redis для хранения состояний
- 📝 Подробное логирование всех действий
- 📊 Интеграция с Google Sheets для аналитики

## 🚀 Подготовка к запуску

### 1️⃣ Установка зависимостей

Клонируем репозиторий и устанавливаем зависимости:

```env
# Клонируем репозиторий
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Устанавливаем Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Устанавливаем зависимости через Poetry
poetry install --no-root
```

### 2️⃣ Настройка окружения

1. Создайте файл `.env` в корневой директории проекта:

```env
MODE=PROD or TEST
NAME=your_session_name
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
PHONE_NUMBER=your_phone_number
POSTGRES_DSN=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_HOST_NAME=localhost
REDIS_PORT=6380
REDIS_PASSWORD=your_password
```

2. Получите необходимые API ключи:
- Создайте приложение на [my.telegram.org](https://my.telegram.org) для получения `API_ID` и `API_HASH`
- Настройте доступ к Google Sheets API для аналитики

### 3️⃣ Настройка базы данных

```bash
alembic upgrade head
```

### 4️⃣ Запуск Redis

```bash
docker compose up -d
```

## 🚀 Запуск бота

```bash
poetry run python main.py
```


## 📝 Основные команды бота

- `/get_statistic` - Получить статистику по папкам
- `/get_statistic_new` - Получить статистику за сегодня
- `/update_managers XX` - Добавить новую папку (XX - две буквы)
- `/managers` - Настроить смены менеджеров
- `/black XXXX` - Добавить карту в черный список
- `/white XXXX` - Удалить карту из черного списка

## 🧪 Тестирование

```bash
poetry run pytest
```

## 📊 Логирование

Логи сохраняются в директории `data/logs/`. Основной лог-файл: `total.log`


## 👥 Деятели

- [Keni13-Coder](https://github.com/Keni13-Coder)
- [Egor Koromyslov](https://github.com/pyegork)
- [EvaDoubleI](https://github.com/EvaDoubleI)
- [KirillKorneevets](https://github.com/KirillKorneevets)

---

Сделано с ❤️ для автоматизации работы с клиентами в Telegram