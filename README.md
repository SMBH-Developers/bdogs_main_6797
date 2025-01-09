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

### 1️⃣ Начальная настройка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. Создайте файл `.env` на основе `.env.example`:
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

3. Создание указанной базы данных

4 Созздание директории для сессии
```bash
mkdir -p data/sessions/
```

### 2️⃣ Запуск с помощью Docker

1. Соберите Docker образы:
```bash
make build
```

2. Запустите аутентификацию в Telegram:
```bash
make auth
```

3. Запустите все сервисы:
```bash
make up
```

4. Проведите миграции:
```bash
make migrate migrate_name
make migrate_up
```

### ⚙️ Дополнительные команды

- `make help` - вывод всех команд (та как в readme описаны не все команды)
- `make start` - умный запуск сервисов (проверяет наличие сессии и при необходимости запускает аутентификацию)
- `make down` - остановка и удаление контейнеров
- `make restart` - перезапуск контейнеров
- `make logs` - просмотр логов
- `make clean` - полная очистка (контейнеры и volumes)
- `make rebuild` - пересборка и перезапуск всех сервисов
- `make rebuild-app` - пересборка только приложения

### 🔍 Проверка работоспособности

1. Проверьте статус контейнеров:
```bash
docker ps
```

2. Должны быть запущены следующие сервисы:
- `redis_bot_app` (Redis)
- `bdocs_main_6797` (Основное приложение)

3. Проверьте логи:
```bash
make logs
```

## 📝 Основные команды бота

- `/get_statistic` - Получить статистику по папкам
- `/get_statistic_new` - Получить статистику за сегодня
- `/update_managers XX` - Добавить новую папку (XX - две буквы)
- `/managers` - Настроить смены менеджеров
- `/black XXXX` - Добавить карту в черный список
- `/white XXXX` - Удалить карту из черного списка


## 📊 Логирование

Логи сохраняются в директории `data/logs/`. Основной лог-файл: `total.log`


## 👥 Деятели

- [Keni13-Coder](https://github.com/Keni13-Coder)
- [Egor Koromyslov](https://github.com/pyegork)
- [EvaDoubleI](https://github.com/EvaDoubleI)
- [KirillKorneevets](https://github.com/KirillKorneevets)

---

Сделано с ❤️ для автоматизации работы с клиентами в Telegram