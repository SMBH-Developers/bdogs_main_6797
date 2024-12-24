import asyncio
import sqlite3
from datetime import datetime
from typing import Optional  # Исправлен импорт
from telethon import TelegramClient
from src.config import settings, client
import os

api_id = settings.api_id
api_hash = settings.api_hash
phone = settings.phone_number
directory = "data/sessions/"
session_path = directory + settings.name


def query_update(user_id: int, api_id: int):
    timestamp = int(datetime.now().timestamp())
    return f"""
    ALTER TABLE sessions ADD COLUMN api_id INTEGER;
    ALTER TABLE sessions ADD COLUMN test_mode INTEGER;
    ALTER TABLE sessions ADD COLUMN date INTEGER;
    ALTER TABLE sessions ADD COLUMN user_id INTEGER;
    ALTER TABLE sessions ADD COLUMN is_bot INTEGER;

    UPDATE sessions SET date = {timestamp};
    UPDATE sessions SET user_id = {user_id};
    UPDATE sessions SET is_bot = 0;
    UPDATE sessions SET test_mode = 0;
    UPDATE sessions SET api_id = {api_id};

    CREATE TABLE IF NOT EXISTS peers (
        id INTEGER PRIMARY KEY,
        access_hash INTEGER,
        type INTEGER NOT NULL,
        username TEXT,
        phone_number INTEGER,
        last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER))
    );
    INSERT INTO peers (id, access_hash, type, username, phone_number, last_update_on)
    SELECT id, hash, 'user', username, phone, date
    FROM entities;

    DROP TABLE IF EXISTS version;
    CREATE TABLE version (number INTEGER PRIMARY KEY);
    INSERT INTO version (number) VALUES (7);

    CREATE INDEX IF NOT EXISTS idx_peers_id ON peers (id);
    CREATE INDEX IF NOT EXISTS idx_peers_username ON peers (username);
    CREATE INDEX IF NOT EXISTS idx_peers_phone_number ON peers (phone_number);
    CREATE TRIGGER IF NOT EXISTS trg_peers_last_update_on
        AFTER UPDATE
        ON peers
    BEGIN
        UPDATE peers
        SET last_update_on = CAST(STRFTIME('%s', 'now') AS INTEGER)
        WHERE id = NEW.id;
    END;
    """


async def create_session() -> Optional["me"]:
    """Создание Telethon сессии"""
    result = None
    try:
        client_telethon = TelegramClient(session_path, api_id, api_hash)
        await client_telethon.start(phone=phone)  # type: ignore
        result = await client_telethon.get_me()
        await client_telethon.disconnect()
        print(f"Авторизован {result.username}")
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
    return result


async def convert_session_to_pyrogram(me: object) -> bool:
    """Подключение к базе данных SQLite"""
    result = True
    conn = None
    try:
        db_path = f"{session_path}.session"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Выполнение запроса
        query = query_update(me.id, api_id)
        cursor.executescript(query)
        conn.commit()
        print("Сессия перезаписана")
    except sqlite3.Error as e:
        result = False
        print(f"Ошибка выполнения SQL-запроса, при конвертации сессии: {e}")
    finally:
        if conn:
            conn.close()
    return result


async def insert_peer_id_to_session():
    """
    Необходимо чтобы сессия узнала все id чатов
        (Иначе работать не будет!!!)
    """
    try:
        print("Приступаем к перебору чатов...")
        app = client
        async with app:

            async for _ in app.get_dialogs():
                pass
        print("Перебор чатов выполнен!")
    except Exception as e:
        print(f"Проблема в переборе чатов: {e}")


def clear_session():
    """Получить список файлов в директории"""
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    if files:
        is_remove = input(f"Удалить старую сессию `{directory + files[0]}` (Y/N): ")
        if is_remove.lower() in ["y"]:
            for file in files:
                file_path = os.path.join(directory, file)
                try:
                    os.remove(file_path)
                    print(f"Удален файл: {file_path}")
                except Exception as e:
                    print(f"Не удалось удалить файл {file_path}: {e}")


async def main():
    clear_session()
    me_object = await create_session()
    if me_object:
        if await convert_session_to_pyrogram(me_object):
            await insert_peer_id_to_session()


if __name__ == "__main__":
    asyncio.run(main())
